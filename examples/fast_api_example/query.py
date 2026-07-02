from __future__ import annotations

from dataclasses import is_dataclass
import sqlite3
from typing import Any, Generic, TypeVar

ModelT = TypeVar("ModelT")


class SelectQuery(Generic[ModelT]):
    def __init__(
        self,
        conn: "TypedConnection",
        model_cls: type[ModelT],
        mapper: Any,
        table: str,
    ) -> None:
        self._conn = conn
        self._model_cls = model_cls
        self._mapper = mapper
        self._table = table
        self._filters: dict[str, Any] = {}

    def WHERE(self, **filters: Any) -> "SelectQuery[ModelT]":
        self._filters.update(filters)
        return self

    def one(self) -> ModelT | None:
        clause = ""
        params: dict[str, Any] = {}
        if self._filters:
            clause = " where " + " and ".join(f"{key} = :{key}" for key in self._filters)
            params.update(self._filters)

        row = self._conn.execute(
            f"select * from {self._table}{clause} limit 1",
            params,
        ).fetchone()
        if row is None:
            return None
        return self._mapper(row)


class TypedConnection:
    def __init__(self, conn: sqlite3.Connection) -> None:
        self._conn = conn
        self._mappers: dict[type[Any], tuple[str, Any]] = {}

    def register(self, model_cls: type[ModelT], table: str, mapper: Any) -> None:
        self._mappers[model_cls] = (table, mapper)

    def SELECT(self, model_cls: type[ModelT]) -> SelectQuery[ModelT]:
        table, mapper = self._mappers[model_cls]
        return SelectQuery(self, model_cls, mapper, table)

    def execute(self, *args: Any, **kwargs: Any):
        return self._conn.execute(*args, **kwargs)

    def commit(self) -> None:
        self._conn.commit()

    def rollback(self) -> None:
        self._conn.rollback()

    @property
    def row_factory(self):
        return self._conn.row_factory

    @row_factory.setter
    def row_factory(self, value):
        self._conn.row_factory = value

    def __getattr__(self, name: str) -> Any:
        return getattr(self._conn, name)


def is_model_instance(value: Any) -> bool:
    return is_dataclass(value) or hasattr(value, "__dict__")
