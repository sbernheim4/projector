from dataclasses import dataclass

from app import project, renderer, views_for


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

UserModels = project(
    User,
    renderer=renderer.Pydantic,
    Create=user_views.name
    + user_views.email
    + user_views.address.city
    + user_views.address.zip,
    Update=user_views.name
    + user_views.email
    + user_views.address.city
    + user_views.address.zip,
    RenameUserCity=user_views.address.city,
)

UserCreate = UserModels.CreateModel
UserUpdate = UserModels.UpdateModel
UserRenameUserCity = UserModels.RenameUserCityModel
