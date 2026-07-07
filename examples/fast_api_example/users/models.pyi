from typing import Any, overload

from projector.projection import Leaf

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

class UserCreateAddress:
    city: str
    zip: str

class UserCreateAddressView:
    city: Leaf[str]
    zip: Leaf[str]

usercreateaddress_views: UserCreateAddressView

class UserCreate:
    name: str
    email: str
    address: UserCreateAddress

class UserCreateView:
    name: Leaf[str]
    email: Leaf[str]
    address: UserCreateAddressView

usercreate_views: UserCreateView

class UserRenameUserCityAddress:
    city: str

class UserRenameUserCityAddressView:
    city: Leaf[str]

userrenameusercityaddress_views: UserRenameUserCityAddressView

class UserRenameUserCity:
    address: UserRenameUserCityAddress

class UserRenameUserCityView:
    address: UserRenameUserCityAddressView

userrenameusercity_views: UserRenameUserCityView

class UserUpdateAddress:
    city: str
    zip: str

class UserUpdateAddressView:
    city: Leaf[str]
    zip: Leaf[str]

userupdateaddress_views: UserUpdateAddressView

class UserUpdate:
    name: str
    email: str
    address: UserUpdateAddress

class UserUpdateView:
    name: Leaf[str]
    email: Leaf[str]
    address: UserUpdateAddressView

userupdate_views: UserUpdateView

@overload
def views_for(model_cls: type[Address]) -> AddressView: ...
@overload
def views_for(model_cls: type[User]) -> UserView: ...
@overload
def views_for(model_cls: type[UserCreate]) -> UserCreateView: ...
@overload
def views_for(model_cls: type[UserRenameUserCity]) -> UserRenameUserCityView: ...
@overload
def views_for(model_cls: type[UserUpdate]) -> UserUpdateView: ...
def views_for(model_cls: type[object]) -> Any: ...
