from typing import overload

from app.projection import Leaf


class Address:
    city: str
    zip: str


class Profile:
    bio: str
    address: Address


class User:
    name: str
    email: str
    profile: Profile
    address: Address


class AddressView:
    city: Leaf[str]
    zip: Leaf[str]


class ProfileView:
    bio: Leaf[str]
    address: AddressView


class UserView:
    name: Leaf[str]
    email: Leaf[str]
    profile: ProfileView
    address: AddressView


@overload
def views_for(model_cls: type[Address]) -> AddressView: ...


@overload
def views_for(model_cls: type[Profile]) -> ProfileView: ...


@overload
def views_for(model_cls: type[User]) -> UserView: ...
