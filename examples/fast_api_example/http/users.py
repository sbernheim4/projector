from fastapi import APIRouter, HTTPException

from app import api, build_entity, renderer

from ..db import conn
from ..users.api import create_user, delete_user, get_user, list_users, rename_city, update_user
from ..users.api.common import row_to_user
from ..users.models import user_views, User as UserModel

router = APIRouter()

user_entity = build_entity(UserModel)

UserAPI = api(
    user_entity,
    renderer=renderer.Pydantic,
    create=user_views.name + user_views.email + user_views.address.city + user_views.address.zip,
    read=user_views.name + user_views.email + user_views.address.city + user_views.address.zip,
    update=user_views.name + user_views.email + user_views.address.city + user_views.address.zip,
    rename_city=user_views.address.city,
)

UserCreate = UserAPI.create_model
UserRead = UserAPI.read_model
UserUpdate = UserAPI.update_model
RenameCityCommand = UserAPI.rename_city_model

conn.register(UserModel, "users", row_to_user)


@router.post("/users", response_model=UserCreate)
def create(user: UserCreate):
    row = create_user(conn, user)
    if row is None:
        raise HTTPException(status_code=404, detail="User not found")
    return row


@router.get("/users", response_model=list[UserRead])
def list_all():
    return list_users(conn)


@router.get("/users/{user_id}", response_model=UserRead)
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


@router.post("/users/{user_id}/commands/rename-city", response_model=RenameCityCommand)
def rename(user_id: int, command: RenameCityCommand):
    row = rename_city(conn, user_id, command.address.city)
    if row is None:
        raise HTTPException(status_code=404, detail="User not found")
    return row
