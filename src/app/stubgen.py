from pathlib import Path
from typing import Iterable

from .ir import Entity


def _render_view_class(name: str, entity: Entity, indent: int = 0) -> list[str]:
    pad = " " * indent
    lines = [f"{pad}class {name}:"]
    if not entity.fields:
        lines.append(f"{pad}    ...")
        return lines

    for field_name, field in entity.fields.items():
        if isinstance(field, Entity):
            lines.append(f"{pad}    {field_name}: {field.name}View")
        else:
            lines.append(f"{pad}    {field_name}: Leaf[{field.type_.__name__}]")
    return lines


def render_views_stub(module_name: str, entities: Iterable[Entity]) -> str:
    entities = list(entities)
    if not entities:
        raise ValueError("At least one entity is required")

    imports = ", ".join(entity.name for entity in entities)
    parts = [
        "from typing import overload",
        "",
        "from app.projection import Leaf",
        "",
        f"from {module_name} import {imports}",
        "",
    ]

    for entity in entities:
        parts.extend(_render_view_class(f"{entity.name}View", entity))
        parts.append("")

    for entity in entities:
        parts.append("@overload")
        parts.append(
            f"def views_for(model_cls: type[{entity.name}]) -> {entity.name}View: ...",
        )
        parts.append("")

    return "\n".join(parts).rstrip() + "\n"


def write_views_stub(module_name: str, entities: Iterable[Entity]) -> Path:
    module_path = Path(*module_name.split("."))
    target = module_path.with_suffix(".pyi")
    target.write_text(render_views_stub(module_name, entities), encoding="utf-8")
    return target
