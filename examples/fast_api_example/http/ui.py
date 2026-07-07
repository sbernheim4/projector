from fastapi import APIRouter
from fastapi.responses import HTMLResponse

from ..projects.sql_queries import LIST_PROJECTS
from ..users.sql_queries import LIST_USERS
from ..db import conn

router: APIRouter = APIRouter()


@router.get("/")
def root() -> HTMLResponse:
    users = conn.execute(LIST_USERS).fetchall()
    projects = conn.execute(LIST_PROJECTS).fetchall()
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

            <h2>Create project</h2>
            <button onclick='createProject()'>Create demo project</button>

            <h2>Rename city command</h2>
            <button onclick='renameCity()'>Rename city for user 1</button>

            <h2>Current users</h2>
            <ul>__ROWS__</ul>

            <h2>Current projects</h2>
            <ul>__PROJECT_ROWS__</ul>

            <h2>Selected user</h2>
            <pre id="selected-user">Click a user to load its details.</pre>

            <h2>Selected project</h2>
            <pre id="selected-project">Click a project to load its details.</pre>

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

              async function loadProject(projectId) {
                const response = await fetch(`/projects/${projectId}`);
                const project = await response.json();
                document.getElementById('selected-project').textContent = JSON.stringify(project, null, 2);
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

              function wireProjectButtons() {
                document.querySelectorAll('.load-project').forEach((button) => {
                  button.addEventListener('click', async () => {
                    await loadProject(button.dataset.projectId);
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

              async function createProject() {
                const suffix = Math.floor(Math.random() * 10000);
                await fetch('/projects', {
                  method: 'POST',
                  headers: {'Content-Type': 'application/json'},
                  body: JSON.stringify({
                    name: `Project ${suffix}`,
                    description: 'Demo project',
                    task: {
                      title: randomChoice(['Draft spec', 'Implement API', 'Write tests']),
                      done: false,
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
              wireProjectButtons();
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
    html = html.replace(
        "__PROJECT_ROWS__",
        "".join(
            f"""<li>
              <button type="button" class="load-project" data-project-id="{row["id"]}">#{row["id"]}: {row["name"]} - {row["description"]} ({row["task_title"]}, done={row["task_done"]})</button>
            </li>"""
            for row in projects
        ),
    )
    return HTMLResponse(html)
