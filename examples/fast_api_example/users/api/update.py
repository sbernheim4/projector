from ...query import TypedConnection
from ..models import User, UserUpdate
from ..sql_queries import UPDATE_USER


def update_user(conn: TypedConnection, user_id: int, user: UserUpdate):
    conn.execute(
        UPDATE_USER,
        {
            "id": user_id,
            "name": user.name,
            "email": user.email,
            "city": user.address.city,
            "zip": user.address.zip,
        },
    )
    conn.commit()
    return conn.SELECT(User).WHERE(id=user_id).one()
