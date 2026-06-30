from .ir import Entity
from .projection import Leaf
from .ir import build_entity


class ViewNode:
    def __init__(self, entity, path=None):
        self._entity = entity
        self._path = path or []

        for name, field in entity.fields.items():
            if isinstance(field, Entity):
                setattr(self, name, ViewNode(field, self._path + [name]))
            else:
                setattr(self, name, Leaf(self._path + [name]))

    def __getattr__(self, name):
        return Leaf([name])


def build_views(entity):
    return ViewNode(entity)


def views_for(model_cls):
    return build_views(build_entity(model_cls))
