from dataclasses import dataclass

from app import views_for
from app.encode import project


def build_user_api(renderer):
    @dataclass(kw_only=True)
    class Address:
        city: str
        zip: str

    @dataclass(kw_only=True)
    class User:
        name: str
        email: str
        address: Address

    views = views_for(User)

    return project(
        User,
        renderer=renderer,
        Create=views.name + views.email + views.address.city + views.address.zip,
        Read=views.name + views.address.city,
        Update=views.name + views.address.city,
    )
