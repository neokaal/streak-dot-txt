"""Local FastAPI application for the REST API and HTMX interface."""

from __future__ import annotations

import os
from pathlib import Path
from datetime import date

from fastapi import FastAPI, Form, HTTPException, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from streak_api.schemas import StatusResponse, StreakCreate, StreakResponse, StreakUpdate, TickCreate
from streak_core import DEFAULT_STREAKS_DIR, DuplicateTickError, InvalidStreakIdError, StreakNotFoundError, StreakRepository, StreakService

BASE_DIR = Path(__file__).parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


def _response(streak_id, streak):
    return StreakResponse.from_streak(streak, streak_id)


def create_app(streaks_dir: str | Path | None = None) -> FastAPI:
    directory = Path(streaks_dir or os.getenv("STREAKS_DIR", DEFAULT_STREAKS_DIR))
    service = StreakService(StreakRepository(directory))
    app = FastAPI(title="Streak API", description="Local API and UI for streak.txt files", version="2.0.0")
    app.state.service = service
    app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")

    def get_service() -> StreakService:
        return app.state.service

    def translate(error: Exception):
        if isinstance(error, StreakNotFoundError):
            raise HTTPException(404, "Streak not found") from error
        if isinstance(error, (InvalidStreakIdError, DuplicateTickError, ValueError, FileExistsError)):
            raise HTTPException(400, str(error)) from error
        raise error

    @app.get("/health")
    def health():
        return {"status": "healthy"}

    @app.get("/api/v1/config")
    def config():
        return {"streaks_directory": str(directory), "directory_exists": directory.exists(), "total_streak_files": len(service.repository.list_ids())}

    @app.get("/api/v1/streaks", response_model=list[StreakResponse])
    def list_streaks():
        return [_response(streak_id, streak) for streak_id, streak in service.list_streaks()]

    @app.get("/api/v1/streaks/{streak_id}", response_model=StreakResponse)
    def get_streak(streak_id: str):
        try:
            return _response(streak_id, service.get_streak(streak_id))
        except Exception as error:
            translate(error)

    @app.post("/api/v1/streaks", status_code=status.HTTP_201_CREATED, response_model=StreakResponse)
    def create_streak(payload: StreakCreate):
        try:
            streak_id, streak = service.create_streak(payload.name, payload.tick_type, payload.description)
            return _response(streak_id, streak)
        except Exception as error:
            translate(error)

    @app.put("/api/v1/streaks/{streak_id}", response_model=StreakResponse)
    def update_streak(streak_id: str, payload: StreakUpdate):
        try:
            return _response(streak_id, service.update_streak(streak_id, payload.description, payload.tick_type))
        except Exception as error:
            translate(error)

    @app.post("/api/v1/streaks/{streak_id}/tick", response_model=StatusResponse)
    def tick(streak_id: str):
        try:
            changed = service.tick_today(streak_id)
            return StatusResponse(message="Today's tick added" if changed else "Today already ticked", success=changed)
        except Exception as error:
            translate(error)

    @app.post("/api/v1/streaks/{streak_id}/ticks", response_model=StreakResponse)
    def add_tick(streak_id: str, payload: TickCreate):
        try:
            return _response(streak_id, service.add_tick(streak_id, payload.tick_datetime_str))
        except Exception as error:
            translate(error)

    @app.delete("/api/v1/streaks/{streak_id}", response_model=StatusResponse)
    def archive_streak(streak_id: str):
        try:
            service.archive_streak(streak_id)
            return StatusResponse(message="Streak archived")
        except Exception as error:
            translate(error)

    @app.get("/", response_class=HTMLResponse)
    def dashboard(request: Request):
        return templates.TemplateResponse(request, "dashboard.html", {"streaks": service.list_streaks(), "today": date.today()})

    @app.post("/ui/streaks", response_class=HTMLResponse)
    def create_streak_form(request: Request, name: str = Form(), tick_type: str = Form("Daily"), description: str = Form("")):
        try:
            service.create_streak(name, tick_type, description or None)
        except Exception as error:
            translate(error)
        return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)

    @app.post("/ui/streaks/{streak_id}/tick", response_class=HTMLResponse)
    def tick_card(request: Request, streak_id: str):
        try:
            service.tick_today(streak_id)
            return templates.TemplateResponse(request, "partials/streak_card.html", {"streak_id": streak_id, "streak": service.get_streak(streak_id), "today": date.today()})
        except Exception as error:
            translate(error)

    return app


app = create_app()
