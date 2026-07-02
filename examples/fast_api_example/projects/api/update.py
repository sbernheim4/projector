from ...query import TypedConnection
from ..models import Project, ProjectUpdate
from ..sql_queries import UPDATE_PROJECT


def update_project(conn: TypedConnection, project_id: int, project: ProjectUpdate):
    conn.execute(
        UPDATE_PROJECT,
        {
            "id": project_id,
            "name": project.name,
            "description": project.description,
            "task_title": project.task.title,
            "task_done": int(project.task.done),
        },
    )
    conn.commit()
    return conn.SELECT(Project).WHERE(id=project_id).one()
