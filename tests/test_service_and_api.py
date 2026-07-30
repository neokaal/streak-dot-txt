import datetime
from datetime import date
from hashlib import sha256
import json
from pathlib import Path
import re
import tomllib

from fastapi.testclient import TestClient
import pytest
from click.testing import CliRunner

from streak_api.main import create_app
from streakdottxt import streakdottxt
from streak_core import (
    StreakRepository,
    StreakService,
    __version__,
    default_streaks_dir,
    resolve_streaks_dir,
)
from streak_core.models import DailyTick, Streak
from streak_core.statistics import StreakStatsCalculator
from streak_core.services import DuplicateTickError


@pytest.fixture
def service(tmp_path):
    return StreakService(StreakRepository(tmp_path / "streaks"))


@pytest.fixture
def client(tmp_path):
    return TestClient(create_app(tmp_path / "streaks"))


def test_service_persists_and_calculates_stats(service):
    streak_id, created = service.create_streak("Morning Walk", description="Fresh air")
    assert streak_id == "morning-walk"
    assert created.metadata["description"] == "Fresh air"
    assert service.tick_today(streak_id) is True
    streak = service.get_streak(streak_id)
    assert streak.stats["ticked_days"] == 1
    assert streak.stats["current_streak"] == 1
    assert service.tick_today(streak_id) is False


def test_repository_uses_the_canonical_slug_for_punctuation_and_slashes(service):
    streak_id, streak = service.create_streak("Read / Reflect - Daily")
    assert streak_id == "read-reflect-daily"
    assert streak.name == "Read / Reflect - Daily"
    assert service.repository.path_for(streak_id).is_file()
    assert list(service.repository.directory.glob("streak-*.txt")) == [
        service.repository.path_for(streak_id)
    ]


@pytest.mark.parametrize(
    ("name", "tick_type", "description"),
    [
        ("---", "Daily", None),
        ("Read", "Monthly", None),
        ("Read", "Daily", "first line\nsecond line"),
    ],
)
def test_invalid_create_leaves_no_streak_file(service, name, tick_type, description):
    with pytest.raises(ValueError):
        service.create_streak(name, tick_type, description)
    assert list(service.repository.directory.glob("streak-*.txt")) == []


def test_service_rejects_duplicate_historical_tick(service):
    streak_id, _ = service.create_streak("Read")
    service.add_tick(streak_id, "2026-01-01")
    with pytest.raises(DuplicateTickError):
        service.add_tick(streak_id, "2026-01-01T20:00:00")


def test_weekly_mark_does_not_confuse_the_same_week_number_across_years():
    today = datetime.date.today()
    current_iso = today.isocalendar()
    previous_iso_year = current_iso.year - 1
    try:
        prior_year_week = datetime.date.fromisocalendar(
            previous_iso_year,
            current_iso.week,
            1,
        )
    except ValueError:
        prior_year_week = datetime.date.fromisocalendar(
            previous_iso_year - 1,
            current_iso.week,
            1,
        )

    streak = Streak("Weekly review", "Weekly")
    streak.ticks.append(DailyTick(prior_year_week.isoformat()))
    assert streak.mark_today() is True
    assert len(streak.ticks) == 2
    assert streak.is_current_period_ticked() is True


def test_weekly_stats_normalize_ticks_to_the_start_of_each_week():
    current_week = datetime.date.today() - datetime.timedelta(
        days=datetime.date.today().weekday()
    )
    streak = Streak("Weekly review", "Weekly")
    streak.ticks = [
        DailyTick((current_week - datetime.timedelta(days=12)).isoformat()),
        DailyTick((current_week - datetime.timedelta(days=7)).isoformat()),
        DailyTick(current_week.isoformat()),
    ]

    stats = StreakStatsCalculator.calculate_stats(streak)
    assert stats["total_days"] == 3
    assert stats["ticked_days"] == 3
    assert stats["current_streak"] == 3
    assert stats["longest_streak"] == 3


