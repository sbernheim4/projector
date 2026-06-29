from dataclasses import is_dataclass, fields as dc_fields
from collections.abc import Callable
from typing import Any, Generic, TypeVar, cast, get_type_hints
from pydantic import BaseModel, create_model


# =========================================================
# 1. ENTITY IR
# =========================================================


class Field:
    def __init__(self, type_):
        self.type_ = type_

    def __repr__(self):
        return f"Field({self.type_.__name__})"


class Entity:
    def __init__(self, name, fields):
        self.name = name
        self.fields = fields


PydanticFieldDefs = dict[str, tuple[Any, Any]]
T = TypeVar("T")


def create_pydantic_model(name: str, fields: PydanticFieldDefs) -> type[BaseModel]:
    typed_create_model = cast(Callable[..., type[BaseModel]], create_model)
    return typed_create_model(name, **fields)


def build_entity(cls):
    if not is_dataclass(cls):
        raise TypeError("Must be a dataclass")

    hints = get_type_hints(cls)
    schema: dict[str, Entity | Field] = {}

    for f in dc_fields(cls):
        tp = hints[f.name]

        if is_dataclass(tp):
            schema[f.name] = build_entity(tp)
        else:
            schema[f.name] = Field(tp)

    return Entity(cls.__name__, schema)


# =========================================================
# 2. VIEW LAYER
# =========================================================


class Leaf(Generic[T]):
    def __init__(self, path):
        self.path = path

    def __add__(self, other):
        return to_projection(self) + to_projection(other)

    def __repr__(self):
        return ".".join(self.path)


class ViewNode:
    def __init__(self, entity, path=None):
        self._entity = entity
        self._path = path or []

        for name, field in entity.fields.items():
            if isinstance(field, Entity):
                setattr(self, name, ViewNode(field, self._path + [name]))
            else:
                setattr(self, name, Leaf(self._path + [name]))

    def __getattr__(self, name) -> Any:
        return Leaf([name])


def build_views(entity):
    return ViewNode(entity)


# =========================================================
# 3. PROJECTION
# =========================================================


class Projection:
    def __init__(self, paths=None):
        self.paths = paths or []

    def __add__(self, other):
        other = to_projection(other)
        return Projection(self.paths + other.paths)


def to_projection(x):
    if isinstance(x, Projection):
        return x

    if isinstance(x, Leaf):
        return Projection([x.path])

    raise TypeError(f"Cannot convert {type(x)} to Projection")


def compile_projection(projection):
    projection = to_projection(projection)  # ⭐ CRITICAL FIX

    spec = {}

    for path in projection.paths:
        cursor = spec
        for part in path[:-1]:
            cursor = cursor.setdefault(part, {})
        cursor[path[-1]] = True

    return spec


# =========================================================
# 4. RENDERER
# =========================================================


class PydanticRenderer:
    def render(self, entity, spec, name: str) -> type[BaseModel]:
        fields = self._build_fields(spec, entity, name)
        return create_pydantic_model(name, fields)

    def _build_fields(self, spec, entity, name) -> PydanticFieldDefs:
        fields: PydanticFieldDefs = {}

        for key, sub_spec in spec.items():
            node = entity.fields[key]

            if isinstance(node, Field):
                fields[key] = (node.type_, ...)

            else:
                nested = self._build_fields(sub_spec, node, f"{name}_{key}")
                nested_model = create_pydantic_model(f"{name}_{key}", nested)
                fields[key] = (nested_model, ...)

        return fields


# =========================================================
# 5. FACTORY BUILDER (CORE FIX)
# =========================================================


def build_model_and_factory(entity, renderer, projection, name):
    spec = compile_projection(projection)

    model_cls = renderer.render(entity, spec, name=name)

    def factory(**kwargs):
        return model_cls(**kwargs)

    setattr(factory, "model", model_cls)  # expose model for typing

    return model_cls, factory


# =========================================================
# 6. API LAYER
# =========================================================


class EntityAPI:
    entity: Any

    renderer: Any

    create: Any
    create_model: Any

    write: Any
    write_model: Any

    read: Any
    read_model: Any


def api(entity, renderer, read=None, write=None, create=None):
    api_obj = EntityAPI()

    def build(name, projection):
        model_cls, factory = build_model_and_factory(
            entity,
            renderer,
            projection,
            name,
        )
        return model_cls, factory

    if create is not None:
        model_cls, factory = build(f"{entity.name}Create", create)
        api_obj.create_model = model_cls
        api_obj.create = factory

    if read is not None:
        model_cls, factory = build(f"{entity.name}Read", read)
        api_obj.read_model = model_cls
        api_obj.read = factory

    if write is not None:
        model_cls, factory = build(f"{entity.name}Write", write)
        api_obj.write_model = model_cls
        api_obj.write = factory

    api_obj.entity = entity
    api_obj.renderer = renderer

    return api_obj
