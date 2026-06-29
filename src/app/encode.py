from dataclasses import (
    is_dataclass,
    fields as dc_fields,
    make_dataclass as dc_make_dataclass,
)
from typing import Any, get_type_hints
from pydantic import create_model


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

    def __repr__(self):
        return f"Entity({self.name})"


def build_entity(cls):
    """
    Convert dataclass -> Entity IR
    """
    if not is_dataclass(cls):
        raise TypeError(f"{cls.__name__} must be a dataclass")

    hints = get_type_hints(cls)
    schema = {}

    for f in dc_fields(cls):
        tp = hints[f.name]

        if is_dataclass(tp):
            schema[f.name] = build_entity(tp)
        else:
            schema[f.name] = Field(tp)

    return Entity(cls.__name__, schema)


# =========================================================
# 2. VIEW LAYER (DSL)
# =========================================================


class Leaf:
    def __init__(self, path):
        self.path = path

    def to_projection(self):
        return Projection([self.path])

    def __add__(self, other):
        return self.to_projection() + to_projection(other)

    def __repr__(self):
        return ".".join(self.path)


class ViewNode:
    def __init__(self, entity, path=None):
        self._entity = entity
        self._path = path or []

        for name, field in entity.fields.items():
            if isinstance(field, Entity):
                setattr(
                    self,
                    name,
                    ViewNode(field, self._path + [name]),
                )
            else:
                setattr(
                    self,
                    name,
                    Leaf(self._path + [name]),
                )


    def __getattr__(self, name: str) -> Any:
        return Leaf([name])

    def __dir__(self):
        return list(self._entity.fields.keys())

def build_views(entity):
    return ViewNode(entity)


# =========================================================
# 3. PROJECTION AST (SINGLE CANONICAL REPRESENTATION)
# =========================================================


class Projection:
    def __init__(self, paths=None):
        self.paths = paths or []  # list[list[str]]

    def __repr__(self):
        return f"Projection({self.paths})"

    def __add__(self, other):
        other = to_projection(other)
        return Projection(self.paths + other.paths)


def compile_projection(projection: Projection):
    """
    [["address","city"], ["name"]]
    → {"address":{"city":True}, "name":True}
    """
    if projection is None:
        return None

    spec = {}

    for path in projection.paths:
        cursor = spec
        for part in path[:-1]:
            cursor = cursor.setdefault(part, {})
        cursor[path[-1]] = True

    return spec


# =========================================================
# 4. RENDERERS (UNIFIED INTERFACE)
# =========================================================


class DictRenderer:
    def render(self, entity, spec):
        return spec


class DataclassRenderer:
    def render(self, entity, spec, name: str):
        return dc_make_dataclass(name, self._build(spec))

    def _build(self, spec):
        fields = []
        for k, v in spec.items():
            if isinstance(v, dict):
                fields.append((k, self._build(v)))
            else:
                fields.append((k, Any))
        return fields


class PydanticRenderer:
    def render(self, entity, spec, name: str):
        fields = self._build_fields(spec, entity, name)
        return create_model(name, **fields)

    def _build_fields(self, spec, entity, name):
        fields = {}

        for key, sub_spec in spec.items():
            node = entity.fields[key]

            if isinstance(node, Field):
                fields[key] = (node.type_, ...)

            else:
                nested_fields = self._build_fields(sub_spec, node, f"{name}_{key}")
                nested_model = create_model(f"{name}_{key}", **nested_fields)
                fields[key] = (nested_model, ...)

        return fields


# =========================================================
# 5. API LAYER
# =========================================================


class EntityAPI:
    def __init__(self, entity, renderer, read=None, write=None, create=None):
        self.entity = entity
        self.renderer = renderer

        self.read_projection = read
        self.write_projection = write
        self.create_projection = create

    def _compile(self, projection):
        if projection is None:
            return None
        return compile_projection(to_projection(projection))

    @property
    def read(self):
        return self.renderer.render(
            self.entity,
            self._compile(self.read_projection),
            name=f"{self.entity.name}Read",
        )

    @property
    def write(self):
        return self.renderer.render(
            self.entity,
            self._compile(self.write_projection),
            name=f"{self.entity.name}Write",
        )

    @property
    def create(self):
        return self.renderer.render(
            self.entity,
            self._compile(self.create_projection),
            name=f"{self.entity.name}Create",
        )


def api(entity, renderer, read=None, write=None, create=None):
    return EntityAPI(
        entity=entity,
        renderer=renderer,
        read=read,
        write=write,
        create=create,
    )


# =========================================================
# 6. DEBUG HELPERS
# =========================================================


def print_entity(entity, indent=0):
    pad = "  " * indent
    print(f"{pad}{entity.name}")

    for name, node in entity.fields.items():
        if isinstance(node, Field):
            print(f"{pad}  {name}: {node}")
        else:
            print(f"{pad}  {name}:")
            print_entity(node, indent + 2)


def to_projection(x):
    if x is None:
        return None

    if isinstance(x, Projection):
        return x

    if isinstance(x, Leaf):
        return Projection([x.path])

    raise TypeError(f"Cannot convert {type(x)} to Projection")
