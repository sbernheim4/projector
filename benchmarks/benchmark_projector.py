from __future__ import annotations

from argparse import ArgumentParser
from dataclasses import dataclass
import gc
import statistics
import time
from typing import Any, Callable, TypedDict

import attrs
from pydantic import BaseModel

from app import project, renderer, views_for


@dataclass(kw_only=True)
class DataclassAddress:
    street: str
    city: str
    state: str
    zip: str


@dataclass(kw_only=True)
class DataclassPreferences:
    newsletter: bool
    theme: str
    locale: str


@dataclass(kw_only=True)
class DataclassProfile:
    display_name: str
    bio: str
    preferences: DataclassPreferences


@dataclass(kw_only=True)
class DataclassUser:
    id: int
    name: str
    email: str
    address: DataclassAddress
    profile: DataclassProfile


@dataclass(kw_only=True)
class ManualDataclassAddress:
    street: str
    city: str
    state: str
    zip: str


@dataclass(kw_only=True)
class ManualDataclassPreferences:
    newsletter: bool
    theme: str
    locale: str


@dataclass(kw_only=True)
class ManualDataclassProfile:
    display_name: str
    bio: str
    preferences: ManualDataclassPreferences


@dataclass(kw_only=True)
class ManualDataclassUserCreate:
    id: int
    name: str
    email: str
    address: ManualDataclassAddress
    profile: ManualDataclassProfile


class PydanticAddress(BaseModel):
    street: str
    city: str
    state: str
    zip: str


class PydanticPreferences(BaseModel):
    newsletter: bool
    theme: str
    locale: str


class PydanticProfile(BaseModel):
    display_name: str
    bio: str
    preferences: PydanticPreferences


class PydanticUser(BaseModel):
    id: int
    name: str
    email: str
    address: PydanticAddress
    profile: PydanticProfile


class ManualPydanticAddress(BaseModel):
    street: str
    city: str
    state: str
    zip: str


class ManualPydanticPreferences(BaseModel):
    newsletter: bool
    theme: str
    locale: str


class ManualPydanticProfile(BaseModel):
    display_name: str
    bio: str
    preferences: ManualPydanticPreferences


class ManualPydanticUserCreate(BaseModel):
    id: int
    name: str
    email: str
    address: ManualPydanticAddress
    profile: ManualPydanticProfile


@attrs.define(kw_only=True)
class AttrsAddress:
    street: str
    city: str
    state: str
    zip: str


@attrs.define(kw_only=True)
class AttrsPreferences:
    newsletter: bool
    theme: str
    locale: str


@attrs.define(kw_only=True)
class AttrsProfile:
    display_name: str
    bio: str
    preferences: AttrsPreferences


@attrs.define(kw_only=True)
class AttrsUser:
    id: int
    name: str
    email: str
    address: AttrsAddress
    profile: AttrsProfile


@attrs.define(kw_only=True)
class ManualAttrsAddress:
    street: str
    city: str
    state: str
    zip: str


@attrs.define(kw_only=True)
class ManualAttrsPreferences:
    newsletter: bool
    theme: str
    locale: str


@attrs.define(kw_only=True)
class ManualAttrsProfile:
    display_name: str
    bio: str
    preferences: ManualAttrsPreferences


@attrs.define(kw_only=True)
class ManualAttrsUserCreate:
    id: int
    name: str
    email: str
    address: ManualAttrsAddress
    profile: ManualAttrsProfile


class TypedDictAddress(TypedDict):
    street: str
    city: str
    state: str
    zip: str


class TypedDictPreferences(TypedDict):
    newsletter: bool
    theme: str
    locale: str


class TypedDictProfile(TypedDict):
    display_name: str
    bio: str
    preferences: TypedDictPreferences


class TypedDictUser(TypedDict):
    id: int
    name: str
    email: str
    address: TypedDictAddress
    profile: TypedDictProfile


class ManualTypedDictAddress(TypedDict):
    street: str
    city: str
    state: str
    zip: str


class ManualTypedDictPreferences(TypedDict):
    newsletter: bool
    theme: str
    locale: str


class ManualTypedDictProfile(TypedDict):
    display_name: str
    bio: str
    preferences: ManualTypedDictPreferences


class ManualTypedDictUserCreate(TypedDict):
    id: int
    name: str
    email: str
    address: ManualTypedDictAddress
    profile: ManualTypedDictProfile


payload: dict[str, Any] = {
    "id": 123,
    "name": "Sam Bernheim",
    "email": "sam@example.com",
    "address": {
        "street": "123 Example Street",
        "city": "Paris",
        "state": "IDF",
        "zip": "75001",
    },
    "profile": {
        "display_name": "Sam",
        "bio": "Builds software.",
        "preferences": {
            "newsletter": True,
            "theme": "light",
            "locale": "en-US",
        },
    },
}


def projection_for(model_cls: type[Any]):
    views = views_for(model_cls)
    return (
        views.id
        + views.name
        + views.email
        + views.address.street
        + views.address.city
        + views.address.state
        + views.address.zip
        + views.profile.display_name
        + views.profile.bio
        + views.profile.preferences.newsletter
        + views.profile.preferences.theme
        + views.profile.preferences.locale
    )


