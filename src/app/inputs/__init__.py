from .attrs import AttrsSourceAdapter
from .base import SourceAdapter, find_source_adapter
from .dataclass import DataclassSourceAdapter
from .plain import PlainClassSourceAdapter
from .pydantic import PydanticSourceAdapter
from .typeddict import TypedDictSourceAdapter

DEFAULT_SOURCE_ADAPTERS: tuple[SourceAdapter, ...] = (
    AttrsSourceAdapter(),
    DataclassSourceAdapter(),
    PydanticSourceAdapter(),
    TypedDictSourceAdapter(),
    PlainClassSourceAdapter(),
)

__all__ = [
    "DEFAULT_SOURCE_ADAPTERS",
    "AttrsSourceAdapter",
    "DataclassSourceAdapter",
    "PlainClassSourceAdapter",
    "PydanticSourceAdapter",
    "TypedDictSourceAdapter",
    "SourceAdapter",
    "find_source_adapter",
]
