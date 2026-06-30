from dataclasses import is_dataclass, make_dataclass
from typing import Any, get_type_hints

from pydantic import BaseModel

from .ir import (
    Entity,
    Field,
    PydanticFieldDefs,
    UNSET,
    dataclass_update_type,
    create_pydantic_model,
    optional_update_type,
)


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
