from typing import Protocol

from ...query import TypedConnection
from ..models import Project
from ..sql_queries import CREATE_PROJECT


class _Task(Protocol):
    title: str
    done: bool


class _ProjectCreate(Protocol):
    name: str
    description: str
    task: _Task


def create_project(conn: TypedConnection, project: _ProjectCreate):
    cur = conn.execute(
        CREATE_PROJECT,
        {
            "name": project.name,
            "description": project.description,
            "task_title": project.task.title,
            "task_done": int(project.task.done),
        },
    )
    conn.commit()
    return conn.SELECT(Project).WHERE(id=cur.lastrowid).one()
