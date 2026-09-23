from pynivo.paths import application_root, resource_path


def test_development_paths_find_project_resources() -> None:
    assert (application_root() / "pyproject.toml").is_file()
    assert resource_path("resources/branding/pynivo.ico").is_file()
