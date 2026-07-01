from dataclasses import dataclass
from typing import TypedDict


@dataclass(kw_only=True)
class Address:
    city: str
    zip: str


@dataclass(kw_only=True)
class User:
    name: str
    email: str
    address: Address


class RenameCityCommand(TypedDict):
    city: str

