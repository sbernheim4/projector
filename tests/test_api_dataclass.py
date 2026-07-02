from dataclasses import is_dataclass

from app import optional, required, views_for
from app.encode import DataclassRenderer, UNSET, api, build_entity

from tests.helpers import build_user_api


def test_dataclass_renderer_generates_dataclass_operation_models():
    user_api = build_user_api(DataclassRenderer())

    assert is_dataclass(user_api.CreateModel)
    assert is_dataclass(user_api.ReadModel)
    assert is_dataclass(user_api.UpdateModel)

    created = user_api.Create(
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

    empty_update = user_api.Update()
    assert empty_update.name is UNSET
    assert empty_update.address is UNSET

    explicit_null_update = user_api.Update(name=None)
    assert explicit_null_update.name is None
    assert explicit_null_update.address is UNSET

    nested_update = user_api.Update(address={"city": "Paris"})
    assert nested_update.name is UNSET
    assert nested_update.address.city == "Paris"
    assert not hasattr(nested_update.address, "zip")


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

    created = user_api.Create(name="Sam", address={"city": "Paris"})
    updated = user_api.Update()

    assert is_dataclass(user_api.CreateModel)
    assert created.address.city == "Paris"
    assert updated.name is UNSET
    assert updated.address is UNSET


def test_typed_dict_models_can_render_dataclass_operation_models():
    from typing import TypedDict

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

    assert is_dataclass(user_api.CreateModel)
    assert created.address.city == "Paris"
    assert updated.name is UNSET
    assert updated.address is UNSET


def test_attrs_models_can_render_dataclass_operation_models():
    import attrs

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

    assert is_dataclass(user_api.CreateModel)
    assert created.address.city == "Paris"
    assert updated.name is UNSET
    assert updated.address is UNSET


def test_required_wrapper_works_for_dataclass_output():
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
        Create=required(views.address.city),
    )

    created = user_api.Create(address={"city": "Paris"})
    assert created.address.city == "Paris"


def test_optional_wrapper_works_for_dataclass_output():
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
        Create=optional(views.address.city),
    )

    created = user_api.Create(address=None)
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
        Create=views.address.city,
    )

    created = user_api.Create(address=None)
    assert created.address is None


def test_optional_projections_can_be_composed_for_dataclass_output():
    from dataclasses import dataclass

    @dataclass(kw_only=True)
    class Address:
        city: str

    @dataclass(kw_only=True)
    class User:
        name: str
        address: Address | None

    user = build_entity(User)
    views = views_for(User)
    user_api = api(
        user,
        renderer=DataclassRenderer(),
        Create=optional(views.name) + optional(views.address.city),
    )

    created = user_api.Create(name="Sam", address=None)
    assert created.name == "Sam"
    assert created.address is None
