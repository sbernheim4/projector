from typing import Any, cast

import sqlite3
from fastapi import APIRouter, HTTPException

from app import api, build_entity, renderer, views_for

from ..domain_models import User
from ..sql_queries import (
    CREATE_USER,
    DELETE_USER,
    GET_USER,
    LIST_USERS,
    RENAME_CITY,
    UPDATE_USER,
)

router = APIRouter()

user_entity = build_entity(User)
user_views = views_for(User)

UserAPI = api(
    user_entity,
    renderer=renderer.Pydantic,
    create=user_views.name
    + user_views.email
    + user_views.address.city
    + user_views.address.zip,
    read=user_views.name
    + user_views.email
    + user_views.address.city
    + user_views.address.zip,
    update=user_views.name
    + user_views.email
    + user_views.address.city
    + user_views.address.zip,
    rename_city=user_views.address.city,
)

UserCreateModel = UserAPI.create_model
UserReadModel = UserAPI.read_model
UserUpdateModel = UserAPI.update_model
RenameCityCommandModel = UserAPI.rename_city_model


def row_to_user(row: sqlite3.Row) -> dict[str, Any]:
    return {
        "id": row["id"],
        "name": row["name"],
        "email": row["email"],
        "address": {
            "city": row["city"],
            "zip": row["zip"],
        },
    }


def configure_user_routes(conn: sqlite3.Connection) -> None:
    @router.post("/users", response_model=UserCreateModel)
    def create_user(user: UserCreateModel):
        payload = user.model_dump()
        cur = conn.execute(
            CREATE_USER,
            {
                "name": payload["name"],
                "email": payload["email"],
                "city": payload["address"]["city"],
                "zip": payload["address"]["zip"],
            },
        )
        conn.commit()
        row = conn.execute(GET_USER, {"id": cur.lastrowid}).fetchone()
        return row_to_user(cast(sqlite3.Row, row))

    @router.get("/users", response_model=list[UserReadModel])
    def list_users():
        rows = conn.execute(LIST_USERS).fetchall()
        return [row_to_user(row) for row in rows]

    @router.get("/users/{user_id}", response_model=UserReadModel)
    def get_user(user_id: int):
        row = conn.execute(GET_USER, {"id": user_id}).fetchone()
        if row is None:
            raise HTTPException(status_code=404, detail="User not found")
        return row_to_user(cast(sqlite3.Row, row))

    @router.put("/users/{user_id}", response_model=UserUpdateModel)
    def update_user(user_id: int, user: UserUpdateModel):
        payload = user.model_dump()
        conn.execute(
            UPDATE_USER,
            {
                "id": user_id,
                "name": payload["name"],
                "email": payload["email"],
                "city": payload["address"]["city"],
                "zip": payload["address"]["zip"],
            },
        )
        conn.commit()
        row = conn.execute(GET_USER, {"id": user_id}).fetchone()
        if row is None:
            raise HTTPException(status_code=404, detail="User not found")
        return row_to_user(cast(sqlite3.Row, row))

    @router.delete("/users/{user_id}")
    def delete_user(user_id: int):
        conn.execute(DELETE_USER, {"id": user_id})
        conn.commit()
        return {"deleted": True}

    @router.post(
        "/users/{user_id}/commands/rename-city",
        response_model=RenameCityCommandModel,
    )
    def rename_city(user_id: int, command: RenameCityCommandModel):
        conn.execute(
            RENAME_CITY,
            {
                "id": user_id,
                "city": command.address.city,
            },
        )
        conn.commit()
        row = conn.execute(GET_USER, {"id": user_id}).fetchone()
        if row is None:
            raise HTTPException(status_code=404, detail="User not found")
        return {
            "address": {
                "city": cast(sqlite3.Row, row)["city"],
            }
        }
