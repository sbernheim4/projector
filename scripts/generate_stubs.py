from __future__ import annotations

from pathlib import Path

from app.cli import main


def _domain_model_modules(root: Path) -> list[str]:
    return sorted(
        f"examples.fast_api_example.{path.parent.name}.models"
        for path in root.glob("*/models.py")
    )


def _http_module_modules(root: Path) -> list[str]:
    return sorted(
        f"examples.fast_api_example.http.{path.stem}"
        for path in root.glob("*.py")
        if path.stem != "main"
    )


def run() -> None:
    main(["stubs", "examples.demo_example.models"])

    for module in _domain_model_modules(Path("examples/fast_api_example")):
        main(["stubs", module])

    for module in _http_module_modules(Path("examples/fast_api_example/http")):
        main(["module-stubs", module])


if __name__ == "__main__":
    run()
