# Projector

Derive fully typed operation-specific python models from existing domain models; declaratively specify the properties you want and eliminate model explosion.

## Example

```python
import sqlite3
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
    create=views.name + views.address.city + views.address.zip,
    read=views.name + views.address.city,
    update=views.name,
)


# Use the derived user models:
conn = sqlite3.connect(":memory:")
conn.execute("create table users (name text, city text, zip text)")

def add_user_to_db(user: UserAPI.create_model) -> None:
    conn.execute(
        "insert into users (name, city, zip) values (?, ?, ?)",
        (user.name, user.address.city, user.address.zip),
    )
    conn.commit()


new_user = UserAPI.create(name="Sam", address={"city": "Paris", "zip": "75001"})
add_user_to_db(new_user)
```

## More Info

`create`, `read`, and `update` are just example names. Use whatever output names
fit your application.

For example:

```python
UserAPI = api(
    user,
    renderer=renderer.Pydantic,
    create_user_command=views.name + views.address.city + views.address.zip,
    read=views.name + views.address.city,
    update_name_command=views.name,
)
```

That gives you:

- `UserAPI.create_user_command_model`
- `UserAPI.read_model`
- `UserAPI.update_name_command_model`

And factories that instantiate those models:

- `UserAPI.create_user_command(...)`
- `UserAPI.read(...)`
- `UserAPI.update_name_command(...)`

If a source model field can be `None`, you can still decide whether a specific
output must require it or keep it optional:

```python
UserAPI = api(
    user,
    renderer=renderer.Pydantic,
    create=required(views.address.city),
    read=optional(views.address.city),
)
```

`required(...)` applies to the whole selected subtree. `optional(...)` keeps
that subtree nullable in the generated output.

## Supported input and output types

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
user models (dataclasses, pydantic, attrs, plain classes) -> entity/projection IR -> generated output models (pydantic, dataclasses, attrs)
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
