from dataclasses import is_dataclass

from app.encode import DataclassRenderer, UNSET, build_entity, api, PydanticRenderer
from app.views import views_for

from .models import User

user = build_entity(User)
views = views_for(User)

UserAPI = api(
    user,
    renderer=PydanticRenderer(),
    read=views.name + views.address.city,
    update=views.name,
    create=views.name + views.address.city + views.address.zip,
)

print(UserAPI.create_model)
print(UserAPI.read_model)
print(UserAPI.update_model)

instance = UserAPI.create(name="Sam", address={"city": "Paris", "zip": "75001"})
print(instance)

update = UserAPI.update(name=None)
print(update)
print(update.model_fields_set)

DataclassUserAPI = api(
    user,
    renderer=DataclassRenderer(),
    read=views.name + views.address.city,
    update=views.name + views.address.city,
    create=views.name + views.address.city + views.address.zip,
)

dataclass_update = DataclassUserAPI.update(address={"city": "Paris"})
print(is_dataclass(DataclassUserAPI.update_model))
print(dataclass_update)
print(dataclass_update.name is UNSET)
