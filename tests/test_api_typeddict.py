from typing import TypedDict

from app import optional, required, views_for
from app.encode import TypedDictRenderer, api, build_entity

from tests.helpers import build_user_api


def test_typeddict_renderer_generates_typed_dict_operation_models():
    user_api = build_user_api(TypedDictRenderer())

    assert user_api.CreateModel.__name__ == "UserCreate"
    assert user_api.ReadModel.__name__ == "UserRead"
    assert user_api.UpdateModel.__name__ == "UserUpdate"
    assert user_api.CreateModel.__required_keys__ == frozenset(
        {"name", "email", "address"}
    )
    assert user_api.UpdateModel.__required_keys__ == frozenset()
    assert user_api.UpdateModel.__optional_keys__ == frozenset({"name", "address"})
    assert "name" in user_api.CreateModel.__annotations__
    assert "address" in user_api.CreateModel.__annotations__


def test_typeddict_source_models_can_render_typed_dict_operation_models():
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
        renderer=TypedDictRenderer(),
        Create=views.name + views.address.city,
        Update=views.name + views.address.city,
    )

    created = user_api.Create(name="Sam", address={"city": "Paris"})
    updated = user_api.Update(name="Sam")

    assert user_api.CreateModel.__required_keys__ == frozenset({"name", "address"})
    assert "address" in user_api.CreateModel.__annotations__
    assert created["address"]["city"] == "Paris"
    assert updated["name"] == "Sam"


def test_required_wrapper_works_for_typed_dict_output():
    class Address(TypedDict):
        city: str

    class User(TypedDict):
        address: Address | None

    user = build_entity(User)
    views = views_for(User)
    user_api = api(
        user,
        renderer=TypedDictRenderer(),
        Create=required(views.address.city),
    )

    assert user_api.CreateModel.__required_keys__ == frozenset({"address"})
    assert user_api.CreateModel.__optional_keys__ == frozenset()
    created = user_api.Create(address={"city": "Paris"})
    assert created["address"]["city"] == "Paris"


def test_optional_wrapper_works_for_typed_dict_output():
    class Address(TypedDict):
        city: str

    class User(TypedDict):
        address: Address | None

    user = build_entity(User)
    views = views_for(User)
    user_api = api(
        user,
        renderer=TypedDictRenderer(),
        Create=optional(views.address.city),
    )

    assert user_api.CreateModel.__required_keys__ == frozenset()
    assert user_api.CreateModel.__optional_keys__ == frozenset({"address"})
    created = user_api.Create(address=None)
    assert created["address"] is None


def test_nullable_subtree_remains_optional_for_typed_dict_output():
    class Address(TypedDict):
        city: str

    class User(TypedDict):
        address: Address | None

    user = build_entity(User)
    views = views_for(User)
    user_api = api(
        user,
        renderer=TypedDictRenderer(),
        Create=views.address.city,
    )

    assert user_api.CreateModel.__required_keys__ == frozenset({"address"})
    created = user_api.Create(address=None)
    assert created["address"] is None


def test_optional_projections_can_be_composed_for_typed_dict_output():
    class Address(TypedDict):
        city: str

    class User(TypedDict):
        name: str
        address: Address

    user = build_entity(User)
    views = views_for(User)
    user_api = api(
        user,
        renderer=TypedDictRenderer(),
        Create=optional(views.name) + optional(views.address.city),
    )

    assert user_api.CreateModel.__required_keys__ == frozenset()
    assert user_api.CreateModel.__optional_keys__ == frozenset({"name", "address"})
    created = user_api.Create(name="Sam", address={"city": "Paris"})
    assert created["name"] == "Sam"
    assert created["address"]["city"] == "Paris"


def test_optional_projections_can_be_composed_for_typed_dict_output_with_nullable_subtree():
    class Address(TypedDict):
        city: str

    class User(TypedDict):
        name: str
        address: Address | None

    user = build_entity(User)
    views = views_for(User)
    user_api = api(
        user,
        renderer=TypedDictRenderer(),
        Create=optional(views.name) + optional(views.address.city),
    )

    created = user_api.Create(name="Sam", address=None)
    assert created["name"] == "Sam"
    assert created["address"] is None
