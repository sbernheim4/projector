from fastapi import APIRouter, HTTPException

from app import api, build_entity, renderer

from ..projects.api import add_task, complete_task, create_project, delete_project, get_project, list_projects, update_project
from ..projects.api.common import row_to_project
from ..projects.models import Project, project_views
from ..db import conn

router = APIRouter()

project_entity = build_entity(Project)

ProjectAPI = api(
    project_entity,
    renderer=renderer.Pydantic,
    create=project_views.name + project_views.description + project_views.task.title + project_views.task.done,
    read=project_views.name + project_views.description + project_views.task.title + project_views.task.done,
    update=project_views.name + project_views.description + project_views.task.title + project_views.task.done,
    add_task=project_views.task.title,
    complete_task=project_views.task.done,
)

ProjectCreate = ProjectAPI.create_model
ProjectRead = ProjectAPI.read_model
ProjectUpdate = ProjectAPI.update_model
AddTaskCommand = ProjectAPI.add_task_model
CompleteTaskCommand = ProjectAPI.complete_task_model

conn.register(Project, "projects", row_to_project)


@router.post("/projects", response_model=ProjectCreate)
def create(project: ProjectCreate):
    row = create_project(conn, project)
    if row is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return row


@router.get("/projects", response_model=list[ProjectRead])
def list_all():
    return list_projects(conn)


@router.get("/projects/{project_id}", response_model=ProjectRead)
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


@router.post("/projects/{project_id}/commands/add-task", response_model=AddTaskCommand)
def add(project_id: int, command: AddTaskCommand):
    row = add_task(conn, project_id, command.task.title)
    if row is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return row


@router.post("/projects/{project_id}/commands/complete-task", response_model=CompleteTaskCommand)
def complete(project_id: int, command: CompleteTaskCommand):
    row = complete_task(conn, project_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return row
