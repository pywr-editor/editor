import pytest
from pathlib import Path


def clean_env(model_file: str) -> None:
    """
    Removes the editor settings.
    :param model_file: The model file.
    :return: None
    """
    from pywr_editor.utils import Settings

    editor_settings = Settings(model_file)
    editor_settings.instance.clear()
    editor_settings.instance.sync()


def pytest_sessionfinish(session):
    """
    Cleans the editor settings after a test.
    """
    for item in session.items:
        cls = item.getparent(pytest.Class)
        if (
            cls is not None
            and hasattr(cls, "obj")
            and hasattr(cls, "model_file")
        ):
            clean_env(cls.obj.model_file)

    # Removed the dynamic table file created by one test. If one test fails the
    # file is not deleted.
    dynamic_file = Path("test/models/files/table_missing.csv")
    if dynamic_file.exists():
        dynamic_file.unlink()
