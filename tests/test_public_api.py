from __future__ import annotations


def test_public_package_exports_project_not_api():
    import projector

    assert hasattr(projector, "project")
    assert not hasattr(projector, "api")
