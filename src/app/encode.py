from dataclasses import is_dataclass, fields as dc_fields, make_dataclass
from collections.abc import Callable
from typing import Any, Generic, Protocol, TypeVar, Union, cast, get_type_hints
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


class SourceAdapter(Protocol):
    def matches(self, cls: type) -> bool: ...

    def name_for(self, cls: type) -> str: ...

    def fields_for(self, cls: type) -> dict[str, Any]: ...


PydanticFieldDefs = dict[str, tuple[Any, Any]]
T = TypeVar("T")


class UnsetType:
    def __bool__(self):
        return False

    def __repr__(self):
        return "UNSET"


UNSET = UnsetType()


def optional_update_type(type_: Any) -> Any:
    return Union[type_, None]


def dataclass_update_type(type_: Any) -> Any:
    return Union[type_, None, UnsetType]


def create_pydantic_model(name: str, fields: PydanticFieldDefs) -> type[BaseModel]:
    typed_create_model = cast(Callable[..., type[BaseModel]], create_model)
    return typed_create_model(name, **fields)


class DataclassSourceAdapter:
    def matches(self, cls: type) -> bool:
        return is_dataclass(cls)

    def name_for(self, cls: type) -> str:
        return cls.__name__

    def fields_for(self, cls: type) -> dict[str, Any]:
        hints = get_type_hints(cls)
        return {field.name: hints[field.name] for field in dc_fields(cls)}


class PydanticSourceAdapter:
    def matches(self, cls: type) -> bool:
        return isinstance(cls, type) and issubclass(cls, BaseModel)

    def name_for(self, cls: type) -> str:
        return cls.__name__

    def fields_for(self, cls: type) -> dict[str, Any]:
        return {
            name: field_info.annotation
            for name, field_info in cls.model_fields.items()
        }


class PlainClassSourceAdapter:
    def matches(self, cls: type) -> bool:
        return isinstance(cls, type) and bool(getattr(cls, "__annotations__", None))

    def name_for(self, cls: type) -> str:
        return cls.__name__

    def fields_for(self, cls: type) -> dict[str, Any]:
        return get_type_hints(cls)


DEFAULT_SOURCE_ADAPTERS: tuple[SourceAdapter, ...] = (
    DataclassSourceAdapter(),
    PydanticSourceAdapter(),
    PlainClassSourceAdapter(),
)


def find_source_adapter(
    cls: type,
    adapters: tuple[SourceAdapter, ...],
) -> SourceAdapter | None:
    for adapter in adapters:
        if adapter.matches(cls):
            return adapter

    return None


def build_entity(
    cls: type,
    *,
    adapter: SourceAdapter | None = None,
    adapters: tuple[SourceAdapter, ...] = DEFAULT_SOURCE_ADAPTERS,
):
    source_adapter = adapter or find_source_adapter(cls, adapters)

    if source_adapter is None:
        raise TypeError(f"No source adapter found for {cls!r}")

    schema: dict[str, Entity | Field] = {}

    for field_name, field_type in source_adapter.fields_for(cls).items():
        nested_adapter = find_source_adapter(field_type, adapters)

        if nested_adapter is not None:
            schema[field_name] = build_entity(
                field_type,
                adapter=nested_adapter,
                adapters=adapters,
            )
        else:
            schema[field_name] = Field(field_type)

    return Entity(source_adapter.name_for(cls), schema)


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
    def render(self, entity, spec, name: str, partial: bool = False) -> type[BaseModel]:
        fields = self._build_fields(spec, entity, name, partial=partial)
        return create_pydantic_model(name, fields)

    def _build_fields(self, spec, entity, name, partial: bool) -> PydanticFieldDefs:
        fields: PydanticFieldDefs = {}

        for key, sub_spec in spec.items():
            node = entity.fields[key]

            if isinstance(node, Field):
                if partial:
                    fields[key] = (optional_update_type(node.type_), None)
                else:
                    fields[key] = (node.type_, ...)

            else:
                nested = self._build_fields(
                    sub_spec,
                    node,
                    f"{name}_{key}",
                    partial=partial,
                )
                nested_model = create_pydantic_model(f"{name}_{key}", nested)
                if partial:
                    fields[key] = (optional_update_type(nested_model), None)
                else:
                    fields[key] = (nested_model, ...)

        return fields


class DataclassRenderer:
    def __init__(self):
        self._models_by_name: dict[str, type] = {}

    def render(self, entity, spec, name: str, partial: bool = False) -> type:
        model_cls = self._build_model(spec, entity, name, partial=partial)
        self._models_by_name[name] = model_cls
        return model_cls

    def instantiate(self, model_cls: type, **kwargs):
        converted = self._convert_kwargs(model_cls, kwargs)
        return model_cls(**converted)

    def _build_model(self, spec, entity, name: str, partial: bool) -> type:
        dataclass_fields = []

        for key, sub_spec in spec.items():
            node = entity.fields[key]

            if isinstance(node, Field):
                field_type = node.type_
            else:
                field_type = self._build_model(
                    sub_spec,
                    node,
                    f"{name}_{key}",
                    partial=partial,
                )

            if partial:
                dataclass_fields.append(
                    (key, dataclass_update_type(field_type), UNSET),
                )
            else:
                dataclass_fields.append((key, field_type))

        model_cls = make_dataclass(name, dataclass_fields, kw_only=True)
        self._models_by_name[name] = model_cls
        return model_cls

    def _convert_kwargs(self, model_cls: type, kwargs: dict[str, Any]) -> dict[str, Any]:
        hints = get_type_hints(model_cls)
        converted = {}

        for key, value in kwargs.items():
            field_type = hints.get(key)
            nested_type = self._nested_dataclass_type(field_type)

            if isinstance(value, dict) and nested_type is not None:
                converted[key] = nested_type(
                    **self._convert_kwargs(nested_type, value),
                )
            else:
                converted[key] = value

        return converted

    def _nested_dataclass_type(self, field_type: Any) -> type | None:
        if isinstance(field_type, type) and is_dataclass(field_type):
            return field_type

        union_args = getattr(field_type, "__args__", ())

        for arg in union_args:
            if isinstance(arg, type) and is_dataclass(arg):
                return arg

        return None


# =========================================================
# 5. FACTORY BUILDER (CORE FIX)
# =========================================================


def build_model_and_factory(entity, renderer, projection, name, partial: bool = False):
    spec = compile_projection(projection)

    model_cls = renderer.render(entity, spec, name=name, partial=partial)

    def factory(**kwargs):
        instantiate = getattr(renderer, "instantiate", None)
        if instantiate is not None:
            return instantiate(model_cls, **kwargs)
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

    update: Any
    update_model: Any

    read: Any
    read_model: Any


def api(entity, renderer, read=None, create=None, update=None):
    api_obj = EntityAPI()

    def build(name, projection, partial: bool = False):
        model_cls, factory = build_model_and_factory(
            entity,
            renderer,
            projection,
            name,
            partial=partial,
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

    if update is not None:
        model_cls, factory = build(
            f"{entity.name}Update",
            update,
            partial=True,
        )
        api_obj.update_model = model_cls
        api_obj.update = factory

    api_obj.entity = entity
    api_obj.renderer = renderer

    return api_obj
