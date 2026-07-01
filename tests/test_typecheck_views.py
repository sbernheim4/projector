from __future__ import annotations

import os
import subprocess
import textwrap
from pathlib import Path


def _run_typechecker(command: list[str], cwd: Path, pythonpath: Path) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env["PYTHONPATH"] = f"{pythonpath / 'src'}:{pythonpath}"
    return subprocess.run(
        command,
        cwd=cwd,
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )


def test_typecheckers_reject_missing_view_attributes(tmp_path: Path):
    repo_root = Path(__file__).resolve().parents[1]
    package = tmp_path / "sample"
    package.mkdir()
    (package / "__init__.py").write_text("", encoding="utf-8")

    (package / "domain_models.py").write_text(
        textwrap.dedent(
            """
            from dataclasses import dataclass

            from app import views_for


            @dataclass(kw_only=True)
            class Address:
                city: str
                zip: str


            @dataclass(kw_only=True)
            class User:
                address: Address


            user_views = views_for(User)
            """
        ),
        encoding="utf-8",
    )
    (package / "domain_models.pyi").write_text(
        textwrap.dedent(
            """
            from typing import Any, overload

            from app.projection import Leaf


            class Address:
                city: str
                zip: str


            class AddressView:
                city: Leaf[str]
                zip: Leaf[str]


            class User:
                address: Address


            class UserView:
                address: AddressView


            user_views: UserView


            @overload
            def views_for(model_cls: type[Address]) -> AddressView: ...


            @overload
            def views_for(model_cls: type[User]) -> UserView: ...


            def views_for(model_cls: type[object]) -> Any: ...
            """
        ),
        encoding="utf-8",
    )
    (package / "api.py").write_text(
        textwrap.dedent(
            """
            from sample.domain_models import user_views


            _ok = user_views.address.city
            _bad = user_views.address.zi
            """
        ),
        encoding="utf-8",
    )

    ty_result = _run_typechecker(["ty", "check", str(package / "api.py")], tmp_path, repo_root)
    assert ty_result.returncode != 0
    assert "zi" in ty_result.stdout + ty_result.stderr
