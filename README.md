# Projector

Eliminate model explosion by deriving fully typed, operation-specific Python models from existing domain models by declaratively specifying the properties you want.

Your application domain models (the input to projector) can be written using: dataclasses, Pydantic models, TypedDict classes, attrs classes, and plain annotated classes.

Projector can output the derived models in: Pydantic, dataclass, attrs, or TypedDict.

## Installation

```bash
pip install model-projector
```

The distribution name is `model-projector`, and the import package is
`projector`:

```python
from projector import project, renderer, views_for
```

## Example

```python
import sqlite3
from dataclasses import dataclass

from projector import project, optional, renderer, required, views_for


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
views = views_for(User)
UserModels = project(
    User,
    renderer=renderer.Pydantic,
    Create=required(views.name) + optional(views.address.city + views.address.zip),
    Read=optional(views.name) + optional(views.address.city),
    Update=views.name,
)
UserCreate = UserModels.CreateModel


# Use the derived user models.
conn = sqlite3.connect(":memory:")
conn.execute("create table users (name text, city text, zip text)")

def add_user_to_db(user: UserCreate) -> None:
    conn.execute(
        "insert into users (name, city, zip) values (?, ?, ?)",
        (user.name, user.address.city, user.address.zip),
    )
    conn.commit()


# Create an instance with the exact keyword argument provided
new_user = UserModels.Create(name="John", address={"city": "Paris", "zip": "75001"})
add_user_to_db(new_user)
```

## More Info

`Create`, `Read`, and `Update` above are arbitrary. Use whatever names fit your
application.

For example:

```python
UserModels = project(
    User,
    renderer=renderer.Pydantic,
    CreateUserCommand=views.name + views.address.city + views.address.zip,
    Read=views.name + views.address.city,
    UpdateNameCommand=views.name,
)
```

That gives you:

- `UserModels.CreateUserCommandModel`
- `UserModels.ReadModel`
- `UserModels.UpdateNameCommandModel`

And functions to instantiate instances:

- `UserModels.CreateUserCommand(...)`
- `UserModels.Read(...)`
- `UserModels.UpdateNameCommand(...)`

If a source model field can be `None`, you can still decide whether a specific
output must require it or keep it optional:

```python
UserModels = project(
    User,
    renderer=renderer.Pydantic,
    Create=required(views.address.city),
    Read=optional(views.address.city),
)
```

`required(...)` applies to the whole selected subtree. `optional(...)` keeps
that subtree nullable in the generated output.

`snake_case` output names are supported too. If you use `create` or
`create_user_command`, the generated accessors stay snake_case:

- `UserModels.create`
- `UserModels.create_model`
- `UserModels.create_user_command`
- `UserModels.create_user_command_model`

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

## Core Concepts

`project(...)` is the main runtime entry point. It takes a source model class,
selected fields, and a renderer, then returns a namespace containing generated
model classes and factory functions.

`views_for(...)` creates typed selectors for a source model. Use these selectors
to describe which fields belong in each generated output model.

`projector type-stubs` is the type-checker build step. It writes sibling `.pyi`
files so LSPs and type checkers can understand dynamic `views_for(...)`
attributes. These files are not executed at runtime.

`build_entity(...)` is the lower-level IR helper. Normal users should not need
it for `project(...)`, but it remains public for debugging, tests, and tooling
that wants to inspect the derived schema.

## Type Checking Build Step

Projector currently derives models dynamically at runtime. Runtime use does not
require generated files, but static type checkers like ty and pyrefly need
`.pyi` files to understand the dynamic view objects returned by
`views_for(...)`.

Generate those type checker stubs with the CLI:

```bash
projector type-stubs path/to/models.py path/to/other_models.py
```

The command accepts one or more Python file paths and writes sibling `.pyi`
files:

```text
examples/demo_example/models.py -> examples/demo_example/models.pyi
```

## Example Layout

The `examples/` directory contains fully isolated consumer examples.

```text
examples/demo_example/        Demo domain models and runnable example
examples/fast_api_example/    An example with a FastAPI HTTP server with CRUD and command style generated models
```

Run the demo example:

```bash
just demo-example
# or
PYTHONPATH=src uv run python -m examples.demo_example.main
```

Run the FastAPI example:

```bash
just fast-api-example
# or
PYTHONPATH=src .venv/bin/python -m examples.fast_api_example.http.main
```

Helpful `just` commands

```bash
just test
just check
just stubs
just demo-example
just fast-api-example
```

## Publishing

Projector is configured as a Python package in `pyproject.toml`. The package
uses the `model-projector` distribution name because `projector` is already
taken on PyPI.

Build the source distribution and wheel:

```bash
uv build
# or
python -m build
```

Validate the built package metadata:

```bash
python -m twine check dist/*
```

Upload to TestPyPI first:

```bash
python -m twine upload --repository testpypi dist/*
```

Install-test from TestPyPI:

```bash
python -m pip install \
  --index-url https://test.pypi.org/simple/ \
  --extra-index-url https://pypi.org/simple/ \
  model-projector
```

Upload the same distributions to PyPI after the TestPyPI package installs and
imports correctly:

```bash
python -m twine upload dist/*
```

PyPI and TestPyPI require separate accounts and API tokens.

## Library Structure

### `projector.ir`

Builds the schema IR from user models.

- `Entity` is a structured schema node
- `Field` is a primitive leaf node
- `build_entity()` introspects supported input models into the lower-level IR

### `projector.projection`

Builds and compiles typed projections.

- `views_for()` returns a tree of selectable fields
- `Leaf` supports `+` composition
- `compile_projection()` turns selections into nested specs

### `projector.renderers`

Turns the IR/spec into concrete output classes.

- `PydanticRenderer`
- `DataclassRenderer`
- `AttrsRenderer`
- `TypedDictRenderer`
- `renderer.Pydantic`
- `renderer.Dataclass`
- `renderer.Attrs`
- `renderer.TypedDict`

### `projector.encode`

Public orchestration helpers.

- `project()` takes a source model class and builds operation-specific factories
- `build_model_and_factory()` wires renderer output to factories

### `projector.stubgen`

Stub generation helpers.

- `generate_views_pyi()` writes a `.pyi` file next to a consumer model module
