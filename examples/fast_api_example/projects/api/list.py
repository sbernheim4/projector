from ...query import TypedConnection
from .common import row_to_project
from ..sql_queries import LIST_PROJECTS


def list_projects(conn: TypedConnection):
    return [row_to_project(row) for row in conn.execute(LIST_PROJECTS).fetchall()]
