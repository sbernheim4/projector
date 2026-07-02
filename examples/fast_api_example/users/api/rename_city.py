from ...query import TypedConnection
from ..models import User, UserRenameUserCity
from ..sql_queries import RENAME_CITY


def rename_city(conn: TypedConnection, user_id: int, command: UserRenameUserCity):
    conn.execute(RENAME_CITY, {"id": user_id, "city": command.address.city})
    conn.commit()
    return conn.SELECT(User).WHERE(id=user_id).one()
