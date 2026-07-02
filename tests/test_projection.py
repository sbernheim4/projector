import pytest

from app import optional, required, views_for
from app.encode import (
    DataclassRenderer,
    PydanticRenderer,
    api,
    build_entity,
    compile_projection,
)
from app.projection import Projection


def test_compile_projection_converts_flat_and_nested_paths():
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

    assert user_api.CreateModel.__name__ == "UserCreate"
    assert user_api.UpdateBirthdayModel.__name__ == "UserUpdateBirthday"

    created = user_api.Create(name="Sam", address={"city": "Paris"})
    updated = user_api.UpdateBirthday(address={"dob": "2000-01-01"})

    assert created.name == "Sam"
    assert updated.address.dob == "2000-01-01"


def test_api_accessor_style_follows_output_name_style():
    from dataclasses import dataclass

    @dataclass(kw_only=True)
    class User:
        name: str

    user = build_entity(User)
    views = views_for(User)

    snake_api = api(
        user,
        renderer=PydanticRenderer(),
        create=views.name,
    )
    pascal_api = api(
        user,
        renderer=PydanticRenderer(),
        Create=views.name,
    )
    mixed_api = api(
        user,
        renderer=PydanticRenderer(),
        renameUserCity=views.name,
    )

    assert hasattr(snake_api, "create")
    assert hasattr(snake_api, "create_model")
    assert hasattr(pascal_api, "Create")
    assert hasattr(pascal_api, "CreateModel")
    assert hasattr(mixed_api, "RenameUserCity")
    assert hasattr(mixed_api, "RenameUserCityModel")


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
