from collections.abc import Generator

from fastapi import Request
from sqlalchemy.orm import Session


def get_db(request: Request) -> Generator[Session, None, None]:
    for db in request.app.state.database.session():
        db.info["early_review_client_capable"] = "empty-day-v1" in request.headers.get(
            "X-Client-Capabilities", ""
        ).split(",")
        yield db


def get_analysis_provider(request: Request):
    return request.app.state.analysis_provider
