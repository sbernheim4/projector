from typing import Any

import sqlite3
from fastapi import APIRouter, HTTPException

from ... import sql_queries
from ...query import TypedConnection
from ...users.models import User, user_views
from ..models import UserCreateModel

router = APIRouter()


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


def register_users(conn: TypedConnection) -> None:
    conn.register(User, "users", row_to_user)


@router.post("/users", response_model=UserCreateModel)
def create_user(conn: TypedConnection, user: UserCreateModel):
    cur = conn.execute(
        sql_queries.CREATE_USER,
        {
            "name": user.name,
            "email": user.email,
            "city": user.address.city,
            "zip": user.address.zip,
        },
    )
    conn.commit()
    row = conn.SELECT(User).WHERE(id=cur.lastrowid).one()
    if row is None:
        raise HTTPException(status_code=404, detail="User not found")
    return row

