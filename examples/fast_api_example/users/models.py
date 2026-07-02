from dataclasses import dataclass

from app import api, build_entity, renderer, views_for


@dataclass(kw_only=True)
class Address:
    city: str
    zip: str


@dataclass(kw_only=True)
class User:
    name: str
    email: str
    address: Address


user_views = views_for(User)

user_entity = build_entity(User)
UserAPI = api(
    user_entity,
    renderer=renderer.Pydantic,
    create=user_views.name + user_views.email + user_views.address.city + user_views.address.zip,
    update=user_views.name + user_views.email + user_views.address.city + user_views.address.zip,
    renameUserCity=user_views.address.city,
)

UserCreate = UserAPI.CreateModel
UserUpdate = UserAPI.UpdateModel
UserRenameUserCity = UserAPI.RenameUserCityModel
