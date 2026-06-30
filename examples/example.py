from argparse import ArgumentParser
from dataclasses import is_dataclass

from app import (
    DataclassRenderer,
    PydanticRenderer,
    UNSET,
    api,
    build_entity,
    generate_views_pyi,
    views_for,
)

from .models import Address, Profile, User

MODELS = [Address, Profile, User]

# End-to-end consumer flow:
# 1. build the schema IR
# 2. derive views
# 3. generate a matching .pyi for type checkers
# 4. build operation-specific API models
user = build_entity(User)
views = views_for(User)

UserAPI = api(
    user,
    renderer=PydanticRenderer(),
    read=views.name + views.address.city,
    update=views.name,
    create=views.name + views.address.city + views.address.zip,
)

instance = UserAPI.create(name="Sam", address={"city": "Paris", "zip": "75001"})
update = UserAPI.update(name=None)

DataclassUserAPI = api(
    user,
    renderer=DataclassRenderer(),
    read=views.name + views.address.city,
    update=views.name + views.address.city,
    create=views.name + views.address.city + views.address.zip,
)

dataclass_update = DataclassUserAPI.update(address={"city": "Paris"})
assert is_dataclass(DataclassUserAPI.update_model)
assert dataclass_update.name is UNSET


def main() -> None:
    parser = ArgumentParser()
    parser.add_argument("--generate-stub", action="store_true")
    args = parser.parse_args()

    if args.generate_stub:
        generate_views_pyi("examples.models", [build_entity(model) for model in MODELS])


if __name__ == "__main__":
    main()
