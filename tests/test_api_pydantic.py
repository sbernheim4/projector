import pytest
from pydantic import BaseModel, ValidationError

from app.encode import PydanticRenderer, api, build_entity
from app import optional, required, views_for

from tests.helpers import build_user_api


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


def test_pydantic_source_models_can_render_pydantic_operation_models():
    class Address(BaseModel):
        city: str
        zip: str

    class User(BaseModel):
        name: str
        email: str
        address: Address

    user = build_entity(User)
    views = views_for(User)
    user_api = api(
        user,
        renderer=PydanticRenderer(),
        create=views.name + views.address.city,
        update=views.email + views.address.zip,
        read=views.name + views.email + views.address.city,
    )

    created = user_api.create(name="Sam", address={"city": "Paris"})
    updated = user_api.update(address={"zip": None})

    assert created.name == "Sam"
    assert created.address.city == "Paris"
    assert updated.model_dump(exclude_unset=True) == {"address": {"zip": None}}


def test_required_wrapper_makes_nullable_subtree_required_in_pydantic():
    class Address(BaseModel):
        city: str

    class User(BaseModel):
        address: Address | None

    user = build_entity(User)
    views = views_for(User)
    user_api = api(
        user,
        renderer=PydanticRenderer(),
        create=required(views.address.city),
    )

    with pytest.raises(ValidationError):
        user_api.create(address=None)

    created = user_api.create(address={"city": "Paris"})
    assert created.address.city == "Paris"


def test_optional_wrapper_keeps_nullable_subtree_optional_in_pydantic():
    class Address(BaseModel):
        city: str

    class User(BaseModel):
        address: Address | None

    user = build_entity(User)
    views = views_for(User)
    user_api = api(
        user,
        renderer=PydanticRenderer(),
        create=optional(views.address.city),
    )

    created = user_api.create(address=None)
    assert created.address is None


def test_optional_projections_can_be_composed_for_pydantic_output():
    class Address(BaseModel):
        city: str

    class User(BaseModel):
        name: str
        address: Address | None

    user = build_entity(User)
    views = views_for(User)
    user_api = api(
        user,
        renderer=PydanticRenderer(),
        create=optional(views.name) + optional(views.address.city),
    )

    created = user_api.create(name="Sam", address=None)
    assert created.name == "Sam"
    assert created.address is None
