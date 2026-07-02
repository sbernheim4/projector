from ...query import TypedConnection
from ..models import User
from ..sql_queries import RENAME_CITY


def rename_city(conn: TypedConnection, user_id: int, city: str):
    conn.execute(RENAME_CITY, {"id": user_id, "city": city})
    conn.commit()
    return conn.SELECT(User).WHERE(id=user_id).one()
