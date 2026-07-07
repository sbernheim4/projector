from typing import Any, get_type_hints, is_typeddict


class TypedDictSourceAdapter:
    def matches(self, cls: type) -> bool:
        return is_typeddict(cls)

    def name_for(self, cls: type) -> str:
        return cls.__name__

    def fields_for(self, cls: type) -> dict[str, Any]:
        return get_type_hints(cls)
