from typing import Any

import sqlite3


def row_to_project(row: sqlite3.Row) -> dict[str, Any]:
    return {
        "id": row["id"],
        "name": row["name"],
        "description": row["description"],
        "task": {
            "title": row["task_title"],
            "done": bool(row["task_done"]),
        },
    }
