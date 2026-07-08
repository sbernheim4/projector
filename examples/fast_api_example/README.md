# FastAPI example

This example shows Projector deriving endpoint-specific FastAPI request and
response models from domain dataclasses.

The user and project domains each define one source model, then derive separate
models for create requests, read responses, list responses, partial updates, and
command payloads.

Run the app from the repository root:

```bash
PYTHONPATH=src .venv/bin/python -m examples.fast_api_example.http.main
```

Regenerate the editor/type-checker stubs after changing the domain models:

```bash
PYTHONPATH=src:. .venv/bin/projector type-stubs \
  examples/fast_api_example/projects/models.py \
  examples/fast_api_example/users/models.py
```

Useful routes:

- `POST /users` accepts `UserCreate` and returns `UserRead`.
- `GET /users` returns `list[UserListItem]`.
- `GET /users/{user_id}` returns `UserRead`.
- `PATCH /users/{user_id}` accepts `UserUpdate` and returns `UserRead`.
- `POST /users/{user_id}/commands/rename-city` accepts `UserRenameCity`.
- `POST /projects` accepts `ProjectCreate` and returns `ProjectRead`.
- `GET /projects` returns `list[ProjectListItem]`.
- `PATCH /projects/{project_id}` accepts `ProjectUpdate` and returns
  `ProjectRead`.
