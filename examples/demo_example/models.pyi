from typing import Any, overload

from projector.projection import Leaf

class Address:
    city: str
    zip: str

class AddressView:
    city: Leaf[str]
    zip: Leaf[str]

address_views: AddressView

class Profile:
    bio: str
    address: Address

class ProfileView:
    bio: Leaf[str]
    address: AddressView

profile_views: ProfileView

class User:
    name: str
    email: str
    profile: Profile
    address: Address

class UserView:
    name: Leaf[str]
    email: Leaf[str]
    profile: ProfileView
    address: AddressView

user_views: UserView

@overload
def views_for(model_cls: type[Address]) -> AddressView: ...
@overload
def views_for(model_cls: type[Profile]) -> ProfileView: ...
@overload
def views_for(model_cls: type[User]) -> UserView: ...
def views_for(model_cls: type[object]) -> Any: ...
