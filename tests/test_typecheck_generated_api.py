from __future__ import annotations

import os
import subprocess
import textwrap
from pathlib import Path

from projector.cli import main


def _run_typechecker(
    command: list[str], cwd: Path, pythonpath: Path
) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env["PYTHONPATH"] = f"{pythonpath / 'src'}:{pythonpath}"
    env["UV_CACHE_DIR"] = str(pythonpath / ".uv-cache")
    return subprocess.run(
        command,
        cwd=cwd,
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )


def test_generated_project_is_typecheckable(tmp_path: Path):
    repo_root = Path(__file__).resolve().parents[1]
    package = tmp_path / "sample"
    package.mkdir()
    (package / "__init__.py").write_text("", encoding="utf-8")

    (package / "models.py").write_text(
        textwrap.dedent(
            """
            from dataclasses import dataclass

            from projector import project, renderer, views_for


            @dataclass(kw_only=True)
            class Address:
                city: str
                zip: str


            @dataclass(kw_only=True)
            class User:
                name: str
                email: str
                address: Address


            user_views = views_for(User)
            UserModels = project(
                User,
                renderer=renderer.Pydantic,
                create=user_views.name + user_views.email + user_views.address.city + user_views.address.zip,
                update=user_views.name + user_views.email + user_views.address.city + user_views.address.zip,
                renameUserCity=user_views.address.city,
            )

            UserCreate = UserModels.CreateModel
            UserUpdate = UserModels.UpdateModel
            UserRenameUserCity = UserModels.RenameUserCityModel
            """
        ),
        encoding="utf-8",
    )

    (package / "models.pyi").write_text(
        textwrap.dedent(
            """
            from typing import Any, overload

            from projector.projection import Leaf


            class Address:
                city: str
                zip: str


            class AddressView:
                city: Leaf[str]
                zip: Leaf[str]


            address_views: AddressView


            class User:
                name: str
                email: str
                address: Address


            class UserView:
                name: Leaf[str]
                email: Leaf[str]
                address: AddressView


            user_views: UserView


            class UserCreateAddress:
                city: str
                zip: str


            class UserCreateAddressView:
                city: Leaf[str]
                zip: Leaf[str]


            usercreateaddress_views: UserCreateAddressView


            class UserCreate:
                name: str
                email: str
                address: UserCreateAddress


            class UserCreateView:
                name: Leaf[str]
                email: Leaf[str]
                address: UserCreateAddressView


            usercreate_views: UserCreateView


            class UserRenameUserCityAddress:
                city: str


            class UserRenameUserCityAddressView:
                city: Leaf[str]


            userrenameusercityaddress_views: UserRenameUserCityAddressView


            class UserRenameUserCity:
                address: UserRenameUserCityAddress


            class UserRenameUserCityView:
                address: UserRenameUserCityAddressView


            userrenameusercity_views: UserRenameUserCityView


            class UserUpdateAddress:
                city: str
                zip: str


            class UserUpdateAddressView:
                city: Leaf[str]
                zip: Leaf[str]


            userupdateaddress_views: UserUpdateAddressView


            class UserUpdate:
                name: str
                email: str
                address: UserUpdateAddress


            class UserUpdateView:
                name: Leaf[str]
                email: Leaf[str]
                address: UserUpdateAddressView


            userupdate_views: UserUpdateView


            @overload
            def views_for(model_cls: type[Address]) -> AddressView: ...


            @overload
            def views_for(model_cls: type[User]) -> UserView: ...


            @overload
            def views_for(model_cls: type[UserCreate]) -> UserCreateView: ...


            @overload
            def views_for(model_cls: type[UserRenameUserCity]) -> UserRenameUserCityView: ...


            @overload
            def views_for(model_cls: type[UserUpdate]) -> UserUpdateView: ...


            def views_for(model_cls: type[object]) -> Any: ...
            """
        ),
        encoding="utf-8",
    )

    (package / "consumer.py").write_text(
        textwrap.dedent(
            """
            from sample.models import UserCreate, UserRenameUserCity, UserUpdate


            def use_create(payload: UserCreate) -> str:
                return payload.address.city


            def use_update(payload: UserUpdate) -> str:
                return payload.address.zip or ""


            def use_command(payload: UserRenameUserCity) -> str:
                return payload.address.city
            """
        ),
        encoding="utf-8",
    )

    result = _run_typechecker(
        ["ty", "check", str(package / "consumer.py")], tmp_path, repo_root
    )
    assert result.returncode == 0, result.stdout + result.stderr


def test_cli_generated_type_stubs_are_typecheckable(tmp_path: Path):
    repo_root = Path(__file__).resolve().parents[1]
    package = tmp_path / "sample_cli"
    package.mkdir()
    (package / "__init__.py").write_text("", encoding="utf-8")

    models_path = package / "models.py"
    models_path.write_text(
        textwrap.dedent(
            """
            from dataclasses import dataclass

            from projector import project, renderer, views_for


            @dataclass(kw_only=True)
            class Address:
                city: str
                zip: str


            @dataclass(kw_only=True)
            class User:
                name: str
                address: Address


            user_views = views_for(User)
            UserModels = project(
                User,
                renderer=renderer.Pydantic,
                Create=user_views.name + user_views.address.city + user_views.address.zip,
                RenameCity=user_views.address.city,
            )

            UserCreate = UserModels.CreateModel
            UserRenameCity = UserModels.RenameCityModel
            """
        ),
        encoding="utf-8",
    )

    main(["type-stubs", str(models_path)])

    (package / "consumer.py").write_text(
        textwrap.dedent(
            """
            from sample_cli.models import UserCreate, UserRenameCity, user_views


            def use_create(payload: UserCreate) -> str:
                return payload.address.zip


            def use_command(payload: UserRenameCity) -> str:
                return payload.address.city


            _ok = user_views.address.city
            """
        ),
        encoding="utf-8",
    )

    result = _run_typechecker(
        ["ty", "check", str(package / "consumer.py")],
        tmp_path,
        repo_root,
    )
    assert result.returncode == 0, result.stdout + result.stderr
