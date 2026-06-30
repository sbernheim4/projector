from typing import Any


class ValidationError(Exception): ...


class BaseModel:
    model_fields: dict[str, Any]
    model_fields_set: set[str]

    def __init__(self, **data: Any) -> None: ...
    def model_dump(self, *, exclude_unset: bool = ...) -> dict[str, Any]: ...


def create_model(__model_name: str, /, **field_definitions: Any) -> type[BaseModel]: ...
