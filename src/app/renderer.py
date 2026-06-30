from .renderers import AttrsRenderer, DataclassRenderer, PydanticRenderer


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


renderer = _RendererNamespace()

__all__ = ["renderer"]
