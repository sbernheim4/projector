from pydantic import BaseModel

from ..ir import (
    Field,
    PydanticFieldDefs,
    annotated_type,
    create_pydantic_model,
    optional_update_type,
)
from ..naming import pascal_case


class PydanticRenderer:
    def render(self, entity, spec, name: str, partial: bool = False) -> type[BaseModel]:
        fields = self._build_fields(spec, entity, name, partial=partial)
        return create_pydantic_model(name, fields)

    def _build_fields(self, spec, entity, name, partial: bool) -> PydanticFieldDefs:
        fields: PydanticFieldDefs = {}

        for key, sub_spec in spec.items():
            node = entity.fields[key]

            if isinstance(node, Field):
                field_type = annotated_type(node.type_, node.metadata)
                if partial:
                    fields[key] = (
                        optional_update_type(field_type),
                        None,
                    )
                elif node.nullable and sub_spec.required is not True:
                    fields[key] = (optional_update_type(field_type), None)
                else:
                    fields[key] = (field_type, ...)
            else:
                nested = self._build_fields(
                    sub_spec.children,
                    node,
                    f"{name}{pascal_case(key)}",
                    partial=partial,
                )
                nested_model = create_pydantic_model(
                    f"{name}{pascal_case(key)}", nested
                )
                field_type = annotated_type(nested_model, node.metadata)
                if partial and sub_spec.required is not True:
                    fields[key] = (optional_update_type(field_type), None)
                elif node.nullable and sub_spec.required is not True:
                    fields[key] = (optional_update_type(field_type), None)
                else:
                    fields[key] = (field_type, ...)

        return fields
