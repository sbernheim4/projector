from dataclasses import dataclass
from typing import Annotated, TypedDict, get_args, get_type_hints

import attrs
import pytest
from pydantic import BaseModel, Field as PydanticField, ValidationError

from projector import views_for
from projector.encode import (
    AttrsRenderer,
    DataclassRenderer,
    Field,
    PydanticRenderer,
    TypedDictRenderer,
    build_entity,
    project,
)


def test_build_entity_preserves_annotated_metadata_from_dataclasses():
    email_metadata = PydanticField(description="Primary email")
    city_metadata = PydanticField(description="City")

    @dataclass(kw_only=True)
    class Address:
        city: Annotated[str, city_metadata]

    @dataclass(kw_only=True)
    class User:
        email: Annotated[str | None, email_metadata]
        address: Annotated[Address, PydanticField(description="Mailing address")]

    entity = build_entity(User)

    email = entity.fields["email"]
    assert isinstance(email, Field)
    assert email.type_ is str
    assert email.nullable is True
    assert email.metadata == (email_metadata,)

    address = entity.fields["address"]
    assert address.metadata[0].description == "Mailing address"
    city = address.fields["city"]
    assert city.metadata == (city_metadata,)


def test_build_entity_preserves_annotated_metadata_from_all_type_hint_sources():
    plain_metadata = PydanticField(description="Plain")
    attrs_metadata = PydanticField(description="Attrs")
    typeddict_metadata = PydanticField(description="TypedDict")

    class PlainUser:
        name: Annotated[str, plain_metadata]

    @attrs.define
    class AttrsUser:
        name: Annotated[str, attrs_metadata]

    class TypedDictUser(TypedDict):
        name: Annotated[str, typeddict_metadata]

    assert build_entity(PlainUser).fields["name"].metadata == (plain_metadata,)
    assert build_entity(AttrsUser).fields["name"].metadata == (attrs_metadata,)
    assert build_entity(TypedDictUser).fields["name"].metadata == (typeddict_metadata,)


def test_pydantic_source_model_field_metadata_survives_projection():
    class User(BaseModel):
        name: Annotated[
            str,
            PydanticField(min_length=2, description="Display name"),
        ]

    views = views_for(User)
    user_models = project(
        User,
        renderer=PydanticRenderer(),
        Create=views.name,
    )

    name_schema = user_models.CreateModel.model_json_schema()["properties"]["name"]
    assert name_schema["description"] == "Display name"
    assert name_schema["minLength"] == 2

    with pytest.raises(ValidationError):
        user_models.Create(name="x")


def test_dataclass_annotated_metadata_survives_pydantic_projection():
    @dataclass(kw_only=True)
    class User:
        name: Annotated[
            str,
            PydanticField(min_length=2, description="Display name"),
        ]

    views = views_for(User)
    user_models = project(
        User,
        renderer=PydanticRenderer(),
        Create=views.name,
    )

    name_schema = user_models.CreateModel.model_json_schema()["properties"]["name"]
    assert name_schema["description"] == "Display name"
    assert name_schema["minLength"] == 2

    with pytest.raises(ValidationError):
        user_models.Create(name="x")


def test_all_type_hint_sources_preserve_metadata_in_pydantic_projection():
    plain_marker = PydanticField(description="Plain name")
    attrs_marker = PydanticField(description="Attrs name")
    typeddict_marker = PydanticField(description="TypedDict name")

    class PlainUser:
        name: Annotated[str, plain_marker]

    @attrs.define
    class AttrsUser:
        name: Annotated[str, attrs_marker]

    class TypedDictUser(TypedDict):
        name: Annotated[str, typeddict_marker]

    for model_cls, description in (
        (PlainUser, "Plain name"),
        (AttrsUser, "Attrs name"),
        (TypedDictUser, "TypedDict name"),
    ):
        views = views_for(model_cls)
        user_models = project(
            model_cls,
            renderer=PydanticRenderer(),
            Create=views.name,
        )

        name_schema = user_models.CreateModel.model_json_schema()["properties"]["name"]
        assert name_schema["description"] == description


def test_non_pydantic_renderers_preserve_annotated_output_annotations():
    marker = PydanticField(description="Display name")

    @dataclass(kw_only=True)
    class User:
        name: Annotated[str, marker]

    views = views_for(User)

    dataclass_models = project(
        User,
        renderer=DataclassRenderer(),
        Create=views.name,
    )
    attrs_models = project(
        User,
        renderer=AttrsRenderer(),
        Create=views.name,
    )
    typeddict_models = project(
        User,
        renderer=TypedDictRenderer(),
        Create=views.name,
    )

    dataclass_name_type = get_type_hints(
        dataclass_models.CreateModel, include_extras=True
    )["name"]
    attrs_name_type = get_type_hints(attrs_models.CreateModel, include_extras=True)[
        "name"
    ]
    typeddict_name_type = typeddict_models.CreateModel.__annotations__["name"]

    assert get_args(dataclass_name_type) == (str, marker)
    assert get_args(attrs_name_type) == (str, marker)
    assert get_args(typeddict_name_type) == (str, marker)
