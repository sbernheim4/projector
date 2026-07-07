from __future__ import annotations

import textwrap
from pathlib import Path

from app.cli import main


def test_stubs_command_accepts_python_file_path(tmp_path: Path):
    package = tmp_path / "sample"
    package.mkdir()
    (package / "__init__.py").write_text("", encoding="utf-8")
    module_path = package / "models.py"
    module_path.write_text(
        textwrap.dedent(
            """
            from dataclasses import dataclass


            @dataclass(kw_only=True)
            class Address:
                city: str
                zip: str


            @dataclass(kw_only=True)
            class User:
                name: str
                address: Address
            """
        ),
        encoding="utf-8",
    )

    main(["stubs", str(module_path)])

    stub = module_path.with_suffix(".pyi")
    assert stub.exists()
    contents = stub.read_text(encoding="utf-8")
    assert "class UserView:" in contents
    assert "name: Leaf[str]" in contents
    assert "address: AddressView" in contents


def test_stubs_command_accepts_multiple_python_file_paths(tmp_path: Path):
    first_package = tmp_path / "first"
    first_package.mkdir()
    (first_package / "__init__.py").write_text("", encoding="utf-8")
    first_module = first_package / "models.py"
    first_module.write_text(
        textwrap.dedent(
            """
            from dataclasses import dataclass


            @dataclass(kw_only=True)
            class User:
                name: str
            """
        ),
        encoding="utf-8",
    )

    second_package = tmp_path / "second"
    second_package.mkdir()
    (second_package / "__init__.py").write_text("", encoding="utf-8")
    second_module = second_package / "models.py"
    second_module.write_text(
        textwrap.dedent(
            """
            from dataclasses import dataclass


            @dataclass(kw_only=True)
            class Project:
                title: str
            """
        ),
        encoding="utf-8",
    )

    main(["stubs", str(first_module), str(second_module)])

    assert "class UserView:" in first_module.with_suffix(".pyi").read_text(
        encoding="utf-8"
    )
    assert "class ProjectView:" in second_module.with_suffix(".pyi").read_text(
        encoding="utf-8"
    )


def test_module_stubs_command_accepts_python_file_path(tmp_path: Path):
    package = tmp_path / "sample_router"
    package.mkdir()
    (package / "__init__.py").write_text("", encoding="utf-8")
    module_path = package / "router.py"
    module_path.write_text(
        textwrap.dedent(
            """
            from fastapi import APIRouter


            router = APIRouter()
            """
        ),
        encoding="utf-8",
    )

    main(["module-stubs", str(module_path)])

    stub = module_path.with_suffix(".pyi")
    assert stub.read_text(encoding="utf-8") == textwrap.dedent(
        """
        from fastapi import APIRouter

        router: APIRouter
        """
    ).lstrip()


def test_module_stubs_command_accepts_multiple_python_file_paths(tmp_path: Path):
    first_package = tmp_path / "first_router"
    first_package.mkdir()
    (first_package / "__init__.py").write_text("", encoding="utf-8")
    first_module = first_package / "users.py"
    first_module.write_text(
        textwrap.dedent(
            """
            from fastapi import APIRouter


            router = APIRouter()
            """
        ),
        encoding="utf-8",
    )

    second_package = tmp_path / "second_router"
    second_package.mkdir()
    (second_package / "__init__.py").write_text("", encoding="utf-8")
    second_module = second_package / "projects.py"
    second_module.write_text(
        textwrap.dedent(
            """
            from fastapi import APIRouter


            router = APIRouter()
            """
        ),
        encoding="utf-8",
    )

    main(["module-stubs", str(first_module), str(second_module)])

    assert "router: APIRouter" in first_module.with_suffix(".pyi").read_text(
        encoding="utf-8"
    )
    assert "router: APIRouter" in second_module.with_suffix(".pyi").read_text(
        encoding="utf-8"
    )
