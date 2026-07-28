import datetime
from datetime import date
from hashlib import sha256

from fastapi.testclient import TestClient
import pytest

from streak_api.main import create_app
from streak_core import StreakRepository, StreakService, default_streaks_dir, resolve_streaks_dir
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


def test_api_rejects_invalid_identifier_and_archives(client):
    assert client.get("/api/v1/streaks/../etc").status_code in (404, 400)
    client.post("/api/v1/streaks", json={"name": "Archive", "tick_type": "Daily"})
    assert client.delete("/api/v1/streaks/archive").status_code == 200


def test_dashboard_and_htmx_fragment_are_rendered_without_browser(client):
    client.post("/api/v1/streaks", json={"name": "Journal", "tick_type": "Daily"})
    page = client.get("/")
    assert page.status_code == 200
    assert "Journal" in page.text
    card = client.post("/ui/streaks/journal/tick")
    assert card.status_code == 200
    expected_dom_id = f"streak-{sha256(b'journal').hexdigest()[:16]}"
    assert f'id="{expected_dom_id}"' in card.text


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
