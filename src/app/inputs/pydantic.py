from typing import Any, cast

from pydantic import BaseModel


class PydanticSourceAdapter:
    def matches(self, cls: type) -> bool:
        return isinstance(cls, type) and issubclass(cls, BaseModel)

    def name_for(self, cls: type) -> str:
        return cls.__name__

    def fields_for(self, cls: type) -> dict[str, Any]:
        model_fields = cast(Any, cls).model_fields
        return {
            name: field_info.annotation for name, field_info in model_fields.items()
        }
