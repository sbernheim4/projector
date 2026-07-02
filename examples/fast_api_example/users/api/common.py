from typing import Any

import sqlite3


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
