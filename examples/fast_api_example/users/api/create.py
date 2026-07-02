from ...query import TypedConnection
from ..models import User, UserCreate
from ..sql_queries import CREATE_USER


def create_user(conn: TypedConnection, user: UserCreate):
    cur = conn.execute(
        CREATE_USER,
        {
            "name": user.name,
            "email": user.email,
            "city": user.address.city,
            "zip": user.address.zip,
        },
    )
    conn.commit()
    return conn.SELECT(User).WHERE(id=cur.lastrowid).one()
