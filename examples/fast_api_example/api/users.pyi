class RenameCityCommandModel:
    address: UserRename_city_address

class UserRename_city_address:
    city: str

class UserCreateModel:
    name: str
    email: str
    address: UserCreate_address

class UserCreate_address:
    city: str
    zip: str

class UserReadModel:
    name: str
    email: str
    address: UserRead_address

class UserRead_address:
    city: str
    zip: str

class UserUpdateModel:
    name: str | None
    email: str | None
    address: UserUpdate_address | None
