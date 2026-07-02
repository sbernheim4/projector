from fastapi import APIRouter

class RenameCityCommand:
    address: "UserRename_city_address"

class UserRename_city_address:
    city: str

class UserModel:
    name: str
    email: str
    address: "Address"

class Address:
    city: str
    zip: str

router: APIRouter
