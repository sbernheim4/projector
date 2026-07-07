import pytest
from pydantic import BaseModel, ValidationError

from projector.encode import PydanticRenderer, project
from projector import optional, required, views_for

from tests.helpers import build_user_models


def test_pydantic_renderer_generates_operation_models():
    user_models = build_user_models(PydanticRenderer())

    assert issubclass(user_models.CreateModel, BaseModel)
    assert issubclass(user_models.ReadModel, BaseModel)
    assert issubclass(user_models.UpdateModel, BaseModel)

    assert user_models.CreateModel.__name__ == "UserCreate"
    assert user_models.ReadModel.__name__ == "UserRead"
    assert user_models.UpdateModel.__name__ == "UserUpdate"


def test_pydantic_create_requires_projected_fields():
    user_models = build_user_models(PydanticRenderer())

    with pytest.raises(ValidationError):
        user_models.Create(name="Sam")

    created = user_models.Create(
        name="Sam",
        email="sam@example.com",
        address={"city": "Paris", "zip": "75001"},
    )

    assert created.name == "Sam"
    assert created.address.city == "Paris"
    assert created.address.zip == "75001"


def test_pydantic_update_uses_unset_vs_none_semantics():
    user_models = build_user_models(PydanticRenderer())

    empty_update = user_models.Update()
    assert empty_update.name is None
    assert empty_update.address is None
    assert empty_update.model_fields_set == set()
    assert empty_update.model_dump(exclude_unset=True) == {}

    explicit_null_update = user_models.Update(name=None)
    assert explicit_null_update.name is None
    assert explicit_null_update.model_fields_set == {"name"}
    assert explicit_null_update.model_dump(exclude_unset=True) == {"name": None}

    nested_update = user_models.Update(address={"city": "Paris"})
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
    user_models = project(
        User,
        renderer=PydanticRenderer(),
        Create=views.name + views.address.city,
        Update=views.email + views.address.zip,
        Read=views.name + views.email + views.address.city,
    )

    created = user_models.Create(name="Sam", address={"city": "Paris"})
    updated = user_models.Update(address={"zip": None})

    assert created.name == "Sam"
    assert created.address.city == "Paris"
    assert updated.model_dump(exclude_unset=True) == {"address": {"zip": None}}


def test_required_wrapper_makes_nullable_subtree_required_in_pydantic():
    class Address(BaseModel):
        city: str

    class User(BaseModel):
        address: Address | None

    views = views_for(User)
    user_models = project(
        User,
        renderer=PydanticRenderer(),
        Create=required(views.address.city),
    )

    with pytest.raises(ValidationError):
        user_models.Create(address=None)

    created = user_models.Create(address={"city": "Paris"})
    assert created.address.city == "Paris"


def test_optional_wrapper_keeps_nullable_subtree_optional_in_pydantic():
    class Address(BaseModel):
        city: str

    class User(BaseModel):
        address: Address | None

    views = views_for(User)
    user_models = project(
        User,
        renderer=PydanticRenderer(),
        Create=optional(views.address.city),
    )

    created = user_models.Create(address=None)
    assert created.address is None


def test_optional_projections_can_be_composed_for_pydantic_output():
    class Address(BaseModel):
        city: str

    class User(BaseModel):
        name: str
        address: Address | None

    views = views_for(User)
    user_models = project(
        User,
        renderer=PydanticRenderer(),
        Create=optional(views.name) + optional(views.address.city),
    )

    created = user_models.Create(name="Sam", address=None)
    assert created.name == "Sam"
    assert created.address is None
