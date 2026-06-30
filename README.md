# Projector

Derive operation-specific python models from existing domain models; declaratively specify the properties you want and eliminate model explosion.

## Example

```python
from dataclasses import dataclass

from app import api, build_entity, renderer, views_for


# Application specific domain models:
@dataclass(kw_only=True)
class Address:
    city: str
    zip: str


@dataclass(kw_only=True)
class User:
    name: str
    address: Address


# Derive operation specific models
user = build_entity(User)
views = views_for(User)

UserAPI = api(
    user,
    renderer=renderer.Pydantic,
    Create=views.name + views.address.city + views.address.zip,
    Read=views.name + views.address.city,
    Update=views.name,
)


def parse_user_input(user: dict):
    new_user = UserAPI.create(name="Sam", address={"city": "Paris", "zip": "75001"})
    return new_user

def add_user_to_db(user: UserAPI.create_model):
    db.INSERT_INTO('users.user').VALUES(user)
```

`Create`, `Read`, and `Update` are just conventions. Use any output names you
want.

That gives you:

- `UserAPI.Create_model`
- `UserAPI.Read_model`
- `UserAPI.Update_model`

And factories that instantiate those models:

- `UserAPI.Create(...)`
- `UserAPI.Read(...)`
- `UserAPI.Update(...)`

Input:
- dataclasses
- Pydantic models
- plain annotated classes
- attrs classes

Output:
- Pydantic models
- dataclass models
- attrs classes

The flow is:

```text
user models -> entity/projection IR -> generated output models
```

Declaratively specify which fields belong in each output model. `Projector`
builds the classes.
## What It Does

- reads user-land model classes into a schema IR
- lets you select fields with a typed projection DSL
- compiles projections into nested specs
- renders Pydantic or dataclass output models
- renders attrs output models
- lets you name each generated model however you want
- supports partial update semantics with unset-vs-`None`
- provides factory functions for the generated classes
- can generate `.pyi` stubs for consumer model modules

## Example Layout

The `examples/` directory is a fully isolated consumer example.

```text
examples/models.py    Demo domain models
examples/models.pyi   Generated stub for the demo models
examples/example.py   Runnable end-to-end example
```

Run it:

```bash
PYTHONPATH=src uv run python -m examples.example
```

Regenerate the stub:

```bash
PYTHONPATH=src uv run python -m examples.example --generate-stub
```

Or use the repo helpers:

```bash
just example
just stubs
just test
just check
```

## Library Structure

### `app.ir`

Builds the schema IR from user models.

- `Entity` is a structured schema node
- `Field` is a primitive leaf node
- `build_entity()` introspects supported input models

### `app.projection`

Builds and compiles typed projections.

- `views_for()` returns a tree of selectable fields
- `Leaf` supports `+` composition
- `compile_projection()` turns selections into nested specs

### `app.renderers`

Turns the IR/spec into concrete output classes.

- `PydanticRenderer`
- `DataclassRenderer`
- `AttrsRenderer`
- `renderer.Pydantic`
- `renderer.Dataclass`
- `renderer.Attrs`

### `app.encode`

Public orchestration helpers.

- `api()` builds operation-specific factories
- `build_model_and_factory()` wires renderer output to factories

### `app.stubgen`

Stub generation helpers.

- `generate_views_pyi()` writes a `.pyi` file next to a consumer model module

## What Works Today

- dataclass, Pydantic, attrs, and plain-annotated input models
- nested projections
- generated Pydantic output models
- generated dataclass output models
- generated attrs output models
- partial updates with unset-vs-`None`
- generated factories
- consumer-owned stub generation
