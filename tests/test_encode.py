from dataclasses import is_dataclass

import pytest
from pydantic import BaseModel, ValidationError

from app.encode import DataclassRenderer, PydanticRenderer, UNSET, api, build_entity
from app.views import views_for


def build_user_api(renderer):
    from dataclasses import dataclass

    @dataclass(kw_only=True)
    class Address:
        city: str
        zip: str

    @dataclass(kw_only=True)
    class User:
        name: str
        email: str
        address: Address

    user = build_entity(User)
    views = views_for(User)

    return api(
        user,
        renderer=renderer,
        create=views.name + views.email + views.address.city + views.address.zip,
        read=views.name + views.address.city,
        update=views.name + views.address.city,
    )


def test_pydantic_renderer_generates_operation_models():
    user_api = build_user_api(PydanticRenderer())

    assert issubclass(user_api.create_model, BaseModel)
    assert issubclass(user_api.read_model, BaseModel)
    assert issubclass(user_api.update_model, BaseModel)

    assert user_api.create_model.__name__ == "UserCreate"
    assert user_api.read_model.__name__ == "UserRead"
    assert user_api.update_model.__name__ == "UserUpdate"


def test_pydantic_create_requires_projected_fields():
    user_api = build_user_api(PydanticRenderer())

    with pytest.raises(ValidationError):
        user_api.create(name="Sam")

    created = user_api.create(
        name="Sam",
        email="sam@example.com",
        address={"city": "Paris", "zip": "75001"},
    )

    assert created.name == "Sam"
    assert created.address.city == "Paris"
    assert created.address.zip == "75001"


def test_pydantic_update_uses_unset_vs_none_semantics():
    user_api = build_user_api(PydanticRenderer())

    empty_update = user_api.update()
    assert empty_update.name is None
    assert empty_update.address is None
    assert empty_update.model_fields_set == set()
    assert empty_update.model_dump(exclude_unset=True) == {}

    explicit_null_update = user_api.update(name=None)
    assert explicit_null_update.name is None
    assert explicit_null_update.model_fields_set == {"name"}
    assert explicit_null_update.model_dump(exclude_unset=True) == {"name": None}

    nested_update = user_api.update(address={"city": "Paris"})
    assert nested_update.address.city == "Paris"
    assert nested_update.address.model_fields_set == {"city"}
    assert nested_update.model_dump(exclude_unset=True) == {
        "address": {"city": "Paris"},
    }


def test_dataclass_renderer_generates_dataclass_operation_models():
    user_api = build_user_api(DataclassRenderer())

    assert is_dataclass(user_api.create_model)
    assert is_dataclass(user_api.read_model)
    assert is_dataclass(user_api.update_model)

    created = user_api.create(
        name="Sam",
        email="sam@example.com",
        address={"city": "Paris", "zip": "75001"},
    )

    assert created.name == "Sam"
    assert is_dataclass(created.address)
    assert created.address.city == "Paris"
    assert created.address.zip == "75001"


def test_dataclass_update_uses_unset_sentinel():
    user_api = build_user_api(DataclassRenderer())

    empty_update = user_api.update()
    assert empty_update.name is UNSET
    assert empty_update.address is UNSET

    explicit_null_update = user_api.update(name=None)
    assert explicit_null_update.name is None
    assert explicit_null_update.address is UNSET

    nested_update = user_api.update(address={"city": "Paris"})
    assert nested_update.name is UNSET
    assert nested_update.address.city == "Paris"
    assert not hasattr(nested_update.address, "zip")
