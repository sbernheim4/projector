import uvicorn

from fastapi import FastAPI

from . import db
from .api.ui import configure_ui_routes, router as ui_router
from .api.users import configure_user_routes, router as user_router


def create_app() -> FastAPI:
    app = FastAPI(title="Projector FastAPI example")
    conn = db.connect()
    db.init_db(conn)

    configure_ui_routes(conn)
    configure_user_routes(conn)

    app.include_router(ui_router)
    app.include_router(user_router)
    return app


app = create_app()


def main() -> None:
    uvicorn.run(
        "examples.fast_api_example.main:app",
        host="127.0.0.1",
        port=8080,
        reload=True,
        reload_dirs=["src", "examples/fast_api_example"],
    )


if __name__ == "__main__":
    main()
