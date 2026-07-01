import uvicorn
import sqlite3
from typing import Any, cast
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse

from app import api, build_entity, renderer, views_for

from . import db
from .domain_models import User
from .sql_queries import (
    CREATE_USER,
    DELETE_USER,
    GET_USER,
    LIST_USERS,
    RENAME_CITY,
    UPDATE_USER,
)


app = FastAPI(title="Projector FastAPI example")
conn = db.connect()
db.init_db(conn)

user_entity = build_entity(User)
user_views = views_for(User)

UserAPI = api(
    user_entity,
    renderer=renderer.Pydantic,
    create=user_views.name
    + user_views.email
    + user_views.address.city
    + user_views.address.zip,
    read=user_views.name
    + user_views.email
    + user_views.address.city
    + user_views.address.zip,
    update=user_views.name
    + user_views.email
    + user_views.address.city
    + user_views.address.zip,
)

CommandAPI = api(
    user_entity,
    renderer=renderer.Pydantic,
    rename_city=user_views.address.city,
)

UserCreateModel = UserAPI.create_model
UserReadModel = UserAPI.read_model
UserUpdateModel = UserAPI.update_model
RenameCityCommandModel = CommandAPI.rename_city_model


def row_to_user(row: sqlite3.Row) -> dict[str, Any]:
    return {
        "id": row["id"],
        "name": row["name"],
        "email": row["email"],
        "address": {
            "city": row["city"],
            "zip": row["zip"],
        },
    }


@app.get("/")
def root() -> HTMLResponse:
    users = conn.execute(LIST_USERS).fetchall()
    rows = "".join(
        f"<li>#{row['id']}: {row['name']} ({row['email']}) - {row['city']}, {row['zip']}</li>"
        for row in users
    )
    html = """
    <!doctype html>
    <html>
      <head>
        <title>Projector FastAPI example</title>
        <style>
          body { font-family: sans-serif; margin: 2rem; max-width: 960px; }
          form { margin-bottom: 1rem; padding: 1rem; border: 1px solid #ddd; }
          label { display: block; margin-top: 0.5rem; }
          input { display: block; margin-top: 0.25rem; padding: 0.4rem; width: 320px; }
          button { margin-top: 0.75rem; padding: 0.5rem 0.9rem; }
        </style>
      </head>
        <body>
        <h1>Projector FastAPI example</h1>
        <p>Use the forms below to exercise the CRUD and command endpoints.</p>
        <h2>Create user</h2>
        <button onclick='createUser()'>Create demo user</button>

        <h2>Rename city command</h2>
        <button onclick='renameCity()'>Rename city for user 1</button>

        <h2>Current users</h2>
        <ul>__ROWS__</ul>

        <h2>Selected user</h2>
        <pre id="selected-user">Click a user to load its details.</pre>

        <h2>Notes</h2>
        <ul>
          <li>GET <code>/users</code> lists users.</li>
          <li>GET <code>/users/1</code> reads a user.</li>
          <li>PUT <code>/users/1</code> updates a user.</li>
          <li>DELETE <code>/users/1</code> deletes a user.</li>
        </ul>
        <script>
          function randomChoice(values) {
            return values[Math.floor(Math.random() * values.length)];
          }

          async function loadUser(userId) {
            const response = await fetch(`/users/${userId}`);
            const user = await response.json();
            document.getElementById('selected-user').textContent = JSON.stringify(user, null, 2);
          }

          async function deleteUser(userId) {
            await fetch(`/users/${userId}`, {
              method: 'DELETE',
            });
            window.location.reload();
          }

          function wireUserButtons() {
            document.querySelectorAll('.load-user').forEach((button) => {
              button.addEventListener('click', async () => {
                await loadUser(button.dataset.userId);
              });
            });

            document.querySelectorAll('.delete-user').forEach((button) => {
              button.addEventListener('click', async () => {
                await deleteUser(button.dataset.userId);
              });
            });
          }

          async function createUser() {
            const suffix = Math.floor(Math.random() * 10000);
            await fetch('/users', {
              method: 'POST',
              headers: {'Content-Type': 'application/json'},
              body: JSON.stringify({
                name: `User ${suffix}`,
                email: `user${suffix}@example.com`,
                address: {
                  city: randomChoice(['Paris', 'Lyon', 'Berlin', 'Tokyo']),
                  zip: String(70000 + Math.floor(Math.random() * 2000)),
                },
              }),
            });
            window.location.reload();
          }

          async function renameCity() {
            await fetch('/users/1/commands/rename-city', {
              method: 'POST',
              headers: {'Content-Type': 'application/json'},
              body: JSON.stringify({address: {city: 'Lyon'}}),
            });
            window.location.reload();
          }

          wireUserButtons();
        </script>
      </body>
    </html>
    """
    html = html.replace(
        "__ROWS__",
        "".join(
            f"""<li>
              <button type="button" class="load-user" data-user-id="{row["id"]}">#{row["id"]}: {row["name"]} ({row["email"]}) - {row["city"]}, {row["zip"]}</button>
              <button type="button" class="delete-user" data-user-id="{row["id"]}">Delete</button>
            </li>"""
            for row in users
        ),
    )
    return HTMLResponse(html)


@app.post("/users", response_model=UserCreateModel)
def create_user(user: UserCreateModel):
    payload = user.model_dump()
    cur = conn.execute(
        CREATE_USER,
        {
            "name": payload["name"],
            "email": payload["email"],
            "city": payload["address"]["city"],
            "zip": payload["address"]["zip"],
        },
    )
    conn.commit()
    row = conn.execute(GET_USER, {"id": cur.lastrowid}).fetchone()
    return row_to_user(cast(sqlite3.Row, row))


@app.get("/users", response_model=list[UserReadModel])
def list_users():
    rows = conn.execute(LIST_USERS).fetchall()
    return [row_to_user(row) for row in rows]


@app.get("/users/{user_id}", response_model=UserReadModel)
def get_user(user_id: int):
    row = conn.execute(GET_USER, {"id": user_id}).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="User not found")
    return row_to_user(cast(sqlite3.Row, row))


@app.put("/users/{user_id}", response_model=UserUpdateModel)
def update_user(user_id: int, user: UserUpdateModel):
    payload = user.model_dump()
    conn.execute(
        UPDATE_USER,
        {
            "id": user_id,
            "name": payload["name"],
            "email": payload["email"],
            "city": payload["address"]["city"],
            "zip": payload["address"]["zip"],
        },
    )
    conn.commit()
    row = conn.execute(GET_USER, {"id": user_id}).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="User not found")
    return row_to_user(cast(sqlite3.Row, row))


@app.delete("/users/{user_id}")
def delete_user(user_id: int):
    conn.execute(DELETE_USER, {"id": user_id})
    conn.commit()
    return {"deleted": True}


@app.post(
    "/users/{user_id}/commands/rename-city", response_model=RenameCityCommandModel
)
def rename_city(user_id: int, command: RenameCityCommandModel):
    conn.execute(
        RENAME_CITY,
        {
            "id": user_id,
            "city": command.address.city,
        },
    )
    conn.commit()
    row = conn.execute(GET_USER, {"id": user_id}).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="User not found")
    return {
        "address": {
            "city": cast(sqlite3.Row, row)["city"],
        }
    }


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
