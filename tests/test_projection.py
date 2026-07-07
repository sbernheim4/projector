import pytest

from app import optional, required, views_for
from app.encode import (
    DataclassRenderer,
    PydanticRenderer,
    project,
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


def test_project_rejects_prebuilt_entities():
    from dataclasses import dataclass

    @dataclass(kw_only=True)
    class User:
        name: str

    entity = build_entity(User)
    views = views_for(User)

    with pytest.raises(TypeError, match="pass User, not build_entity"):
        project(
            entity,
            renderer=PydanticRenderer(),
            Create=views.name,
        )


def test_project_supports_named_outputs():
    from dataclasses import dataclass

    @dataclass(kw_only=True)
    class Address:
        city: str
        dob: str

    @dataclass(kw_only=True)
    class User:
        name: str
        address: Address

    views = views_for(User)

    user_models = project(
        User,
        renderer=PydanticRenderer(),
        Create=views.name + views.address.city,
        UpdateBirthday=views.address.dob,
    )

    assert user_models.CreateModel.__name__ == "UserCreate"
    assert user_models.UpdateBirthdayModel.__name__ == "UserUpdateBirthday"

    created = user_models.Create(name="Sam", address={"city": "Paris"})
    updated = user_models.UpdateBirthday(address={"dob": "2000-01-01"})

    assert created.name == "Sam"
    assert updated.address.dob == "2000-01-01"


def test_project_accessor_style_follows_output_name_style():
    from dataclasses import dataclass

    @dataclass(kw_only=True)
    class User:
        name: str

    views = views_for(User)

    snake_models = project(
        User,
        renderer=PydanticRenderer(),
        create=views.name,
    )
    pascal_models = project(
        User,
        renderer=PydanticRenderer(),
        Create=views.name,
    )
    mixed_models = project(
        User,
        renderer=PydanticRenderer(),
        renameUserCity=views.name,
    )

    assert hasattr(snake_models, "create")
    assert hasattr(snake_models, "create_model")
    assert hasattr(pascal_models, "Create")
    assert hasattr(pascal_models, "CreateModel")
    assert hasattr(mixed_models, "RenameUserCity")
    assert hasattr(mixed_models, "RenameUserCityModel")


def test_required_wrapper_works_for_dataclass_output():
    from dataclasses import dataclass

    @dataclass(kw_only=True)
    class Address:
        city: str

    @dataclass(kw_only=True)
    class User:
        address: Address | None

    views = views_for(User)
    user_models = project(
        User,
        renderer=DataclassRenderer(),
        Create=required(views.address.city),
    )

    created = user_models.Create(address={"city": "Paris"})
    assert created.address.city == "Paris"


def test_optional_wrapper_works_for_dataclass_output():
    from dataclasses import dataclass

    @dataclass(kw_only=True)
    class Address:
        city: str

    @dataclass(kw_only=True)
    class User:
        address: Address | None

    views = views_for(User)
    user_models = project(
        User,
        renderer=DataclassRenderer(),
        Create=optional(views.address.city),
    )

    created = user_models.Create(address=None)
    assert created.address is None
