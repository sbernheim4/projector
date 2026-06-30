# Projector

`Projector` is a small prototype for deriving operation-specific API models
from a single domain model.

The core idea is to avoid hand-writing separate `Create`, `Read`, and `Update`
models for every domain object. Instead, the user declares which fields belong
to each operation, and the library generates concrete model classes that can be
used as FastAPI request or response types.

## What It Does

- accepts dataclass domain models as input
- builds a small intermediate representation of the schema
- lets you declaratively select fields for each operation
- generates Pydantic or dataclass output models
- supports partial update models with unset-vs-`None` semantics
- provides factory functions that instantiate the generated models
- can generate `.pyi` stubs for a consumer’s model module

## Why This Exists

Python API projects often start with one domain model and quickly grow several
similar shapes around it:

- a create model for fields accepted when inserting a new object
- an update model for fields accepted when changing an existing object
- a read model for fields returned from the API
- sometimes additional public, private, admin, or partial variants

That model explosion becomes noisy because most variants are not conceptually
new domain objects. They are views over the same object with different allowed
fields and validation/output targets.

This project experiments with expressing those views declaratively:

```python
UserAPI = api(
    user,
    renderer=PydanticRenderer(),
    read=views.name + views.address.city,
    update=views.name,
    create=views.name + views.address.city + views.address.zip,
)
```

From that declaration, the library creates:

- `UserAPI.create_model`
- `UserAPI.read_model`
- `UserAPI.update_model`

Each generated model is a real class and can be passed to tools such as FastAPI.

## Example

The `examples/` directory is a fully isolated consumer-style example.

It shows:

1. defining domain models
2. building the schema IR
3. building typed field selectors
4. generating a matching `.pyi` file for type checkers
5. generating operation-specific API models
6. instantiating the generated models

Run it from the repo root:

```bash
PYTHONPATH=src uv run python -m examples.example
```

Regenerate the demo stub:

```bash
PYTHONPATH=src uv run python -m examples.example --generate-stub
```

Or use the repo helper commands:

```bash
just example
just stubs
just test
```

## Current Architecture

The library is split into small internal modules:

### `app.ir`

Schema introspection and the entity IR.

- `Entity` represents a structured object.
- `Field` represents a leaf field and stores the field type.
- `build_entity()` inspects supported source models and builds the IR.

### `app.projection`

Typed field selectors and projection compilation.

- `views_for()` returns a tree of selectable fields.
- `Leaf` supports declarative selection with `+`.
- `compile_projection()` converts selected paths into a nested spec.

### `app.renderers`

Output-target renderers.

- `PydanticRenderer` builds Pydantic models.
- `DataclassRenderer` builds dataclass models.

### `app.encode`

Public orchestration helpers.

- `api()` composes entity, projection, and renderer into operation-specific models.
- `build_model_and_factory()` wires a generated class to a factory function.

### `app.stubgen`

Stub generation helpers.

- `generate_views_pyi()` writes a matching `.pyi` file for a consumer module.

## Example Layout

```text
examples/models.py    Demo dataclass domain models
examples/models.pyi   Generated type stub for the demo consumer module
examples/example.py   Runnable end-to-end example
```

## What Works Today

- dataclass input models
- nested declarative projections
- generated Pydantic output models
- generated dataclass output models
- partial update models with unset-vs-`None` semantics
- generated factories for both renderer styles
- consumer-owned stub generation