def test_stats_ignore_duplicate_and_future_ticks():
    today = datetime.date.today()
    streak = Streak("Read")
    streak.ticks = [
        DailyTick(today.isoformat()),
        DailyTick(f"{today.isoformat()}T20:00:00"),
        DailyTick((today + datetime.timedelta(days=1)).isoformat()),
    ]

    stats = StreakStatsCalculator.calculate_stats(streak)
    assert stats == {
        "total_days": 1,
        "ticked_days": 1,
        "unticked_days": 0,
        "current_streak": 1,
        "longest_streak": 1,
        "tick_average": 1,
    }


def test_tick_metadata_keeps_period_in_sync():
    streak = Streak("Review")
    streak.set_metadata("tick", "Weekly")
    assert streak.tick == "Weekly"
    assert streak.period == 7
    with pytest.raises(ValueError, match="Unsupported tick type"):
        streak.set_metadata("tick", "Monthly")


def test_repository_rejects_path_traversal(service):
    with pytest.raises(ValueError):
        service.get_streak("../private")


def test_repository_lists_legacy_safe_filename_ids(service):
    directory = service.repository.directory
    directory.mkdir(parents=True)
    (directory / "streak-Morning_Walk.txt").write_text("---\nname: Morning Walk\ntick: Daily\n---\n")
    assert service.repository.list_ids() == ["Morning_Walk"]
    assert service.get_streak("Morning_Walk").name == "Morning Walk"


def test_repository_lists_legacy_filename_ids_with_spaces(service):
    directory = service.repository.directory
    directory.mkdir(parents=True)
    (directory / "streak-Reading (evening).txt").write_text("---\nname: Reading\ntick: Daily\n---\n")
    assert service.get_streak("Reading (evening)").name == "Reading"


def test_repository_preserves_existing_order_and_appends_new_streaks(service):
    directory = service.repository.directory
    directory.mkdir(parents=True)
    for streak_id, name in (("bravo", "Bravo"), ("charlie", "Charlie")):
        (directory / f"streak-{streak_id}.txt").write_text(
            f"---\nname: {name}\ntick: Daily\n---\n"
        )

    assert service.repository.list_ids() == ["bravo", "charlie"]
    service.create_streak("Alpha")

    assert service.repository.list_ids() == ["bravo", "charlie", "alpha"]
    config = json.loads((directory / "streaks-config.json").read_text())
    assert config == {
        "version": 1,
        "order": ["bravo", "charlie", "alpha"],
    }

    (directory / "streak-delta.txt").write_text(
        "---\nname: Delta\ntick: Daily\n---\n"
    )
    assert service.repository.list_ids() == ["bravo", "charlie", "alpha", "delta"]

    service.tick_today("bravo")
    assert service.repository.list_ids() == ["bravo", "charlie", "alpha", "delta"]


def test_repository_removes_archived_streak_from_portable_order(service):
    first_id, _ = service.create_streak("First")
    second_id, _ = service.create_streak("Second")

    service.archive_streak(first_id)

    assert service.repository.list_ids() == [second_id]
    config = json.loads(service.repository.config_path.read_text())
    assert config["order"] == [second_id]


def test_streak_directory_defaults_to_home_streaks_and_allows_explicit_override(tmp_path, monkeypatch):
    home = tmp_path / "home"
    monkeypatch.delenv("STREAKS_DIR", raising=False)
    assert default_streaks_dir(home) == home / "streaks"
    assert resolve_streaks_dir(tmp_path / "chosen") == tmp_path / "chosen"
    monkeypatch.setenv("STREAKS_DIR", str(tmp_path / "environment"))
    assert resolve_streaks_dir() == tmp_path / "environment"


def test_archive_is_recoverable(service):
    streak_id, _ = service.create_streak("Archive me")
    service.archive_streak(streak_id)
    assert (service.repository.directory / "archive" / "streak-archive-me.txt").is_file()
    assert not service.repository.path_for(streak_id).exists()


def test_archive_preserves_previous_streak_with_the_same_id(service):
    streak_id, _ = service.create_streak("Archive me")
    service.add_tick(streak_id, "2025-01-01")
    service.archive_streak(streak_id)

    recreated_id, _ = service.create_streak("Archive me")
    service.add_tick(recreated_id, "2026-01-01")
    service.archive_streak(recreated_id)

    archived = sorted((service.repository.directory / "archive").glob("*.txt"))
    assert [path.name for path in archived] == [
        "streak-archive-me.1.txt",
        "streak-archive-me.txt",
    ]
    assert "2025-01-01" in archived[1].read_text()
    assert "2026-01-01" in archived[0].read_text()


