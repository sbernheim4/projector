from __future__ import annotations


def test_public_package_exports_project_not_api():
    import app

    assert hasattr(app, "project")
    assert not hasattr(app, "api")
