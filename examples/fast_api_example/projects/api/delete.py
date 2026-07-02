from ...query import TypedConnection
from ..sql_queries import DELETE_PROJECT


def delete_project(conn: TypedConnection, project_id: int) -> None:
    conn.execute(DELETE_PROJECT, {"id": project_id})
    conn.commit()
