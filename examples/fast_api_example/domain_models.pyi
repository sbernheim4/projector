from typing import Any, overload

from app.projection import Leaf

class Address:
    city: str
    zip: str

class AddressView:
    city: Leaf[str]
    zip: Leaf[str]

address_views: AddressView

class User:
    name: str
    email: str
    address: Address

class UserView:
    name: Leaf[str]
    email: Leaf[str]
    address: AddressView

user_views: UserView

@overload
def views_for(model_cls: type[Address]) -> AddressView: ...
@overload
def views_for(model_cls: type[User]) -> UserView: ...
def views_for(model_cls: type[object]) -> Any: ...
