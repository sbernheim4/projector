from typing import Any

import sqlite3
from fastapi import APIRouter, HTTPException

from app import api, build_entity, renderer

from ..projects_models import Project, project_views
from ..projects_sql import (
    ADD_TASK,
    COMPLETE_TASK,
    CREATE_PROJECT,
    DELETE_PROJECT,
    LIST_PROJECTS,
    UPDATE_PROJECT,
)
from ..query import TypedConnection

router = APIRouter()

project_entity = build_entity(Project)

ProjectAPI = api(
    project_entity,
    renderer=renderer.Pydantic,
    create=project_views.name
    + project_views.description
    + project_views.task.title
    + project_views.task.done,
    read=project_views.name
    + project_views.description
    + project_views.task.title
    + project_views.task.done,
    update=project_views.name
    + project_views.description
    + project_views.task.title
    + project_views.task.done,
    add_task=project_views.task.title,
    complete_task=project_views.task.done,
)

ProjectCreate = ProjectAPI.create_model
ProjectRead = ProjectAPI.read_model
ProjectUpdate = ProjectAPI.update_model
AddTaskCommand = ProjectAPI.add_task_model
CompleteTaskCommand = ProjectAPI.complete_task_model


def row_to_project(row: sqlite3.Row) -> dict[str, Any]:
    return {
        "id": row["id"],
        "name": row["name"],
        "description": row["description"],
        "task": {
            "title": row["task_title"],
            "done": bool(row["task_done"]),
        },
    }


def map_project(row: sqlite3.Row) -> dict[str, Any]:
    return row_to_project(row)


def configure_project_routes(conn: TypedConnection) -> None:
    conn.register(Project, "projects", map_project)

    @router.post("/projects", response_model=ProjectCreate)
    def create_project(project: ProjectCreate):
        payload = project.model_dump()
        cur = conn.execute(
            CREATE_PROJECT,
            {
                "name": payload["name"],
                "description": payload["description"],
                "task_title": payload["task"]["title"],
                "task_done": int(payload["task"]["done"]),
            },
        )
        conn.commit()
        row = conn.SELECT(Project).WHERE(id=cur.lastrowid).one()
        if row is None:
            raise HTTPException(status_code=404, detail="Project not found")
        return row

    @router.get("/projects", response_model=list[ProjectRead])
    def list_projects():
        rows = conn.execute(LIST_PROJECTS).fetchall()
        return [row_to_project(row) for row in rows]

    @router.get("/projects/{project_id}", response_model=ProjectRead)
    def get_project(project_id: int):
        row = conn.SELECT(Project).WHERE(id=project_id).one()
        if row is None:
            raise HTTPException(status_code=404, detail="Project not found")
        return row

    @router.put("/projects/{project_id}", response_model=ProjectUpdate)
    def update_project(project_id: int, project: ProjectUpdate):
        payload = project.model_dump()
        conn.execute(
            UPDATE_PROJECT,
            {
                "id": project_id,
                "name": payload["name"],
                "description": payload["description"],
                "task_title": payload["task"]["title"],
                "task_done": int(payload["task"]["done"]),
            },
        )
        conn.commit()
        row = conn.SELECT(Project).WHERE(id=project_id).one()
        if row is None:
            raise HTTPException(status_code=404, detail="Project not found")
        return row

    @router.delete("/projects/{project_id}")
    def delete_project(project_id: int):
        conn.execute(DELETE_PROJECT, {"id": project_id})
        conn.commit()
        return {"deleted": True}

    @router.post(
        "/projects/{project_id}/commands/add-task",
        response_model=AddTaskCommand,
    )
    def add_task(project_id: int, command: AddTaskCommand):
        conn.execute(
            ADD_TASK,
            {
                "id": project_id,
                "task_title": command.task.title,
            },
        )
        conn.commit()
        row = conn.SELECT(Project).WHERE(id=project_id).one()
        if row is None:
            raise HTTPException(status_code=404, detail="Project not found")
        return row

    @router.post(
        "/projects/{project_id}/commands/complete-task",
        response_model=CompleteTaskCommand,
    )
    def complete_task(project_id: int, command: CompleteTaskCommand):
        conn.execute(
            COMPLETE_TASK,
            {
                "id": project_id,
            },
        )
        conn.commit()
        row = conn.SELECT(Project).WHERE(id=project_id).one()
        if row is None:
            raise HTTPException(status_code=404, detail="Project not found")
        return row
