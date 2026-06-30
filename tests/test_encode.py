from dataclasses import is_dataclass
from typing import TypedDict

import attrs
import pytest
from pydantic import BaseModel, ValidationError

from app.encode import (
    DataclassRenderer,
    AttrsRenderer,
    Entity,
    Field,
    Leaf,
    PydanticRenderer,
    UNSET,
    api,
    build_entity,
    compile_projection,
)
from app import optional, required, views_for


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


def test_build_entity_supports_pydantic_source_models():
    class Address(BaseModel):
        city: str
        zip: str

    class User(BaseModel):
        name: str
        email: str
        address: Address

    entity = build_entity(User)

    assert entity.name == "User"
    assert isinstance(entity.fields["name"], Field)
    assert entity.fields["name"].type_ is str
    assert isinstance(entity.fields["address"], Entity)
    assert entity.fields["address"].name == "Address"
    assert entity.fields["address"].fields["city"].type_ is str


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


def test_build_entity_supports_plain_annotated_classes():
    class Address:
        city: str
        zip: str

    class User:
        name: str
        address: Address

    entity = build_entity(User)

    assert entity.name == "User"
    assert entity.fields["name"].type_ is str
    assert isinstance(entity.fields["address"], Entity)
    assert entity.fields["address"].fields["zip"].type_ is str


def test_plain_annotated_classes_can_render_dataclass_models():
    class Address:
        city: str

    class User:
        name: str
        address: Address

    user = build_entity(User)
    views = views_for(User)
    user_api = api(
        user,
        renderer=DataclassRenderer(),
        create=views.name + views.address.city,
        update=views.name + views.address.city,
    )

    created = user_api.create(name="Sam", address={"city": "Paris"})
    updated = user_api.update()

    assert is_dataclass(user_api.create_model)
    assert created.address.city == "Paris"
    assert updated.name is UNSET
    assert updated.address is UNSET


def test_api_supports_named_outputs():
    from dataclasses import dataclass

    @dataclass(kw_only=True)
    class Address:
        city: str
        dob: str

    @dataclass(kw_only=True)
    class User:
        name: str
        address: Address

    user = build_entity(User)
    views = views_for(User)

    user_api = api(
        user,
        renderer=PydanticRenderer(),
        Create=views.name + views.address.city,
        UpdateBirthday=views.address.dob,
    )

    assert user_api.Create_model.__name__ == "UserCreate"
    assert user_api.UpdateBirthday_model.__name__ == "UserUpdateBirthday"

    created = user_api.Create(name="Sam", address={"city": "Paris"})
    updated = user_api.UpdateBirthday(address={"dob": "2000-01-01"})

    assert created.name == "Sam"
    assert updated.address.dob == "2000-01-01"


def test_build_entity_supports_typed_dict_models():
    class Address(TypedDict):
        city: str
        zip: str

    class User(TypedDict):
        name: str
        address: Address

    entity = build_entity(User)

    assert entity.name == "User"
    assert isinstance(entity.fields["name"], Field)
    assert entity.fields["name"].type_ is str
    assert isinstance(entity.fields["address"], Entity)
    assert entity.fields["address"].name == "Address"
    assert entity.fields["address"].fields["city"].type_ is str


def test_typed_dict_models_can_render_dataclass_operation_models():
    class Address(TypedDict):
        city: str
        zip: str

    class User(TypedDict):
        name: str
        address: Address

    user = build_entity(User)
    views = views_for(User)
    user_api = api(
        user,
        renderer=DataclassRenderer(),
        Create=views.name + views.address.city,
        Update=views.name + views.address.city,
    )

    created = user_api.Create(name="Sam", address={"city": "Paris"})
    updated = user_api.Update()

    assert is_dataclass(user_api.Create_model)
    assert created.address.city == "Paris"
    assert updated.name is UNSET
    assert updated.address is UNSET


def test_typed_dict_models_can_render_pydantic_operation_models():
    class Address(TypedDict):
        city: str
        zip: str

    class User(TypedDict):
        name: str
        address: Address

    user = build_entity(User)
    views = views_for(User)
    user_api = api(
        user,
        renderer=PydanticRenderer(),
        Create=views.name + views.address.city,
        Update=views.name + views.address.city,
    )

    created = user_api.Create(name="Sam", address={"city": "Paris"})
    updated = user_api.Update()

    assert issubclass(user_api.Create_model, BaseModel)
    assert created.address.city == "Paris"
    assert updated.model_dump(exclude_unset=True) == {}


