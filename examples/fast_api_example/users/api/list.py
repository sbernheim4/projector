from ...query import TypedConnection
from .common import row_to_user
from ..sql_queries import LIST_USERS


def list_users(conn: TypedConnection):
    return [row_to_user(row) for row in conn.execute(LIST_USERS).fetchall()]
