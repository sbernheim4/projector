from ...query import TypedConnection
from ..sql_queries import DELETE_USER


def delete_user(conn: TypedConnection, user_id: int) -> None:
    conn.execute(DELETE_USER, {"id": user_id})
    conn.commit()
