from ...query import TypedConnection
from ..models import User


def get_user(conn: TypedConnection, user_id: int):
    return conn.SELECT(User).WHERE(id=user_id).one()
