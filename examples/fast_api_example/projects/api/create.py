from ...query import TypedConnection
from ..models import Project, ProjectCreate
from ..sql_queries import CREATE_PROJECT


def create_project(conn: TypedConnection, project: ProjectCreate):
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
