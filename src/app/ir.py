from collections.abc import Callable
from dataclasses import dataclass
from typing import Any, TypeVar, Union, cast

from pydantic import BaseModel, create_model

from .inputs import DEFAULT_SOURCE_ADAPTERS, SourceAdapter, find_source_adapter


@dataclass
class Field:
    type_: Any


@dataclass
class Entity:
    name: str
    fields: dict[str, Any]


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
