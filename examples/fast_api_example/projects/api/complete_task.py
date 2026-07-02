from ...query import TypedConnection
from ..models import Project
from ..sql_queries import COMPLETE_TASK


def complete_task(conn: TypedConnection, project_id: int):
    conn.execute(COMPLETE_TASK, {"id": project_id})
    conn.commit()
    return conn.SELECT(Project).WHERE(id=project_id).one()
