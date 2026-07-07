from typing import Any, cast

import attrs

from ..ir import Field
from ..naming import pascal_case


class AttrsRenderer:
    def __init__(self):
        self._models_by_name: dict[str, type] = {}
        self._conversion_plans: dict[type, dict[str, type]] = {}

    def render(self, entity, spec, name: str, partial: bool = False) -> type:
        model_cls = self._build_model(spec, entity, name, partial=partial)
        self._models_by_name[name] = model_cls
        return model_cls

    def instantiate(self, model_cls: type, **kwargs):
        converted = self._convert_kwargs(model_cls, kwargs)
        return model_cls(**converted)

    def _build_model(self, spec, entity, name: str, partial: bool) -> type:
        class_fields: dict[str, Any] = {}
        conversion_plan: dict[str, type] = {}

        for key, sub_spec in spec.items():
            node = entity.fields[key]

            if isinstance(node, Field):
                field_type = node.type_
            else:
                field_type = self._build_model(
                    sub_spec.children,
                    node,
                    f"{name}{pascal_case(key)}",
                    partial=partial,
                )
                conversion_plan[key] = field_type

            if partial and sub_spec.required is not True:
                class_fields[key] = attrs.field(
                    default=None,
                    type=cast(type | None, field_type),
                )
            else:
                class_fields[key] = attrs.field(type=cast(type, field_type))

        model_cls = attrs.make_class(name, class_fields, kw_only=True)
        self._conversion_plans[model_cls] = conversion_plan
        return model_cls

    def _convert_kwargs(
        self, model_cls: type, kwargs: dict[str, Any]
    ) -> dict[str, Any]:
        conversion_plan = self._conversion_plans.get(model_cls, {})
        converted = {}

        for key, value in kwargs.items():
            nested_type = conversion_plan.get(key)

            if isinstance(value, dict) and nested_type is not None:
                converted[key] = nested_type(**self._convert_kwargs(nested_type, value))
            else:
                converted[key] = value

        return converted
