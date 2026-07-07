from fastapi import APIRouter, HTTPException

from ..db import conn
from ..users.api import (
    create_user,
    delete_user,
    get_user,
    list_users,
    rename_city,
    update_user,
)
from ..users.api.common import row_to_user
from ..users.models import User, UserCreate, UserRenameUserCity, UserUpdate

router: APIRouter = APIRouter()

conn.register(User, "users", row_to_user)


@router.post("/users", response_model=UserCreate)
def create(user: UserCreate):
    row = create_user(conn, user)
    if row is None:
        raise HTTPException(status_code=404, detail="User not found")
    return row


@router.get("/users", response_model=list[User])
def list_all():
    return list_users(conn)


@router.get("/users/{user_id}", response_model=User)
def get_one(user_id: int):
    row = get_user(conn, user_id)
    if row is None:
        raise HTTPException(status_code=404, detail="User not found")
    return row


@router.put("/users/{user_id}", response_model=UserUpdate)
def update(user_id: int, user: UserUpdate):
    row = update_user(conn, user_id, user)
    if row is None:
        raise HTTPException(status_code=404, detail="User not found")
    return row


@router.delete("/users/{user_id}")
def delete(user_id: int):
    delete_user(conn, user_id)
    return {"deleted": True}


@router.post("/users/{user_id}/commands/rename-city", response_model=UserRenameUserCity)
def rename(user_id: int, command: UserRenameUserCity):
    row = rename_city(conn, user_id, command)
    if row is None:
        raise HTTPException(status_code=404, detail="User not found")
    return row
