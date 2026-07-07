from pydantic import BaseModel

from ..ir import Field, PydanticFieldDefs, create_pydantic_model, optional_update_type
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
                if partial:
                    fields[key] = (
                        optional_update_type(node.type_),
                        None,
                    )
                elif node.nullable and sub_spec.required is not True:
                    fields[key] = (optional_update_type(node.type_), None)
                else:
                    fields[key] = (node.type_, ...)
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
                if partial and sub_spec.required is not True:
                    fields[key] = (optional_update_type(nested_model), None)
                elif node.nullable and sub_spec.required is not True:
                    fields[key] = (optional_update_type(nested_model), None)
                else:
                    fields[key] = (nested_model, ...)

        return fields
