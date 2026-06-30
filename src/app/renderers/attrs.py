from typing import Any, cast, get_type_hints

import attrs

from ..ir import Field


class AttrsRenderer:
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
        class_fields: dict[str, Any] = {}

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
                class_fields[key] = attrs.field(
                    default=None,
                    type=cast(type | None, field_type),
                )
            else:
                class_fields[key] = attrs.field(type=cast(type, field_type))

        return attrs.make_class(name, class_fields, kw_only=True)

    def _convert_kwargs(self, model_cls: type, kwargs: dict[str, Any]) -> dict[str, Any]:
        hints = get_type_hints(model_cls)
        converted = {}

        for key, value in kwargs.items():
            field_type = hints.get(key)
            nested_type = self._nested_attrs_type(field_type)

            if isinstance(value, dict) and nested_type is not None:
                converted[key] = nested_type(**self._convert_kwargs(nested_type, value))
            else:
                converted[key] = value

        return converted

    def _nested_attrs_type(self, field_type: Any) -> type | None:
        if isinstance(field_type, type) and attrs.has(field_type):
            return field_type

        union_args = getattr(field_type, "__args__", ())

        for arg in union_args:
            if isinstance(arg, type) and attrs.has(arg):
                return arg

        return None
