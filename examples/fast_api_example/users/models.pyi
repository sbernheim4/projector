from app.projection import Leaf


class Address:
    city: str
    zip: str


class AddressView:
    city: Leaf[str]
    zip: Leaf[str]


class User:
    name: str
    email: str
    address: Address


class UserView:
    name: Leaf[str]
    email: Leaf[str]
    address: AddressView


user_views: UserView
