import pytest

from pywr_editor.model import ModelConfig
from tests.utils import resolve_model_path


@pytest.fixture
def model():
    return ModelConfig(resolve_model_path("model_tables.json"))


def test_names(model):
    """
    Tests the names property.
    """
    assert model.tables.names == [
        "Table 1",
        "Table 2",
        "Table 3",
        "Table 5",
        "Table 6",
        "Table 7",
        "Table 8",
    ]


def test_is_used(model):
    """
    Tests the is_used method.
    """
    assert model.tables.is_used("Table 1") == 2
    assert model.tables.is_used("Table 2") == 0
    # non existing table
    assert model.tables.is_used("Table X") == 0


def test_delete(model):
    """
    Tests the delete method.
    """
    model.tables.delete("Table 1")
    assert model.has_changes is True
    assert model.tables.names == [
        "Table 2",
        "Table 3",
        "Table 5",
        "Table 6",
        "Table 7",
        "Table 8",
    ]


def test_get_table_config(model):
    """
    Tests the get_table_config_from_name method.
    """
    assert model.tables.config("Table 2") == {
        "url": "file2.csv",
        "index_col": "Date",
        "parse_dates": False,
    }


def test_update(model):
    """
    Tests the update method.
    """
    model.tables.update("Table 1", {"url": "fileXX.csv", "sep": ";"})
    assert model.has_changes is True
    assert model.tables.config("Table 1") == {
        "sep": ";",
        "url": "fileXX.csv",
    }

    model.tables.update("Table new", {})
    assert model.has_changes is True
    assert model.tables.config("Table new") == {}


def test_rename(model):
    """
    Tests the rename method.
    """
    model.tables.rename("Table 1", "New name")
    assert model.has_changes is True

    assert "Table 1" not in model.tables.names
    assert "New name" in model.tables.names


def test_rename_special_characters(model):
    """
    Tests the rename method containing regex or JSON special characters.
    """
    model.tables.rename("Table 1", 'New name"')
    assert model.has_changes is True

    assert "Table 1" "" not in model.tables.names
