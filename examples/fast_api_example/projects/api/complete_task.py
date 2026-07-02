from ...query import TypedConnection
from ..models import Project, ProjectCompleteTask
from ..sql_queries import COMPLETE_TASK


def complete_task(conn: TypedConnection, project_id: int, command: ProjectCompleteTask):
    conn.execute(COMPLETE_TASK, {"id": project_id})
    conn.commit()
    return conn.SELECT(Project).WHERE(id=project_id).one()
