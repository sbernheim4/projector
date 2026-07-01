from dataclasses import dataclass


@dataclass(kw_only=True)
class Address:
    city: str
    zip: str


@dataclass(kw_only=True)
class User:
    name: str
    email: str
    address: Address
