from typing import Any, cast

from ...query import TypedConnection
from ..models import Project, ProjectUpdate
from ..sql_queries import UPDATE_PROJECT


def update_project(conn: TypedConnection, project_id: int, project: ProjectUpdate):
    selected = conn.SELECT(Project).WHERE(id=project_id).one()
    if selected is None:
        return None
    current = cast(dict[str, Any], selected)

    fields_set = getattr(project, "model_fields_set", set())

    name = (
        project.name
        if "name" in fields_set and project.name is not None
        else current["name"]
    )
    description = (
        project.description
        if "description" in fields_set and project.description is not None
        else current["description"]
    )
    task_title = current["task"]["title"]
    task_done = current["task"]["done"]
    if "task" in fields_set and project.task is not None:
        task_fields_set = getattr(project.task, "model_fields_set", set())
        if "title" in task_fields_set and project.task.title is not None:
            task_title = project.task.title
        if "done" in task_fields_set and project.task.done is not None:
            task_done = project.task.done

    conn.execute(
        UPDATE_PROJECT,
        {
            "id": project_id,
            "name": name,
            "description": description,
            "task_title": task_title,
            "task_done": int(task_done),
        },
    )
    conn.commit()
    return conn.SELECT(Project).WHERE(id=project_id).one()
