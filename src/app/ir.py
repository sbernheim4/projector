from collections.abc import Callable
from dataclasses import dataclass
from types import NoneType, UnionType
from typing import Any, TypeVar, Union, cast, get_args, get_origin

from pydantic import BaseModel, create_model

from .inputs import DEFAULT_SOURCE_ADAPTERS, SourceAdapter, find_source_adapter


@dataclass
class Field:
    type_: Any
    nullable: bool = False


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


def unwrap_optional(type_: Any) -> tuple[Any, bool]:
    origin = get_origin(type_)
    if origin is Union or origin is UnionType:
        args = tuple(arg for arg in get_args(type_) if arg is not NoneType)
        if len(args) == 1 and len(get_args(type_)) == 2:
            return args[0], True
    return type_, False


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
        field_type, nullable = unwrap_optional(field_type)
        nested_adapter = find_source_adapter(field_type, adapters)

        if nested_adapter is not None:
            entity = build_entity(
                field_type,
                adapter=nested_adapter,
                adapters=adapters,
            )
            entity.fields["_nullable"] = Field(nullable, False)
            schema[field_name] = entity
        else:
            schema[field_name] = Field(field_type, nullable=nullable)

    return Entity(source_adapter.name_for(cls), schema)
