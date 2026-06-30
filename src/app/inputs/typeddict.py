from typing import Any, get_type_hints


class TypedDictSourceAdapter:
    def matches(self, cls: type) -> bool:
        return isinstance(cls, type) and issubclass(cls, dict) and hasattr(cls, "__total__") and hasattr(cls, "__annotations__")

    def name_for(self, cls: type) -> str:
        return cls.__name__

    def fields_for(self, cls: type) -> dict[str, Any]:
        return get_type_hints(cls)
