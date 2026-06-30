from app import optional, required, views_for
from app.encode import AttrsRenderer, api, build_entity


def test_build_entity_supports_attrs_models():
    import attrs

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
    assert entity.fields["address"].name == "Address"
    assert entity.fields["address"].fields["zip"].type_ is str


def test_attrs_models_can_render_attrs_operation_models():
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


def test_required_wrapper_works_for_attrs_output():
    import attrs

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
        create=required(views.address.city),
    )

    created = user_api.create(address={"city": "Paris"})
    assert created.address.city == "Paris"


def test_optional_wrapper_works_for_attrs_output():
    import attrs

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
        create=optional(views.address.city),
    )

    created = user_api.create(address=None)
    assert created.address is None


def test_nullable_subtree_remains_optional_for_attrs_output():
    import attrs

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
