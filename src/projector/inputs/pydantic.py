from typing import Annotated, Any, cast

from pydantic import BaseModel


class PydanticSourceAdapter:
    def matches(self, cls: type) -> bool:
        return isinstance(cls, type) and issubclass(cls, BaseModel)

    def name_for(self, cls: type) -> str:
        return cls.__name__

    def fields_for(self, cls: type) -> dict[str, Any]:
        model_fields = cast(Any, cls).model_fields
        return {
            name: _field_type(field_info) for name, field_info in model_fields.items()
        }


def _field_type(field_info: Any) -> Any:
    metadata = tuple(field_info.metadata)
    if _has_field_metadata(field_info):
        metadata = metadata + (field_info,)
    if not metadata:
        return field_info.annotation
    return Annotated[field_info.annotation, *metadata]


def _has_field_metadata(field_info: Any) -> bool:
    attributes_set = getattr(field_info, "_attributes_set", {})
    return any(key != "annotation" for key in attributes_set)
