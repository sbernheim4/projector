from typing import Any, get_type_hints


class PlainClassSourceAdapter:
    def matches(self, cls: type) -> bool:
        return isinstance(cls, type) and bool(getattr(cls, "__annotations__", None))

    def name_for(self, cls: type) -> str:
        return cls.__name__

    def fields_for(self, cls: type) -> dict[str, Any]:
        return get_type_hints(cls)