def test_unterminated_metadata_fails_fast_and_does_not_hide_valid_streaks(service, caplog):
    directory = service.repository.directory
    directory.mkdir(parents=True)
    (directory / "streak-broken.txt").write_text("---\nname: Broken\n")
    service.create_streak("Working")

    with pytest.raises(ValueError, match="Unterminated metadata"):
        service.get_streak("broken")

    listed = service.list_streaks()
    assert [streak_id for streak_id, _ in listed] == ["working"]
    assert "Skipping unreadable streak 'broken'" in caplog.text


def test_frontmatterless_file_keeps_its_first_tick(service):
    directory = service.repository.directory
    directory.mkdir(parents=True)
    (directory / "streak-legacy.txt").write_text("2026-01-01\n2026-01-02\n")

    streak = service.get_streak("legacy")
    assert [tick.tick_datetime_str for tick in streak.ticks] == [
        "2026-01-01",
        "2026-01-02",
    ]


def test_api_has_isolated_create_tick_list_flow(client):
    created = client.post("/api/v1/streaks", json={"name": "Practice", "tick_type": "Daily"})
    assert created.status_code == 201
    assert created.json()["id"] == "practice"
    ticked = client.post("/api/v1/streaks/practice/tick")
    assert ticked.json()["success"] is True
    listed = client.get("/api/v1/streaks")
    assert listed.status_code == 200
    assert listed.json()[0]["stats"]["current_streak"] == 1


@pytest.mark.parametrize(
    "payload",
    [
        {"name": "   "},
        {"name": "Read", "tick_type": "Monthly"},
        {"name": "Read", "description": "line one\nline two"},
    ],
)
def test_api_rejects_invalid_create_before_writing(client, payload):
    response = client.post("/api/v1/streaks", json=payload)
    assert response.status_code == 422
    assert client.app.state.service.repository.list_ids() == []


def test_api_rejects_invalid_identifier_and_archives(client):
    assert client.get("/api/v1/streaks/../etc").status_code in (404, 400)
    client.post("/api/v1/streaks", json={"name": "Archive", "tick_type": "Daily"})
    assert client.delete("/api/v1/streaks/archive").status_code == 200


def test_dashboard_and_htmx_fragment_are_rendered_without_browser(client):
    client.post("/api/v1/streaks", json={"name": "Journal", "tick_type": "Daily"})
    page = client.get("/")
    assert page.status_code == 200
    assert "Journal" in page.text
    assert 'src="/static/htmx.min.js"' in page.text
    assert "unpkg.com" not in page.text
    htmx = client.get("/static/htmx.min.js")
    assert htmx.status_code == 200
    assert len(htmx.content) > 50_000
    card = client.post("/ui/streaks/journal/tick")
    assert card.status_code == 200
    expected_dom_id = f"streak-{sha256(b'journal').hexdigest()[:16]}"
    assert f'id="{expected_dom_id}"' in card.text


def test_dashboard_renders_dense_switchboard_and_non_shifting_create_dialog(client):
    for index in range(25):
        client.app.state.service.create_streak(f"Practice {index + 1:02}")

    page = client.get("/")

    assert page.text.count('role="listitem"') == 25
    assert 'class="switchboard"' in page.text
    assert 'id="create-streak-dialog"' in page.text
    assert "<details" not in page.text
    assert page.text.index("Practice 01") < page.text.index("Practice 25")

    stylesheet = client.get("/static/app.css").text
    assert set(re.findall(r"#[0-9a-fA-F]{6}", stylesheet)) == {
        "#f5f6df",
        "#5a8f78",
        "#3a5068",
        "#372a51",
    }


def test_htmx_tick_returns_same_pressed_control_geometry(client):
    client.app.state.service.create_streak("Long practice name that must remain readable")
    before = client.get("/")
    expected_dom_id = f"streak-{sha256(b'long-practice-name-that-must-remain-readable').hexdigest()[:16]}"
    assert "Long practice name that must remain readable" in before.text
    assert 'aria-pressed="false"' in before.text

    control = client.post(
        "/ui/streaks/long-practice-name-that-must-remain-readable/tick"
    )

    assert f'id="{expected_dom_id}"' in control.text
    assert "streak-control is-done" in control.text
    assert 'aria-pressed="true"' in control.text
    assert "disabled" in control.text
    assert "✓ Done" in control.text


