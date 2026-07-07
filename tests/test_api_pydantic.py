import pytest
from pydantic import BaseModel, ValidationError

from app.encode import PydanticRenderer, api
from app import optional, required, views_for

from tests.helpers import build_user_api


def test_pydantic_renderer_generates_operation_models():
    user_api = build_user_api(PydanticRenderer())

    assert issubclass(user_api.CreateModel, BaseModel)
    assert issubclass(user_api.ReadModel, BaseModel)
    assert issubclass(user_api.UpdateModel, BaseModel)

    assert user_api.CreateModel.__name__ == "UserCreate"
    assert user_api.ReadModel.__name__ == "UserRead"
    assert user_api.UpdateModel.__name__ == "UserUpdate"


def test_pydantic_create_requires_projected_fields():
    user_api = build_user_api(PydanticRenderer())

    with pytest.raises(ValidationError):
        user_api.Create(name="Sam")

    created = user_api.Create(
        name="Sam",
        email="sam@example.com",
        address={"city": "Paris", "zip": "75001"},
    )

    assert created.name == "Sam"
    assert created.address.city == "Paris"
    assert created.address.zip == "75001"


def test_pydantic_update_uses_unset_vs_none_semantics():
    user_api = build_user_api(PydanticRenderer())

    empty_update = user_api.Update()
    assert empty_update.name is None
    assert empty_update.address is None
    assert empty_update.model_fields_set == set()
    assert empty_update.model_dump(exclude_unset=True) == {}

    explicit_null_update = user_api.Update(name=None)
    assert explicit_null_update.name is None
    assert explicit_null_update.model_fields_set == {"name"}
    assert explicit_null_update.model_dump(exclude_unset=True) == {"name": None}

    nested_update = user_api.Update(address={"city": "Paris"})
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

    views = views_for(User)
    user_api = api(
        User,
        renderer=PydanticRenderer(),
        Create=views.name + views.address.city,
        Update=views.email + views.address.zip,
        Read=views.name + views.email + views.address.city,
    )

    created = user_api.Create(name="Sam", address={"city": "Paris"})
    updated = user_api.Update(address={"zip": None})

    assert created.name == "Sam"
    assert created.address.city == "Paris"
    assert updated.model_dump(exclude_unset=True) == {"address": {"zip": None}}


def test_required_wrapper_makes_nullable_subtree_required_in_pydantic():
    class Address(BaseModel):
        city: str

    class User(BaseModel):
        address: Address | None

    views = views_for(User)
    user_api = api(
        User,
        renderer=PydanticRenderer(),
        Create=required(views.address.city),
    )

    with pytest.raises(ValidationError):
        user_api.Create(address=None)

    created = user_api.Create(address={"city": "Paris"})
    assert created.address.city == "Paris"


def test_optional_wrapper_keeps_nullable_subtree_optional_in_pydantic():
    class Address(BaseModel):
        city: str

    class User(BaseModel):
        address: Address | None

    views = views_for(User)
    user_api = api(
        User,
        renderer=PydanticRenderer(),
        Create=optional(views.address.city),
    )

    created = user_api.Create(address=None)
    assert created.address is None


def test_optional_projections_can_be_composed_for_pydantic_output():
    class Address(BaseModel):
        city: str

    class User(BaseModel):
        name: str
        address: Address | None

    views = views_for(User)
    user_api = api(
        User,
        renderer=PydanticRenderer(),
        Create=optional(views.name) + optional(views.address.city),
    )

    created = user_api.Create(name="Sam", address=None)
    assert created.name == "Sam"
    assert created.address is None
