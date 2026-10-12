from typing import Annotated

from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session

from push_kids.daily_tasks.schemas import (
    DailyCompletionCommand,
    DailyTaskCreate,
    DailyTaskPatch,
    DailyTasksToday,
    DailyTaskView,
)
from push_kids.daily_tasks.service import DailyTasksService
from push_kids.platform.context import family_id
from push_kids.platform.dependencies import get_db

router = APIRouter(prefix="/children/{child_id}/daily-tasks", tags=["daily-tasks"])
Family = Annotated[str, Depends(family_id)]
DB = Annotated[Session, Depends(get_db)]


@router.get("", response_model=list[DailyTaskView])
def list_tasks(child_id: str, family: Family, db: DB):
    return DailyTasksService.list_tasks(db, family, child_id)


@router.get("/today", response_model=DailyTasksToday)
def today(child_id: str, family: Family, db: DB):
    return DailyTasksService.today(db, family, child_id)


@router.post("", response_model=DailyTaskView, status_code=201)
def create_task(child_id: str, body: DailyTaskCreate, family: Family, db: DB):
    return DailyTasksService.create(db, family, child_id, body)


@router.patch("/{task_id}", response_model=DailyTaskView)
def patch_task(child_id: str, task_id: str, body: DailyTaskPatch, family: Family, db: DB):
    return DailyTasksService.patch(db, family, child_id, task_id, body)


@router.delete("/{task_id}", status_code=204)
def remove_task(child_id: str, task_id: str, family: Family, db: DB):
    DailyTasksService.remove(db, family, child_id, task_id)
    return Response(status_code=204)


@router.put("/{task_id}/today-completion", response_model=DailyTasksToday)
def complete_task(
    child_id: str, task_id: str, body: DailyCompletionCommand, family: Family, db: DB
):
    return DailyTasksService.complete(db, family, child_id, task_id, body.completed)
