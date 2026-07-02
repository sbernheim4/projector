from importlib import import_module
from typing import Any

import uvicorn

from fastapi import FastAPI

from .. import db


def _load(module_name: str) -> Any:
    return import_module(module_name, __package__)


project_http: Any = _load(".projects")
ui_http: Any = _load(".ui")
user_http: Any = _load(".users")


def create_app() -> FastAPI:
    app = FastAPI(title="Projector FastAPI example")
    db.init_db(db.conn)

    app.include_router(ui_http.router)
    app.include_router(project_http.router)
    app.include_router(user_http.router)
    return app


app = create_app()


def main() -> None:
    uvicorn.run(
        "examples.fast_api_example.http.main:app",
        host="127.0.0.1",
        port=8080,
        reload=True,
        reload_dirs=["src", "examples/fast_api_example"],
    )


if __name__ == "__main__":
    main()
