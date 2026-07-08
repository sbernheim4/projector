from dataclasses import dataclass

from projector import project, renderer, views_for


@dataclass(kw_only=True)
class Address:
    city: str
    zip: str


@dataclass(kw_only=True)
class User:
    id: int
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
    Read=user_views.id
    + user_views.name
    + user_views.email
    + user_views.address.city
    + user_views.address.zip,
    ListItem=user_views.id + user_views.name + user_views.address.city,
    Update=user_views.name
    + user_views.email
    + user_views.address.city
    + user_views.address.zip,
    RenameCity=user_views.address.city,
)

UserCreate = UserModels.CreateModel
UserRead = UserModels.ReadModel
UserListItem = UserModels.ListItemModel
UserUpdate = UserModels.UpdateModel
UserRenameCity = UserModels.RenameCityModel
