from typing import Any, cast

from examples.fast_api_example import db
from examples.fast_api_example.users.api import create_user, list_users, update_user
from examples.fast_api_example.users.api.common import row_to_user
from examples.fast_api_example.users.models import (
    User,
    UserCreate,
    UserListItem,
    UserRead,
    UserUpdate,
)


def test_fast_api_example_uses_projected_api_shapes():
    conn = db.connect()
    db.init_db(conn)
    conn.register(User, "users", row_to_user)
    user_create_model = cast(Any, UserCreate)
    user_read_model = cast(Any, UserRead)
    user_list_item_model = cast(Any, UserListItem)
    user_update_model = cast(Any, UserUpdate)

    created = create_user(
        conn,
        user_create_model(
            name="Ada Lovelace",
            email="ada@example.com",
            address={"city": "London", "zip": "SW1A"},
        ),
    )
    assert created is not None
    user = user_read_model.model_validate(created).model_dump()
    assert user == {
        "id": user["id"],
        "name": "Ada Lovelace",
        "email": "ada@example.com",
        "address": {"city": "London", "zip": "SW1A"},
    }

    listed = list_users(conn)
    list_item = user_list_item_model.model_validate(
        next(item for item in listed if item["id"] == user["id"])
    ).model_dump()
    assert list_item == {
        "id": user["id"],
        "name": "Ada Lovelace",
        "address": {"city": "London"},
    }

    patched = update_user(
        conn,
        user["id"],
        user_update_model(address={"city": "Paris"}),
    )
    assert patched is not None
    assert user_read_model.model_validate(patched).model_dump() == {
        "id": user["id"],
        "name": "Ada Lovelace",
        "email": "ada@example.com",
        "address": {"city": "Paris", "zip": "SW1A"},
    }
