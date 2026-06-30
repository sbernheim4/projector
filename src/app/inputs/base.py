from typing import Any, Protocol


class SourceAdapter(Protocol):
    def matches(self, cls: type) -> bool: ...

    def name_for(self, cls: type) -> str: ...

    def fields_for(self, cls: type) -> dict[str, Any]: ...


def find_source_adapter(
    cls: type,
    adapters: tuple[SourceAdapter, ...],
) -> SourceAdapter | None:
    for adapter in adapters:
        if adapter.matches(cls):
            return adapter

    return None
