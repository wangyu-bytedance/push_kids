from collections.abc import Generator

from fastapi import Request
from sqlalchemy.orm import Session


def get_db(request: Request) -> Generator[Session, None, None]:
    yield from request.app.state.database.session()


def get_analysis_provider(request: Request):
    return request.app.state.analysis_provider
