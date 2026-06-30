from dataclasses import is_dataclass, make_dataclass
from typing import Any, get_type_hints

from ..ir import Field, UNSET, dataclass_update_type


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
        dataclass_fields: list[Any] = []

        for key, sub_spec in spec.items():
            node = entity.fields[key]

            if isinstance(node, Field):
                field_type = node.type_
            else:
                field_type = self._build_model(
                    sub_spec.children,
                    node,
                    f"{name}_{key}",
                    partial=partial,
                )

            if partial and sub_spec.required is not True:
                dataclass_fields.append(
                    (key, dataclass_update_type(field_type), UNSET),
                )
            else:
                dataclass_fields.append((key, field_type))

        model_cls = make_dataclass(name, dataclass_fields, kw_only=True)
        self._models_by_name[name] = model_cls
        return model_cls

    def _convert_kwargs(
        self, model_cls: type, kwargs: dict[str, Any]
    ) -> dict[str, Any]:
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
