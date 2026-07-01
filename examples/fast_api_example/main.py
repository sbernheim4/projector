from typing import Any, cast

import sqlite3
from fastapi import FastAPI, HTTPException

from app import api, build_entity, renderer, views_for

from . import db
from .domain_models import Address, User
from .sql_queries import CREATE_USER, DELETE_USER, GET_USER, LIST_USERS, RENAME_CITY, UPDATE_USER


app = FastAPI(title="Projector FastAPI example")
conn = db.connect()
db.init_db(conn)

user_entity = build_entity(User)
user_views = views_for(User)

UserAPI = api(
    user_entity,
    renderer=renderer.Pydantic,
    create=user_views.name + user_views.email + user_views.address.city + user_views.address.zip,
    read=user_views.name + user_views.email + user_views.address.city + user_views.address.zip,
    update=user_views.name + user_views.email + user_views.address.city + user_views.address.zip,
)

CommandAPI = api(
    user_entity,
    renderer=renderer.Pydantic,
    rename_city=user_views.address.city,
)


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


@app.post("/users", response_model=UserAPI.create_model)
def create_user(user: UserAPI.create_model):
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


@app.get("/users", response_model=list[UserAPI.read_model])
def list_users():
    rows = conn.execute(LIST_USERS).fetchall()
    return [row_to_user(row) for row in rows]


@app.get("/users/{user_id}", response_model=UserAPI.read_model)
def get_user(user_id: int):
    row = conn.execute(GET_USER, {"id": user_id}).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="User not found")
    return row_to_user(cast(sqlite3.Row, row))


@app.put("/users/{user_id}", response_model=UserAPI.update_model)
def update_user(user_id: int, user: UserAPI.update_model):
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


@app.delete("/users/{user_id}")
def delete_user(user_id: int):
    conn.execute(DELETE_USER, {"id": user_id})
    conn.commit()
    return {"deleted": True}


@app.post("/users/{user_id}/commands/rename-city", response_model=CommandAPI.rename_city_model)
def rename_city(user_id: int, command: CommandAPI.rename_city_model):
    conn.execute(
        RENAME_CITY,
        {
            "id": user_id,
            "city": command.city,
        },
    )
    conn.commit()
    row = conn.execute(GET_USER, {"id": user_id}).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="User not found")
    return {"city": cast(sqlite3.Row, row)["city"]}


def main() -> None:
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8080, reload=False)


if __name__ == "__main__":
    main()
