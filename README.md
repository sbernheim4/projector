# Projector

Eliminate model explosion by deriving fully typed, operation-specific Python
models from existing domain models by declaratively specifying the properties
you want.

Instead of maintaining separate `CreateUser`, `ReadUser`, `UpdateUser`, request
and response models by hand (or equivalent command models for RPC-style APIs),
you describe the fields each operation needs and Projector builds the output
models at runtime.

```text
domain models -> typed field projection -> generated operation models
```

Projector is useful when your API, command, or service boundary needs many
model variants that mostly differ by selected fields, requiredness, or output
target.

## Installation

```bash
pip install model-projector
```

The PyPI distribution is named `model-projector`. The Python import package is
named `projector`:

```python
from projector import project, renderer, views_for
```

Projector requires Python 3.12 or newer.

## Quickstart

```python
from dataclasses import dataclass

from projector import project, optional, renderer, required, views_for


@dataclass(kw_only=True)
class Address:
    city: str
    zip: str


@dataclass(kw_only=True)
class User:
    name: str
    email: str
    address: Address


views = views_for(User)

UserModels = project(
    User,
    renderer=renderer.Pydantic,
    Create=(
        required(views.name + views.email)
        + optional(views.address.city + views.address.zip)
    ),
    Read=views.name + views.email + views.address.city,
    Update=views.name,
)

UserCreate = UserModels.CreateModel
UserRead = UserModels.ReadModel

created = UserModels.Create(
    name="Sam",
    email="sam@example.com",
    address={"city": "Paris", "zip": "75001"},
)
read = UserModels.Read(name="Sam", email="sam@example.com", address={"city": "Paris"})
```

The output namespace contains generated model classes and matching factory
functions:

```python
UserModels.CreateModel
UserModels.ReadModel
UserModels.UpdateModel

UserModels.Create(...)
UserModels.Read(...)
UserModels.Update(...)
```

The names `Create`, `Read`, and `Update` are conventions only. You can use
operation names that match your application:

```python
UserCommands = project(
    User,
    renderer=renderer.Pydantic,
    RegisterUser=views.name + views.email,
    RenameUser=views.name,
)
```

Snake-case names are supported too:

```python
UserModels = project(User, renderer=renderer.Pydantic, create_user=views.name)

UserModels.create_user(...)
UserModels.create_user_model
```

## At a Glance

- Generate operation-specific models from existing domain models.
- Keep runtime model derivation in Python; no generated source files are needed
  to run your application.
- Generate optional `.pyi` files so type checkers and LSPs like ty and pyrefly
  and understand dynamic field selectors.
- Projector can ingest models written using dataclasses, Pydantic models, attrs
  classes, `TypedDict` classes, and plain annotated classes.
- Projector can output: Pydantic, dataclass, attrs, or `TypedDict` models.


## Core Concepts

`views_for(Model)` returns a typed selector tree for a source model. Selectors
can be composed with `+` to describe the fields included in each output model.

`project(Model, renderer=..., **views)` compiles the selected fields and returns
a namespace containing generated model classes and factory functions.

`required(...)` and `optional(...)` override nullability for a selected subtree.
This lets a nullable source field be required in one operation and optional in
another.

`Update` is currently special-cased as a partial update model. Other output
names are treated as full models.

`build_entity(Model)` is the lower-level schema IR helper. Most users should
call `project(...)` with the source model class directly.

## Supported Models

Projector can read these source model shapes:

- dataclasses
- Pydantic models
- attrs classes
- `TypedDict` classes
- plain annotated classes

Projector can generate these output model shapes:

- Pydantic models
- dataclass models
- attrs classes
- `TypedDict` classes

Choose the output target with a renderer:

```python
from projector import renderer

renderer.Pydantic
renderer.Dataclass
renderer.Attrs
renderer.TypedDict
```

Renderer classes are also exported directly:

```python
from projector import PydanticRenderer, DataclassRenderer
```

## Public API

Most users only need:

```python
from projector import project, renderer, views_for
```

Additional helpers are exported for requiredness, direct renderer classes, stub
generation, and lower-level schema inspection:

```python
from projector import (
    AttrsRenderer,
    DataclassRenderer,
    PydanticRenderer,
    TypedDictRenderer,
    UNSET,
    build_entity,
    generate_views_pyi,
    optional,
    required,
)
```

## Type Checking

Projector derives models dynamically at runtime. Runtime use does not require
generated files.

Static type checkers and LSPs need one extra step for dynamic `views_for(...)`
attributes. Generate sibling `.pyi` files with:

```bash
projector type-stubs path/to/models.py path/to/other_models.py
```

Example:

```text
app/models.py -> app/models.pyi
```

Run this command after changing source model definitions. The generated stubs
are for type checkers and language servers; they are not imported at runtime.

## Examples

The repository includes two isolated examples:

```text
examples/demo_example/        Small end-to-end demo
examples/fast_api_example/    FastAPI CRUD and command-style demo
```

From a checkout of this repository:

```bash
just demo-example
just fast-api-example
```

## Development

Useful common commands:

```bash
just test
just check
just stubs
just demo-example
just fast-api-example
```

`just check` runs Ruff, ty, and pyrefly.

## Contributing

Issues and pull requests are welcome. Before opening a change, run:

```bash
just test
just check
```

If you change example model definitions, regenerate their type stubs:

```bash
just stubs
```

## Releasing

Releases are published to PyPI as `model-projector` by GitHub Actions using PyPI
Trusted Publishing. No PyPI API token is stored in the repository.

For maintainers, create a patch, minor, or major release with:

```bash
just bump patch
just bump minor
just bump major
```

The `bump` recipe updates the version with `uv version`, runs tests and checks,
pushes `main`, creates a matching `vX.Y.Z` tag, and pushes the tag. The tag
triggers the PyPI publishing workflow.

Manual workflow runs publish to TestPyPI only.

## License

Projector is distributed under the MIT License. See [LICENSE](LICENSE).
