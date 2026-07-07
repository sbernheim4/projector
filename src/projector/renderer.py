from .renderers import (
    AttrsRenderer,
    DataclassRenderer,
    PydanticRenderer,
    TypedDictRenderer,
)


class _RendererNamespace:
    @property
    def Attrs(self) -> AttrsRenderer:
        return AttrsRenderer()

    @property
    def Dataclass(self) -> DataclassRenderer:
        return DataclassRenderer()

    @property
    def Pydantic(self) -> PydanticRenderer:
        return PydanticRenderer()

    @property
    def TypedDict(self) -> TypedDictRenderer:
        return TypedDictRenderer()


renderer = _RendererNamespace()

__all__ = ["renderer"]