def manual_dataclass_factory() -> ManualDataclassUserCreate:
    address = payload["address"]
    profile = payload["profile"]
    preferences = profile["preferences"]
    return ManualDataclassUserCreate(
        id=payload["id"],
        name=payload["name"],
        email=payload["email"],
        address=ManualDataclassAddress(**address),
        profile=ManualDataclassProfile(
            display_name=profile["display_name"],
            bio=profile["bio"],
            preferences=ManualDataclassPreferences(**preferences),
        ),
    )


def manual_attrs_factory() -> ManualAttrsUserCreate:
    address = payload["address"]
    profile = payload["profile"]
    preferences = profile["preferences"]
    return ManualAttrsUserCreate(
        id=payload["id"],
        name=payload["name"],
        email=payload["email"],
        address=ManualAttrsAddress(**address),
        profile=ManualAttrsProfile(
            display_name=profile["display_name"],
            bio=profile["bio"],
            preferences=ManualAttrsPreferences(**preferences),
        ),
    )


def manual_typed_dict_factory() -> ManualTypedDictUserCreate:
    return ManualTypedDictUserCreate(
        id=payload["id"],
        name=payload["name"],
        email=payload["email"],
        address=payload["address"],
        profile=payload["profile"],
    )


def benchmark(label: str, fn: Callable[[], object], *, iterations: int) -> float:
    for _ in range(1_000):
        fn()

    gc_was_enabled = gc.isenabled()
    gc.disable()
    try:
        start = time.perf_counter_ns()
        for _ in range(iterations):
            fn()
        end = time.perf_counter_ns()
    finally:
        if gc_was_enabled:
            gc.enable()

    per_call_us = (end - start) / iterations / 1_000
    print(f"{label:<38} {per_call_us:>10.3f} us/op")
    return per_call_us


def benchmark_generation(
    label: str,
    fn: Callable[[], object],
    *,
    iterations: int,
) -> float:
    samples: list[float] = []

    gc_was_enabled = gc.isenabled()
    gc.disable()
    try:
        for _ in range(iterations):
            start = time.perf_counter_ns()
            fn()
            end = time.perf_counter_ns()
            samples.append((end - start) / 1_000)
    finally:
        if gc_was_enabled:
            gc.enable()

    median = statistics.median(samples)
    print(f"{label:<38} {median:>10.3f} us/op median")
    return median


def run_hot_path_benchmarks(*, iterations: int) -> None:
    pydantic_models = project(
        PydanticUser,
        renderer=renderer.Pydantic,
        Create=projection_for(PydanticUser),
    )
    dataclass_models = project(
        DataclassUser,
        renderer=renderer.Dataclass,
        Create=projection_for(DataclassUser),
    )
    attrs_models = project(
        AttrsUser,
        renderer=renderer.Attrs,
        Create=projection_for(AttrsUser),
    )
    typed_dict_models = project(
        TypedDictUser,
        renderer=renderer.TypedDict,
        Create=projection_for(TypedDictUser),
    )

    cases = [
        (
            "Pydantic -> Pydantic",
            lambda: ManualPydanticUserCreate(**payload),
            lambda: pydantic_models.Create(**payload),
        ),
        (
            "dataclass -> dataclass",
            manual_dataclass_factory,
            lambda: dataclass_models.Create(**payload),
        ),
        (
            "attrs -> attrs",
            manual_attrs_factory,
            lambda: attrs_models.Create(**payload),
        ),
        (
            "TypedDict -> TypedDict",
            manual_typed_dict_factory,
            lambda: typed_dict_models.Create(**payload),
        ),
    ]

    print("Validation / instantiation hot path")
    for label, manual, projected in cases:
        print()
        print(label)
        manual_time = benchmark("manual", manual, iterations=iterations)
        projected_time = benchmark("project(...)", projected, iterations=iterations)
        print(f"ratio project/manual{'':<18} {projected_time / manual_time:>10.3f}x")


def run_generation_benchmarks(*, iterations: int) -> None:
    cases = [
        ("Pydantic -> Pydantic", PydanticUser, renderer.Pydantic),
        ("dataclass -> dataclass", DataclassUser, renderer.Dataclass),
        ("attrs -> attrs", AttrsUser, renderer.Attrs),
        ("TypedDict -> TypedDict", TypedDictUser, renderer.TypedDict),
    ]

    print()
    print("One-time project(...) generation")
    for label, model_cls, output_renderer in cases:
        benchmark_generation(
            label,
            lambda model_cls=model_cls, output_renderer=output_renderer: project(
                model_cls,
                renderer=output_renderer,
                Create=projection_for(model_cls),
            ),
            iterations=iterations,
        )


def main() -> None:
    parser = ArgumentParser()
    parser.add_argument(
        "--iterations",
        type=int,
        default=100_000,
        help="Hot-path payload construction iterations",
    )
    parser.add_argument(
        "--generation-iterations",
        type=int,
        default=500,
        help="One-time project(...) generation iterations",
    )
    args = parser.parse_args()

    print(f"Hot-path iterations: {args.iterations:,}")
    print(f"Generation iterations: {args.generation_iterations:,}")
    print()
    run_hot_path_benchmarks(iterations=args.iterations)
    run_generation_benchmarks(iterations=args.generation_iterations)


if __name__ == "__main__":
    main()
