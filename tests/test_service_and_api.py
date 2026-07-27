from datetime import date

from fastapi.testclient import TestClient
import pytest

from streak_api.main import create_app
from streak_core import StreakRepository, StreakService
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


def test_service_rejects_duplicate_historical_tick(service):
    streak_id, _ = service.create_streak("Read")
    service.add_tick(streak_id, "2026-01-01")
    with pytest.raises(DuplicateTickError):
        service.add_tick(streak_id, "2026-01-01T20:00:00")


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


def test_archive_is_recoverable(service):
    streak_id, _ = service.create_streak("Archive me")
    service.archive_streak(streak_id)
    assert (service.repository.directory / "archive" / "streak-archive-me.txt").is_file()
    assert not service.repository.path_for(streak_id).exists()


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
    assert 'id="streak-journal"' in card.text
