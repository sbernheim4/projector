from typing import Protocol

from ...query import TypedConnection
from ..models import User
from ..sql_queries import UPDATE_USER


class _Address(Protocol):
    city: str
    zip: str


class _UserUpdate(Protocol):
    name: str
    email: str
    address: _Address


def update_user(conn: TypedConnection, user_id: int, user: _UserUpdate):
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
