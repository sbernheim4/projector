from argparse import ArgumentParser
from dataclasses import is_dataclass
from pathlib import Path
import importlib.util
import sys

import attrs

from app import (
    UNSET,
    api,
    build_entity,
    generate_views_pyi,
    optional,
    renderer,
    required,
    views_for,
)


def run_example() -> None:
    models_module = _load_example_models()
    Address = models_module.Address
    Profile = models_module.Profile
    User = models_module.User

    # Step 1: build the schema IR from the user's domain models.
    user = build_entity(User)

    # Step 2: build typed field selectors for declarative projections.
    views = views_for(User)

    # Step 3: generate Pydantic models for create/read/update operations.
    user_api = api(
        user,
        renderer=renderer.Pydantic,
        read=views.name + views.address.city,
        update=views.name,
        create=views.name + views.address.city + views.address.zip,
    )

    # Step 4: instantiate the generated Pydantic models through the factories.
    instance = user_api.create(name="Sam", address={"city": "Paris", "zip": "75001"})
    update = user_api.update(name=None)

    # Step 5: generate dataclass models for the same projections.
    dataclass_user_api = api(
        user,
        renderer=renderer.Dataclass,
        read=views.name + views.address.city,
        update=views.name + views.address.city,
        create=views.name + views.address.city + views.address.zip,
    )

    # Step 6: show the dataclass update factory preserving unset-vs-None semantics.
    dataclass_update = dataclass_user_api.update(address={"city": "Paris"})

    # Step 7: generate attrs models for the same projections.
    attrs_user_api = api(
        user,
        renderer=renderer.Attrs,
        read=views.name + views.address.city,
        update=views.name + views.address.city,
        create=views.name + views.address.city + views.address.zip,
    )

    # Step 8: instantiate the generated attrs models through the factories.
    attrs_create = attrs_user_api.create(
        name="Sam",
        address={"city": "Paris", "zip": "75001"},
    )
    attrs_update = attrs_user_api.update(address={"city": "Paris"})

    @dataclass(kw_only=True)
    class NullableUser:
        address: Address | None

    nullable_user = build_entity(NullableUser)
    nullable_views = views_for(NullableUser)

    # Step 9: show required/optional selectors on a nullable subtree.
    required_user_api = api(
        nullable_user,
        renderer=renderer.Pydantic,
        create=required(nullable_views.address.city),
    )
    optional_user_api = api(
        nullable_user,
        renderer=renderer.Pydantic,
        create=optional(nullable_views.address.city),
    )
    required_address = required_user_api.create(address={"city": "Paris"})
    optional_address = optional_user_api.create(address=None)

    print("Pydantic API")
    print("  create model:", user_api.create_model)
    print("  read model:", user_api.read_model)
    print("  update model:", user_api.update_model)
    print("  create instance:", instance)
    print("  update instance:", update)
    print("  update fields set:", update.model_fields_set)

    print("Dataclass API")
    print("  create model:", dataclass_user_api.create_model)
    print("  read model:", dataclass_user_api.read_model)
    print("  update model:", dataclass_user_api.update_model)
    print("  update instance:", dataclass_update)
    print("  update model is dataclass:", is_dataclass(dataclass_user_api.update_model))
    print("  omitted name is UNSET:", dataclass_update.name is UNSET)

    print("Attrs API")
    print("  create model:", attrs_user_api.create_model)
    print("  read model:", attrs_user_api.read_model)
    print("  update model:", attrs_user_api.update_model)
    print("  create instance:", attrs_create)
    print("  update instance:", attrs_update)
    print("  update model is attrs:", attrs.has(attrs_user_api.update_model))

    print("Required/Optional API")
    print("  required model:", required_user_api.create_model)
    print("  optional model:", optional_user_api.create_model)
    print("  required instance:", required_address)
    print("  optional instance:", optional_address)

    nullable_api = api(
        nullable_user,
        renderer=renderer.Pydantic,
        create=optional(nullable_views.address.city),
    )
    nullable_instance = nullable_api.create(address=None)

    print("Nullable API")
    print("  create model:", nullable_api.create_model)
    print("  create instance:", nullable_instance)


def generate_example_stubs() -> None:
    models_module = _load_example_models()
    Address = models_module.Address
    Profile = models_module.Profile
    User = models_module.User

    generate_views_pyi(
        "examples.models",
        [build_entity(model) for model in (Address, Profile, User)],
    )


def _load_example_models():
    module_name = "examples.models"
    if module_name in sys.modules:
        return sys.modules[module_name]

    path = Path.cwd() / "examples" / "models.py"
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load example models from {path}")

    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def main() -> None:
    parser = ArgumentParser()
    parser.add_argument("--generate-stub", action="store_true")
    args = parser.parse_args()

    if args.generate_stub:
        generate_example_stubs()
    else:
        run_example()


if __name__ == "__main__":
    main()
