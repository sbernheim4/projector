from dataclasses import dataclass

from app import views_for


@dataclass(kw_only=True)
class Address:
    city: str
    zip: str


@dataclass(kw_only=True)
class User:
    name: str
    email: str
    address: Address


user_views = views_for(User)