def test_build_entity_supports_attrs_models():
    @attrs.define
    class Address:
        city: str
        zip: str

    @attrs.define
    class User:
        name: str
        address: Address

    entity = build_entity(User)

    assert entity.name == "User"
    assert entity.fields["name"].type_ is str
    assert isinstance(entity.fields["address"], Entity)
    assert entity.fields["address"].name == "Address"
    assert entity.fields["address"].fields["zip"].type_ is str


def test_attrs_models_can_render_dataclass_operation_models():
    @attrs.define
    class Address:
        city: str
        zip: str

    @attrs.define
    class User:
        name: str
        address: Address

    user = build_entity(User)
    views = views_for(User)
    user_api = api(
        user,
        renderer=DataclassRenderer(),
        Create=views.name + views.address.city,
        Update=views.name + views.address.city,
    )

    created = user_api.Create(name="Sam", address={"city": "Paris"})
    updated = user_api.Update()

    assert is_dataclass(user_api.Create_model)
    assert created.address.city == "Paris"
    assert updated.name is UNSET
    assert updated.address is UNSET


def test_attrs_models_can_render_attrs_operation_models():
    @attrs.define
    class Address:
        city: str
        zip: str

    @attrs.define
    class User:
        name: str
        address: Address

    user = build_entity(User)
    views = views_for(User)
    user_api = api(
        user,
        renderer=AttrsRenderer(),
        Create=views.name + views.address.city,
        Update=views.name + views.address.city,
    )

    created = user_api.Create(name="Sam", address={"city": "Paris"})
    updated = user_api.Update(name="Sam")

    assert attrs.has(user_api.Create_model)
    assert created.address.city == "Paris"
    assert updated.name == "Sam"
    assert updated.address is None


def test_build_entity_supports_mixed_nested_source_models():
    from dataclasses import dataclass

    class Coordinates(BaseModel):
        lat: float
        lng: float

    @dataclass(kw_only=True)
    class Address:
        city: str
        coordinates: Coordinates

    class User:
        name: str
        address: Address

    entity = build_entity(User)

    assert isinstance(entity.fields["address"], Entity)
    coordinates = entity.fields["address"].fields["coordinates"]
    assert isinstance(coordinates, Entity)
    assert coordinates.fields["lat"].type_ is float
    assert coordinates.fields["lng"].type_ is float


def test_build_entity_accepts_custom_source_adapter():
    class ExternalModel:
        pass

    class ExternalAdapter:
        def matches(self, cls):
            return cls is ExternalModel

        def name_for(self, cls):
            return "External"

        def fields_for(self, cls):
            return {"id": int, "label": str}

    entity = build_entity(ExternalModel, adapters=(ExternalAdapter(),))

    assert entity.name == "External"
    assert entity.fields["id"].type_ is int
    assert entity.fields["label"].type_ is str


def test_build_entity_rejects_unknown_models():
    class Empty:
        pass

    with pytest.raises(TypeError, match="No source adapter found"):
        build_entity(Empty, adapters=())


def test_compile_projection_converts_flat_and_nested_paths():
    from app.projection import Projection

    projection = Projection([["name"], ["address", "city"]])

    assert compile_projection(projection) == {
        "name": True,
        "address": {
            "city": True,
        },
    }


def test_compile_projection_rejects_unknown_input():
    with pytest.raises(TypeError, match="Cannot convert"):
        compile_projection(object())


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


def test_nullable_subtree_remains_optional_for_dataclass_output():
    from dataclasses import dataclass

    @dataclass(kw_only=True)
    class Address:
        city: str

    @dataclass(kw_only=True)
    class User:
        address: Address | None

    user = build_entity(User)
    views = views_for(User)
    user_api = api(
        user,
        renderer=DataclassRenderer(),
        create=views.address.city,
    )

    created = user_api.create(address=None)
    assert created.address is None


def test_nullable_subtree_remains_optional_for_attrs_output():
    @attrs.define
    class Address:
        city: str

    @attrs.define
    class User:
        address: Address | None

    user = build_entity(User)
    views = views_for(User)
    user_api = api(
        user,
        renderer=AttrsRenderer(),
        create=views.address.city,
    )

    created = user_api.create(address=None)
    assert created.address is None
