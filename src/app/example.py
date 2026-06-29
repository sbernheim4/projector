from .encode import build_entity, api, PydanticRenderer
from .models import User
from .views import views_for

user = build_entity(User)
views = views_for(User)

UserAPI = api(
    user,
    renderer=PydanticRenderer(),
    read=views.name + views.address.city,
    write=views.name,
    create=views.name + views.address.city + views.address.zip,
)

# --- model classes (types) ---
print(UserAPI.create_model)
print(UserAPI.read_model)
print(UserAPI.write_model)

# --- factories ---
instance = UserAPI.create(name="Sam", address={"city": "Paris", "zip": "75001"})

print(instance)
