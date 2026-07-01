from argparse import ArgumentParser
from importlib import import_module

from .ir import build_entity
from .stubgen import generate_views_pyi


def generate_stubs(module_name: str) -> None:
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

    generate_views_pyi(module_name, entities)


def main(argv: list[str] | None = None) -> None:
    parser = ArgumentParser(prog="projector")
    subparsers = parser.add_subparsers(dest="command", required=True)

    stubs = subparsers.add_parser("stubs", help="Generate .pyi view stubs")
    stubs.add_argument("module", help="Module containing domain models")

    args = parser.parse_args(argv)

    if args.command == "stubs":
        generate_stubs(args.module)


if __name__ == "__main__":
    main()
