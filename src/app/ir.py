from dataclasses import dataclass, fields as dc_fields, is_dataclass
from collections.abc import Callable
from typing import Any, Protocol, TypeVar, Union, cast, get_type_hints

from pydantic import BaseModel, create_model


@dataclass
class Field:
    type_: Any


@dataclass
class Entity:
    name: str
    fields: dict[str, Any]


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
        model_fields = cast(Any, cls).model_fields
        return {
            name: field_info.annotation for name, field_info in model_fields.items()
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
