from ...query import TypedConnection
from ..models import Project, ProjectAddTask
from ..sql_queries import ADD_TASK


def add_task(
    conn: TypedConnection, project_id: int, command: ProjectAddTask
) -> Project | None:
    conn.execute(ADD_TASK, {"id": project_id, "task_title": command.task.title})
    conn.commit()
    return conn.SELECT(Project).WHERE(id=project_id).one()
