import uvicorn

from fastapi import FastAPI
from .ui import router as ui_router
from .projects import router as projects_router
from .users import router as users_router

from .. import db


def create_app() -> FastAPI:
    app = FastAPI(title="Projector FastAPI example")
    db.init_db(db.conn)

    app.include_router(ui_router)
    app.include_router(projects_router)
    app.include_router(users_router)
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
