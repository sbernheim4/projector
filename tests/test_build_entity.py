from typing import TypedDict

import attrs
from pydantic import BaseModel

from projector.encode import Entity, Field, build_entity


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

    import pytest

    with pytest.raises(TypeError, match="No source adapter found"):
        build_entity(Empty, adapters=())
