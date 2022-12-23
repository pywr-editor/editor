import pytest

from pywr_editor.model import JsonUtils


@pytest.fixture
def dict_utils() -> JsonUtils:
    """
    Returns the JsonUtils instance.
    :return: The JsonUtils instance.
    """
    return JsonUtils(
        {
            "scenarios": [
                {"name": "scenario A", "size": 10},
                {
                    "name": "scenario B",
                    "size": 2,
                    "ensemble_names": ["First", "Second"],
                },
            ],
            "nodes": {
                "table": "cc",
                "index_col": "cc",
                "param": [
                    {"table": "cc", "ss": 1, "file": "path/to/file.csv"},
                    {"cc": 1},
                ],
                "dd": ["cc"],
            },
        }
    )


def test_find_str(dict_utils):
    """
    Tests find string in dictionary.
    """
    # find in key
    a = dict_utils.find_str("cc", "table")
    assert a.occurrences == 2
    assert a.paths == ["nodes/table", "nodes/param/Item #0/table"]

    a = dict_utils.find_str("scenario A", "scenario")
    assert a.occurrences == 0
    assert a.paths == []

    # find everywhere
    a = dict_utils.find_str("cc")
    assert a.occurrences == 5
    assert a.paths == [
        "nodes/table",
        "nodes/index_col",
        "nodes/param/Item #0/table",
        "nodes/param/Item #1/key/Item #0",
        "nodes/dd/Item #0",
    ]

    # string not found
    a = dict_utils.find_str("xx")
    assert a.occurrences == 0
    assert a.paths == []


def test_replace_str(dict_utils):
    """
    Tests string replacement in dictionary.
    """
    or_dict = dict_utils.d

    # with match key
    a = dict_utils.replace_str(old="cc", new="XX", match_key="table")
    assert a == {
        "scenarios": or_dict["scenarios"],
        "nodes": {
            "table": "XX",
            "index_col": "cc",
            "param": [
                {"table": "XX", "ss": 1, "file": "path/to/file.csv"},
                {"cc": 1},
            ],
            "dd": ["cc"],
        },
    }

    # replace everywhere
    a = dict_utils.replace_str(old="cc", new="XX", rename_dict_keys=True)
    assert a == {
        "scenarios": or_dict["scenarios"],
        "nodes": {
            "table": "XX",
            "index_col": "XX",
            "param": [
                {"table": "XX", "ss": 1, "file": "path/to/file.csv"},
                {"XX": 1},
            ],
            "dd": ["XX"],
        },
    }

    # replace everywhere but not in dictionary keys
    a = dict_utils.replace_str(old="cc", new="XX", rename_dict_keys=False)
    assert a == {
        "scenarios": or_dict["scenarios"],
        "nodes": {
            "table": "XX",
            "index_col": "XX",
            "param": [
                {"table": "XX", "ss": 1, "file": "path/to/file.csv"},
                {"cc": 1},
            ],
            "dd": ["XX"],
        },
    }

    # no replacement - string not found
    a = dict_utils.replace_str(old="xx", new="XX")
    assert dict_utils.d == a

    # replace everywhere but exclude dictionary key
    a = dict_utils.replace_str(
        old="cc", new="New", exclude_key="table", rename_dict_keys=True
    )
    assert a == {
        "scenarios": or_dict["scenarios"],
        "nodes": {
            "table": "cc",
            "index_col": "New",
            "param": [
                {"table": "cc", "ss": 1, "file": "path/to/file.csv"},
                {"New": 1},
            ],
            "dd": ["New"],
        },
    }

    # replace everywhere but exclude dictionary keys
    a = dict_utils.replace_str(
        "cc", "New", exclude_key=["table", "index_col"], rename_dict_keys=True
    )
    assert a == {
        "scenarios": or_dict["scenarios"],
        "nodes": {
            "table": "cc",
            "index_col": "cc",
            "param": [
                {"table": "cc", "ss": 1, "file": "path/to/file.csv"},
                {"New": 1},
            ],
            "dd": ["New"],
        },
    }
