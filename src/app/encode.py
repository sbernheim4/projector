from typing import Any

from .ir import Entity, Field, UNSET, build_entity
from .naming import pascal_case
from .projection import Leaf, Projection, compile_projection
from .renderers import (
    AttrsRenderer,
    DataclassRenderer,
    PydanticRenderer,
    TypedDictRenderer,
)

__all__ = [
    "DataclassRenderer",
    "AttrsRenderer",
    "Entity",
    "Field",
    "Leaf",
    "Projection",
    "PydanticRenderer",
    "TypedDictRenderer",
    "UNSET",
    "project",
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

    def __getattr__(self, name: str) -> Any:
        raise AttributeError(name)


def project(model_cls, renderer, **outputs):
    if isinstance(model_cls, Entity):
        raise TypeError(
            "project() accepts a model class; pass User, not build_entity(User)"
        )

    entity = build_entity(model_cls)
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

    for output_name, projection in outputs.items():
        partial = output_name.lower() == "update"
        model_suffix = pascal_case(output_name)
        if output_name.islower() or "_" in output_name:
            accessor_name = output_name
            model_attr_name = f"{output_name}_model"
        else:
            accessor_name = model_suffix
            model_attr_name = f"{model_suffix}Model"
        model_cls, factory = build(
            f"{entity.name}{model_suffix}",
            projection,
            partial=partial,
        )
        setattr(api_obj, model_attr_name, model_cls)
        setattr(api_obj, accessor_name, factory)

    api_obj.entity = entity
    api_obj.renderer = renderer

    return api_obj
