from .encode import build_entity, build_views


def views_for(model_cls):
    return build_views(build_entity(model_cls))
