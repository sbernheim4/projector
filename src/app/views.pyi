from .projection import Leaf


class AddressView:
    city: Leaf[str]
    zip: Leaf[str]


class UserView:
    name: Leaf[str]
    email: Leaf[str]
    address: AddressView


def views_for(model_cls: object) -> UserView: ...