def test_weekly_card_stays_done_for_the_complete_current_week(client):
    created = client.post(
        "/api/v1/streaks",
        json={"name": "Weekly review", "tick_type": "Weekly"},
    )
    assert created.status_code == 201
    card = client.post("/ui/streaks/weekly-review/tick")
    assert card.status_code == 200
    assert "✓ Done" in card.text
    assert "is-done" in card.text


def test_foreign_origin_cannot_modify_local_streaks(client):
    response = client.post(
        "/api/v1/streaks",
        json={"name": "Injected"},
        headers={"Origin": "https://example.com"},
    )
    assert response.status_code == 403
    assert client.get("/api/v1/streaks").json() == []


def test_same_origin_can_modify_local_streaks(client):
    response = client.post(
        "/api/v1/streaks",
        json={"name": "Allowed"},
        headers={"Origin": "http://testserver"},
    )
    assert response.status_code == 201


def test_desktop_health_requires_the_current_sidecar_token(client, monkeypatch):
    monkeypatch.setenv("STREAK_INSTANCE_TOKEN", "expected-token")
    assert client.get("/desktop-health?token=wrong-token").status_code == 404
    response = client.get("/desktop-health?token=expected-token")
    assert response.status_code == 200
    assert response.text == "expected-token"


def test_legacy_identifier_is_encoded_for_url_and_safe_for_dom(client):
    directory = client.app.state.service.repository.directory
    directory.mkdir(parents=True)
    legacy_id = "Read #1?"
    (directory / f"streak-{legacy_id}.txt").write_text(
        "---\nname: Legacy\ntick: Daily\n---\n"
    )

    page = client.get("/")
    expected_dom_id = f"streak-{sha256(legacy_id.encode()).hexdigest()[:16]}"
    assert f'id="{expected_dom_id}"' in page.text
    assert "/ui/streaks/Read%20%231%3F/tick" in page.text
    assert f'hx-target="#{expected_dom_id}"' in page.text


def test_cli_create_mark_and_list_use_the_unified_service(tmp_path):
    streaks_directory = tmp_path / "cli-streaks"
    runner = CliRunner()

    created = runner.invoke(
        streakdottxt,
        ["--dir", str(streaks_directory), "new", "--name", "Read / Write"],
    )
    assert created.exit_code == 0, created.output
    assert (streaks_directory / "streak-read-write.txt").is_file()

    marked = runner.invoke(
        streakdottxt,
        ["--dir", str(streaks_directory), "mark", "--name", "read-write"],
    )
    assert marked.exit_code == 0, marked.output
    assert "Tick added" in marked.output

    listed = runner.invoke(
        streakdottxt,
        ["--dir", str(streaks_directory), "list"],
    )
    assert listed.exit_code == 0, listed.output
    assert "Read / Write" in listed.output
    assert "✓" in listed.output


def test_release_version_is_consistent_across_python_and_desktop_manifests():
    project_root = Path(__file__).resolve().parents[1]
    cargo = tomllib.loads(
        (project_root / "desktop/src-tauri/Cargo.toml").read_text()
    )
    tauri = json.loads(
        (project_root / "desktop/src-tauri/tauri.conf.json").read_text()
    )
    npm = json.loads((project_root / "desktop/package.json").read_text())
    npm_lock = json.loads(
        (project_root / "desktop/package-lock.json").read_text()
    )
    cargo_lock = (project_root / "desktop/src-tauri/Cargo.lock").read_text()
    cargo_lock_version = re.search(
        r'(?ms)\[\[package\]\]\nname = "streak-txt"\nversion = "([^"]+)"',
        cargo_lock,
    )

    assert cargo_lock_version is not None
    assert {
        __version__,
        cargo["package"]["version"],
        tauri["version"],
        npm["version"],
        npm_lock["version"],
        npm_lock["packages"][""]["version"],
        cargo_lock_version.group(1),
    } == {__version__}
