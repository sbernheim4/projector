import sqlite3
from contextlib import contextmanager
from typing import Iterator

from .query import TypedConnection


def connect() -> TypedConnection:
    conn = sqlite3.connect(":memory:", check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return TypedConnection(conn)


conn = connect()


def init_db(conn: TypedConnection) -> None:
    conn.execute(
        """
        create table if not exists users (
            id integer primary key autoincrement,
            name text not null,
            email text not null,
            city text not null,
            zip text not null
        )
        """,
    )
    conn.execute(
        """
        create table if not exists projects (
            id integer primary key autoincrement,
            name text not null,
            description text not null,
            task_title text not null,
            task_done integer not null default 0
        )
        """,
    )
    conn.commit()


@contextmanager
def transaction(conn: TypedConnection) -> Iterator[TypedConnection]:
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
