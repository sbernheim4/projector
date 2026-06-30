from .base import SourceAdapter, find_source_adapter
from .dataclass import DataclassSourceAdapter
from .plain import PlainClassSourceAdapter
from .pydantic import PydanticSourceAdapter
from .typeddict import TypedDictSourceAdapter

DEFAULT_SOURCE_ADAPTERS: tuple[SourceAdapter, ...] = (
    DataclassSourceAdapter(),
    PydanticSourceAdapter(),
    TypedDictSourceAdapter(),
    PlainClassSourceAdapter(),
)

__all__ = [
    "DEFAULT_SOURCE_ADAPTERS",
    "DataclassSourceAdapter",
    "PlainClassSourceAdapter",
    "PydanticSourceAdapter",
    "TypedDictSourceAdapter",
    "SourceAdapter",
    "find_source_adapter",
]
