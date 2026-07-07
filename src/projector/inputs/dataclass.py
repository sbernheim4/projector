from dataclasses import fields as dc_fields, is_dataclass
from typing import Any, get_type_hints


class DataclassSourceAdapter:
    def matches(self, cls: type) -> bool:
        return is_dataclass(cls)

    def name_for(self, cls: type) -> str:
        return cls.__name__

    def fields_for(self, cls: type) -> dict[str, Any]:
        hints = get_type_hints(cls)
        return {field.name: hints[field.name] for field in dc_fields(cls)}
