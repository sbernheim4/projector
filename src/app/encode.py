from typing import Any

from .ir import Entity, Field, UNSET, build_entity
from .projection import Leaf, Projection, compile_projection
from .renderers import DataclassRenderer, PydanticRenderer

__all__ = [
    "DataclassRenderer",
    "Entity",
    "Field",
    "Leaf",
    "Projection",
    "PydanticRenderer",
    "UNSET",
    "api",
    "build_entity",
    "build_model_and_factory",
    "compile_projection",
]


def build_model_and_factory(entity, renderer, projection, name, partial: bool = False):
    spec = compile_projection(projection)

    model_cls = renderer.render(entity, spec, name=name, partial=partial)

    def factory(**kwargs):
        instantiate = getattr(renderer, "instantiate", None)
        if instantiate is not None:
            return instantiate(model_cls, **kwargs)
        return model_cls(**kwargs)

    setattr(factory, "model", model_cls)

    return model_cls, factory


class EntityAPI:
    entity: Any

    renderer: Any

    create: Any
    create_model: Any

    update: Any
    update_model: Any

    read: Any
    read_model: Any


def api(entity, renderer, read=None, create=None, update=None):
    api_obj = EntityAPI()

    def build(name, projection, partial: bool = False):
        model_cls, factory = build_model_and_factory(
            entity,
            renderer,
            projection,
            name,
            partial=partial,
        )
        return model_cls, factory

    if create is not None:
        model_cls, factory = build(f"{entity.name}Create", create)
        api_obj.create_model = model_cls
        api_obj.create = factory

    if read is not None:
        model_cls, factory = build(f"{entity.name}Read", read)
        api_obj.read_model = model_cls
        api_obj.read = factory

    if update is not None:
        model_cls, factory = build(
            f"{entity.name}Update",
            update,
            partial=True,
        )
        api_obj.update_model = model_cls
        api_obj.update = factory

    api_obj.entity = entity
    api_obj.renderer = renderer

    return api_obj
