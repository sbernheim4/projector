from typing import Any, cast

from ...query import TypedConnection
from ..models import User, UserUpdate
from ..sql_queries import UPDATE_USER


def update_user(conn: TypedConnection, user_id: int, user: UserUpdate):
    selected = conn.SELECT(User).WHERE(id=user_id).one()
    if selected is None:
        return None
    current = cast(dict[str, Any], selected)

    fields_set = getattr(user, "model_fields_set", set())

    name = (
        user.name if "name" in fields_set and user.name is not None else current["name"]
    )
    email = (
        user.email
        if "email" in fields_set and user.email is not None
        else current["email"]
    )
    city = current["address"]["city"]
    zip_code = current["address"]["zip"]
    if "address" in fields_set and user.address is not None:
        address_fields_set = getattr(user.address, "model_fields_set", set())
        if "city" in address_fields_set and user.address.city is not None:
            city = user.address.city
        if "zip" in address_fields_set and user.address.zip is not None:
            zip_code = user.address.zip

    conn.execute(
        UPDATE_USER,
        {
            "id": user_id,
            "name": name,
            "email": email,
            "city": city,
            "zip": zip_code,
        },
    )
    conn.commit()
    return conn.SELECT(User).WHERE(id=user_id).one()
