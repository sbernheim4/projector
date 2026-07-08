from __future__ import annotations

from collections.abc import Callable
from typing import Any, TypedDict, cast

from ..ir import Field, annotated_type
from ..naming import pascal_case


class TypedDictRenderer:
    def render(self, entity, spec, name: str, partial: bool = False) -> type[Any]:
        annotations, required_keys, optional_keys = self._build_schema(
            spec,
            entity,
            partial=partial,
        )
        typed_dict_cls = self._make_typed_dict(name, annotations)
        setattr(typed_dict_cls, "__required_keys__", frozenset(required_keys))
        setattr(typed_dict_cls, "__optional_keys__", frozenset(optional_keys))
        return typed_dict_cls

    def instantiate(self, model_cls: type, **kwargs):
        return model_cls(**kwargs)

    def _make_typed_dict(self, name: str, annotations: dict[str, Any]) -> type[Any]:
        typed_dict_factory = cast(Callable[[str, dict[str, Any]], type[Any]], TypedDict)
        return typed_dict_factory(name, annotations)

    def _build_schema(
        self,
        spec,
        entity,
        partial: bool,
    ) -> tuple[dict[str, Any], set[str], set[str]]:
        annotations: dict[str, Any] = {}
        required_keys: set[str] = set()
        optional_keys: set[str] = set()

        for key, sub_spec in spec.items():
            node = entity.fields[key]

            if isinstance(node, Field):
                field_type = annotated_type(node.type_, node.metadata)
            else:
                nested_annotations, _, _ = self._build_schema(
                    sub_spec.children,
                    node,
                    partial=partial,
                )
                field_type = self._make_typed_dict(
                    f"{entity.name}{pascal_case(key)}", nested_annotations
                )
                field_type = annotated_type(field_type, node.metadata)

            if node.nullable and sub_spec.required is not True:
                field_type = field_type | None

            annotations[key] = field_type
            if sub_spec.required is False or (
                partial and sub_spec.required is not True
            ):
                optional_keys.add(key)
            else:
                required_keys.add(key)

        return annotations, required_keys, optional_keys
