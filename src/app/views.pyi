from typing import overload

from .encode import Leaf
from .models import Address, Profile, User


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
