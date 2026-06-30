from dataclasses import is_dataclass
from pathlib import Path
import importlib.util
import sys

from . import (
    DataclassRenderer,
    PydanticRenderer,
    UNSET,
    api,
    build_entity,
    generate_views_pyi,
    views_for,
)


def run_example() -> None:
    models_module = _load_example_models()
    Address = models_module.Address
    Profile = models_module.Profile
    User = models_module.User

    # End-to-end consumer flow:
    # 1. build the schema IR
    # 2. derive views
    # 3. generate a matching .pyi for type checkers
    # 4. build operation-specific API models
    user = build_entity(User)
    views = views_for(User)

    user_api = api(
        user,
        renderer=PydanticRenderer(),
        read=views.name + views.address.city,
        update=views.name,
        create=views.name + views.address.city + views.address.zip,
    )

    instance = user_api.create(name="Sam", address={"city": "Paris", "zip": "75001"})
    update = user_api.update(name=None)

    dataclass_user_api = api(
        user,
        renderer=DataclassRenderer(),
        read=views.name + views.address.city,
        update=views.name + views.address.city,
        create=views.name + views.address.city + views.address.zip,
    )

    dataclass_update = dataclass_user_api.update(address={"city": "Paris"})

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

def generate_example_stubs() -> None:
    models_module = _load_example_models()
    Address = models_module.Address
    Profile = models_module.Profile
    User = models_module.User

    generate_views_pyi("examples.models", [build_entity(model) for model in (Address, Profile, User)])



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
