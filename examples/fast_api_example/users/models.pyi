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
    id: int
    name: str
    email: str
    address: Address

class UserView:
    id: Leaf[int]
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

class UserListItemAddress:
    city: str

class UserListItemAddressView:
    city: Leaf[str]

userlistitemaddress_views: UserListItemAddressView

class UserListItem:
    id: int
    name: str
    address: UserListItemAddress

class UserListItemView:
    id: Leaf[int]
    name: Leaf[str]
    address: UserListItemAddressView

userlistitem_views: UserListItemView

class UserReadAddress:
    city: str
    zip: str

class UserReadAddressView:
    city: Leaf[str]
    zip: Leaf[str]

userreadaddress_views: UserReadAddressView

class UserRead:
    id: int
    name: str
    email: str
    address: UserReadAddress

class UserReadView:
    id: Leaf[int]
    name: Leaf[str]
    email: Leaf[str]
    address: UserReadAddressView

userread_views: UserReadView

class UserRenameCityAddress:
    city: str

class UserRenameCityAddressView:
    city: Leaf[str]

userrenamecityaddress_views: UserRenameCityAddressView

class UserRenameCity:
    address: UserRenameCityAddress

class UserRenameCityView:
    address: UserRenameCityAddressView

userrenamecity_views: UserRenameCityView

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
def views_for(model_cls: type[UserListItem]) -> UserListItemView: ...
@overload
def views_for(model_cls: type[UserRead]) -> UserReadView: ...
@overload
def views_for(model_cls: type[UserRenameCity]) -> UserRenameCityView: ...
@overload
def views_for(model_cls: type[UserUpdate]) -> UserUpdateView: ...
def views_for(model_cls: type[object]) -> Any: ...
