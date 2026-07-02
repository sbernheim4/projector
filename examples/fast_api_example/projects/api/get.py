from ...query import TypedConnection
from ..models import Project


def get_project(conn: TypedConnection, project_id: int):
    return conn.SELECT(Project).WHERE(id=project_id).one()
