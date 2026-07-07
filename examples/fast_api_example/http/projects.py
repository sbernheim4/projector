from fastapi import APIRouter, HTTPException

from ..db import conn
from ..projects.api import (
    add_task,
    complete_task,
    create_project,
    delete_project,
    get_project,
    list_projects,
    update_project,
)
from ..projects.api.common import row_to_project
from ..projects.models import (
    Project,
    ProjectAddTask,
    ProjectCompleteTask,
    ProjectCreate,
    ProjectUpdate,
)

router: APIRouter = APIRouter()

conn.register(Project, "projects", row_to_project)


@router.post("/projects", response_model=ProjectCreate)
def create(project: ProjectCreate):
    row = create_project(conn, project)
    if row is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return row


@router.get("/projects", response_model=list[Project])
def list_all():
    return list_projects(conn)


@router.get("/projects/{project_id}", response_model=Project)
def get_one(project_id: int):
    row = get_project(conn, project_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return row


@router.put("/projects/{project_id}", response_model=ProjectUpdate)
def update(project_id: int, project: ProjectUpdate):
    row = update_project(conn, project_id, project)
    if row is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return row


@router.delete("/projects/{project_id}")
def delete(project_id: int):
    delete_project(conn, project_id)
    return {"deleted": True}


@router.post("/projects/{project_id}/commands/add-task", response_model=ProjectAddTask)
def add(project_id: int, command: ProjectAddTask):
    row = add_task(conn, project_id, command)
    if row is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return row


@router.post(
    "/projects/{project_id}/commands/complete-task", response_model=ProjectCompleteTask
)
def complete(project_id: int, command: ProjectCompleteTask):
    row = complete_task(conn, project_id, command)
    if row is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return row
