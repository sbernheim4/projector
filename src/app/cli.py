from argparse import ArgumentParser
from collections.abc import Iterator
from contextlib import contextmanager
from importlib import import_module
from pathlib import Path
import sys

from .ir import build_entity
from .stubgen import generate_views_pyi, write_module_class_stubs


@contextmanager
def _with_sys_path(path: Path) -> Iterator[None]:
    path_str = str(path)
    sys.path.insert(0, path_str)
    try:
        yield
    finally:
        sys.path.remove(path_str)


def _module_from_path(path: Path) -> tuple[str, Path, Path]:
    path = path.resolve()
    if path.suffix != ".py":
        raise SystemExit(f"Expected a Python module path ending in .py: {path}")

    search_roots = [*(Path(item) for item in sys.path if item), Path.cwd()]
    seen_roots: set[Path] = set()
    for root in search_roots:
        root = root.resolve()
        if root in seen_roots:
            continue
        seen_roots.add(root)
        try:
            relative = path.relative_to(root)
        except ValueError:
            continue
        return ".".join(relative.with_suffix("").parts), root, path.with_suffix(".pyi")

    package_parts = [path.stem]
    package_root = path.parent
    current = path.parent
    while (current / "__init__.py").exists():
        package_parts.append(current.name)
        package_root = current.parent
        current = current.parent

    return ".".join(reversed(package_parts)), package_root, path.with_suffix(".pyi")


def generate_stubs(module_path: str) -> None:
    module_name, package_root, target = _module_from_path(Path(module_path))
    with _with_sys_path(package_root):
        module = import_module(module_name)

    entities = []

    for name in dir(module):
        value = getattr(module, name)
        if isinstance(value, type):
            try:
                entities.append(build_entity(value))
            except TypeError:
                continue

    if not entities:
        raise SystemExit(f"No supported model classes found in {module_name}")

    generate_views_pyi(module_name, entities, target=target)


def generate_stubs_for_paths(module_paths: list[str]) -> None:
    for module_path in module_paths:
        generate_stubs(module_path)


def generate_module_stubs(module_path: str) -> None:
    module_name, package_root, target = _module_from_path(Path(module_path))
    with _with_sys_path(package_root):
        write_module_class_stubs(module_name, target=target)


def generate_module_stubs_for_paths(module_paths: list[str]) -> None:
    for module_path in module_paths:
        generate_module_stubs(module_path)


def main(argv: list[str] | None = None) -> None:
    parser = ArgumentParser(prog="projector")
    subparsers = parser.add_subparsers(dest="command", required=True)

    stubs = subparsers.add_parser("stubs", help="Generate .pyi view stubs")
    stubs.add_argument(
        "modules",
        nargs="+",
        help="Python file paths containing domain models",
    )

    module_stubs = subparsers.add_parser(
        "module-stubs",
        help="Generate .pyi module class stubs",
    )
    module_stubs.add_argument(
        "modules",
        nargs="+",
        help="Python file path containing typed API classes",
    )

    args = parser.parse_args(argv)

    if args.command == "stubs":
        generate_stubs_for_paths(args.modules)
    elif args.command == "module-stubs":
        generate_module_stubs_for_paths(args.modules)


if __name__ == "__main__":
    main()
