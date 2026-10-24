"""Transport mappings only; request_context enforces editor/manager writes."""

from typing import Annotated

from fastapi import APIRouter, Depends, Header, Query
from sqlalchemy.orm import Session

from push_kids.learning_suggestions import queries, recording, service
from push_kids.learning_suggestions.schemas import (
    Edit,
    Generate,
    PromptDisplayed,
    RecordIntentCreate,
    RecordLink,
    RequestKey,
    Version,
)
from push_kids.platform.context import RequestContext, request_context
from push_kids.platform.dependencies import get_db

router = APIRouter(
    prefix="/children/{child_id}/learning-suggestions", tags=["learning-suggestions"]
)
Context = Annotated[RequestContext, Depends(request_context)]
DB = Annotated[Session, Depends(get_db)]
Key = Annotated[
    str,
    Header(alias="Idempotency-Key", min_length=8, max_length=100, pattern=r"^[A-Za-z0-9._:-]+$"),
]


@router.get("/current")
def current(child_id: str, context: Context, db: DB):
    result = queries.current(db, context.family_id, child_id)
    if context.role not in {"manager", "editor"}:
        result.update(proposal=None, job=None, stale=False, can_regenerate=False)
    return result


@router.post("/automatic-prompt")
def automatic_prompt(child_id: str, body: RequestKey, context: Context, db: DB):
    return service.automatic_prompt(
        db, context.family_id, child_id, context.member_id or "local-parent", body.request_id
    )


@router.post("/prompt-displayed")
def prompt_displayed(child_id: str, body: PromptDisplayed, context: Context, db: DB):
    return service.prompt_displayed(
        db, context.family_id, child_id, body.prompt_on, body.request_id
    )


@router.post("/generate", status_code=202)
def generate(child_id: str, body: Generate, context: Context, db: DB, key: Key):
    return service.generate(
        db, context.family_id, child_id, body.expected_version, key, body.replace_suggestion_id
    )


@router.get("/jobs/{job_id}")
def job(child_id: str, job_id: str, context: Context, db: DB):
    return queries.get_job(db, context.family_id, child_id, job_id)


@router.patch("/{suggestion_id}")
def edit(child_id: str, suggestion_id: str, body: Edit, context: Context, db: DB):
    return service.edit(db, context.family_id, child_id, suggestion_id, body)


@router.post("/{suggestion_id}/approve", status_code=201)
def approve(child_id: str, suggestion_id: str, body: Version, context: Context, db: DB):
    return service.approve(
        db,
        context.family_id,
        child_id,
        context.member_id or "local-parent",
        suggestion_id,
        body.expected_version,
    )


@router.post("/{suggestion_id}/defer")
def defer(child_id: str, suggestion_id: str, body: Version, context: Context, db: DB):
    return service.defer(
        db,
        context.family_id,
        child_id,
        context.member_id or "local-parent",
        suggestion_id,
        body.expected_version,
    )


@router.post("/tasks/{task_id}/remove", status_code=202)
def remove(child_id: str, task_id: str, body: Version, context: Context, db: DB, key: Key):
    return service.remove_task(db, context.family_id, child_id, task_id, body.expected_version, key)


@router.post("/tasks/{task_id}/record-intents", status_code=201)
def create_intent(child_id: str, task_id: str, body: RecordIntentCreate, context: Context, db: DB):
    return recording.create_intent(
        db,
        context.family_id,
        child_id,
        context.member_id or "local-parent",
        task_id,
        body.expected_version,
        body.mode,
        body.request_id,
    )


@router.post("/tasks/{task_id}/records")
def record(child_id: str, task_id: str, body: RecordLink, context: Context, db: DB):
    return recording.link_records(
        db, context.family_id, child_id, task_id, body.intent_id, body.submission_id
    )


@router.get("/tasks/{task_id}/records")
def records(
    child_id: str,
    task_id: str,
    context: Context,
    db: DB,
    limit: Annotated[int, Query(ge=1, le=50)] = 20,
    cursor: Annotated[str | None, Query(max_length=1500)] = None,
):
    return recording.records_page(
        db, context.family_id, child_id, task_id, limit=limit, cursor=cursor
    )
