from .projection import Leaf


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


def views_for(model_cls: object) -> UserView: ...
