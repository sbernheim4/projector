from importlib import import_module
from pathlib import Path
from types import NoneType
from typing import Any, Iterable, get_args, get_origin, get_type_hints

from .ir import Entity


def _render_model_class(name: str, entity: Entity) -> list[str]:
    lines = [f"class {name}:"]
    if not entity.fields:
        lines.append("    ...")
        return lines

    for field_name, field in entity.fields.items():
        if isinstance(field, Entity):
            lines.append(f"    {field_name}: {field.name}")
        else:
            lines.append(f"    {field_name}: {field.type_.__name__}")
    return lines


def _render_view_class(name: str, entity: Entity) -> list[str]:
    lines = [f"class {name}:"]
    if not entity.fields:
        lines.append("    ...")
        return lines

    for field_name, field in entity.fields.items():
        if isinstance(field, Entity):
            lines.append(f"    {field_name}: {field.name}View")
        else:
            lines.append(f"    {field_name}: Leaf[{field.type_.__name__}]")
    return lines


def _render_entity_stubs(entity: Entity, parts: list[str], emitted: set[str]) -> None:
    if entity.name in emitted:
        return
    emitted.add(entity.name)

    nested_entities = [field for field in entity.fields.values() if isinstance(field, Entity)]
    for nested_entity in nested_entities:
        _render_entity_stubs(nested_entity, parts, emitted)

    parts.extend(_render_model_class(entity.name, entity))
    parts.append("")
    parts.extend(_render_view_class(f"{entity.name}View", entity))
    parts.append("")
    parts.append(f"{entity.name.lower()}_views: {entity.name}View")
    parts.append("")


def render_views_stub(_module_name: str, entities: Iterable[Entity]) -> str:
    entities = list(entities)
    if not entities:
        raise ValueError("At least one entity is required")

    parts = [
        "from typing import Any, overload",
        "",
        "from app.projection import Leaf",
        "",
    ]

    emitted: set[str] = set()
    for entity in entities:
        _render_entity_stubs(entity, parts, emitted)

    for entity in entities:
        parts.append("@overload")
        parts.append(
            f"def views_for(model_cls: type[{entity.name}]) -> {entity.name}View: ..."
        )

    parts.append("def views_for(model_cls: type[object]) -> Any: ...")

    return "\n".join(parts).rstrip() + "\n"


def write_views_stub(module_name: str, entities: Iterable[Entity]) -> Path:
    module_path = Path(*module_name.split("."))
    target = module_path.with_suffix(".pyi")
    target.write_text(render_views_stub(module_name, entities), encoding="utf-8")
    return target


def generate_views_pyi(module_name: str, entities: Iterable[Entity]) -> Path:
    return write_views_stub(module_name, entities)


def _render_type_expr(field_type: Any) -> str:
    origin = get_origin(field_type)
    if origin is None:
        if isinstance(field_type, type):
            module = getattr(field_type, "__module__", "")
            if module == "builtins":
                return field_type.__name__
            return f'"{field_type.__name__}"'
        return getattr(field_type, "__name__", str(field_type))

    if origin is list:
        return f"list[{_render_type_expr(get_args(field_type)[0])}]"
    if origin is dict:
        key_type, value_type = get_args(field_type)
        return f"dict[{_render_type_expr(key_type)}, {_render_type_expr(value_type)}]"
    if origin is tuple:
        return "tuple[" + ", ".join(_render_type_expr(arg) for arg in get_args(field_type)) + "]"
    if origin is type:
        return f"type[{_render_type_expr(get_args(field_type)[0])}]"
    args = get_args(field_type)
    if len(args) == 2 and NoneType in args:
        other = next(arg for arg in args if arg is not NoneType)
        return f"{_render_type_expr(other)} | None"

    rendered_args = ", ".join(_render_type_expr(arg) for arg in args)
    origin_name = getattr(origin, "__name__", str(origin).removeprefix("typing."))
    return f"{origin_name}[{rendered_args}]"


def _render_class_stub(
    name: str,
    cls: type[Any],
    emitted: set[str],
    parts: list[str],
) -> None:
    if name in emitted:
        return
    emitted.add(name)

    parts.append(f"class {name}:")
    annotations = get_type_hints(cls, include_extras=True)
    if not annotations:
        parts.append("    ...")
        parts.append("")
        return

    nested_types: list[tuple[str, type[Any]]] = []
    for field_name, field_type in annotations.items():
        if isinstance(field_type, type) and field_type.__module__ != "builtins":
            nested_types.append((field_type.__name__, field_type))
        parts.append(f"    {field_name}: {_render_type_expr(field_type)}")

    parts.append("")

    for nested_name, nested_cls in nested_types:
        _render_class_stub(nested_name, nested_cls, emitted, parts)


def render_module_class_stubs(module_name: str) -> str:
    module = import_module(module_name)
    parts: list[str] = []
    has_router = hasattr(module, "router")

    if has_router:
        parts.append("from fastapi import APIRouter")
        parts.append("")
        parts.append("router: APIRouter")
        parts.append("")

    return "\n".join(parts).rstrip() + "\n"


def write_module_class_stubs(module_name: str) -> Path:
    module_path = Path(*module_name.split("."))
    target = module_path.with_suffix(".pyi")
    target.write_text(render_module_class_stubs(module_name), encoding="utf-8")
    return target
