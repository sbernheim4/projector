# Projector

Eliminate model explosion by deriving fully typed, operation-specific Python models from existing domain models by declaratively specifying the properties you want.

Domain models (input) can be written using: dataclasses, Pydantic models, TypedDict classes, attrs classes, and plain annotated classes.

Output can be: Pydantic models, dataclass models, attrs classes, or TypedDict classes.


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


# Derive operation-specific models.
user = build_entity(User)
views = views_for(User)
UserAPI = api(
    user,
    renderer=renderer.Pydantic,
    Create=required(views.name) + optional(views.address.city + views.address.zip),
    Read=optional(views.name) + optional(views.address.city),
    Update=views.name,
)


# Use the derived user models. Types have `Model` (or `_model` if using
# snake_case) appended to the end of the keyword argument:
conn = sqlite3.connect(":memory:")
conn.execute("create table users (name text, city text, zip text)")

def add_user_to_db(user: UserAPI.CreateModel) -> None:
    conn.execute(
        "insert into users (name, city, zip) values (?, ?, ?)",
        (user.name, user.address.city, user.address.zip),
    )
    conn.commit()


# Create an instance with the exact keyword argument provided
new_user = UserAPI.Create(name="John", address={"city": "Paris", "zip": "75001"})
add_user_to_db(new_user)
```

## More Info

`Create`, `Read`, and `Update` aboe are arbitrary. Use whatever names fit your
application.

For example:

```python
UserAPI = api(
    user,
    renderer=renderer.Pydantic,
    CreateUserCommand=views.name + views.address.city + views.address.zip,
    Read=views.name + views.address.city,
    UpdateNameCommand=views.name,
)
```

That gives you:

- `UserAPI.CreateUserCommandModel`
- `UserAPI.ReadModel`
- `UserAPI.UpdateNameCommandModel`

And factories that instantiate those models:

- `UserAPI.CreateUserCommand(...)`
- `UserAPI.Read(...)`
- `UserAPI.UpdateNameCommand(...)`

If a source model field can be `None`, you can still decide whether a specific
output must require it or keep it optional:

```python
UserAPI = api(
    user,
    renderer=renderer.Pydantic,
    Create=required(views.address.city),
    Read=optional(views.address.city),
)
```

`required(...)` applies to the whole selected subtree. `optional(...)` keeps
that subtree nullable in the generated output.

Snake_case output names are still supported too. If you use `create` or
`create_user_command`, the generated accessors stay snake_case:

- `UserAPI.create`
- `UserAPI.create_model`
- `UserAPI.create_user_command`
- `UserAPI.create_user_command_model`

## Supported input and output types

Input:
- dataclasses
- Pydantic models
- plain annotated classes
- attrs classes
- `TypedDict` classes

Output:
- Pydantic models
- dataclass models
- attrs classes
- `TypedDict` classes

The flow is:

```text
user models (dataclasses, pydantic, attrs, typed dicts, plain classes) -> entity/projection IR -> generated output models (pydantic, dataclasses, attrs, typed dicts)
```

Declaratively specify which fields belong in each output model. `Projector`
builds the classes.

## What It Does

- reads user-land model classes into a schema IR
- lets you select fields with a typed projection DSL
- compiles projections into nested specs
- renders Pydantic or dataclass output models
- renders attrs output models
- renders `TypedDict` output models
- lets you name each generated model however you want
- supports partial update semantics with unset-vs-`None`
- provides factory functions for the generated classes
- can generate `.pyi` stubs for consumer model modules

## Example Layout

The `examples/` directory is a fully isolated consumer example.

```text
examples/demo_example/               Demo domain models and runnable example
examples/fast_api_example/users/     User domain package
examples/fast_api_example/projects/  Project domain package
examples/fast_api_example/http/      FastAPI transport layer
```

Run the demo example:

```bash
PYTHONPATH=src uv run python -m examples.demo_example.main
```

Run the FastAPI example:

```bash
PYTHONPATH=src .venv/bin/python -m examples.fast_api_example.http.main
```

Helpful `just` commands

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
- `TypedDictRenderer`
- `renderer.Pydantic`
- `renderer.Dataclass`
- `renderer.Attrs`
- `renderer.TypedDict`

### `app.encode`

Public orchestration helpers.

- `api()` builds operation-specific factories
- `build_model_and_factory()` wires renderer output to factories

### `app.stubgen`

Stub generation helpers.

- `generate_views_pyi()` writes a `.pyi` file next to a consumer model module

## What Works Today

- dataclass, Pydantic, attrs, and plain-annotated input models
- `TypedDict` input models
- nested projections
- generated Pydantic output models
- generated dataclass output models
- generated attrs output models
- generated `TypedDict` output models
- partial updates with unset-vs-`None`
- generated factories
- consumer-owned stub generation
