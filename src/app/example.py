from .encode import PydanticRenderer, build_entity, api, build_views
from .models import User

user = build_entity(User)
views = build_views(user)

UserAPI = api(
    user,
    renderer=PydanticRenderer(),
    read=(views.name + views.address.city),
    write=views.name,
    create=(views.name + views.address.city + views.address.zip),
)

print(UserAPI.create)
print(UserAPI.read)
print(UserAPI.write)
