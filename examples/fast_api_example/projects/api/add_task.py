from ...query import TypedConnection
from ..models import Project
from ..sql_queries import ADD_TASK


def add_task(conn: TypedConnection, project_id: int, title: str):
    conn.execute(ADD_TASK, {"id": project_id, "task_title": title})
    conn.commit()
    return conn.SELECT(Project).WHERE(id=project_id).one()
