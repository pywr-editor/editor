import pandas as pd
import pytest

from pywr_editor.utils import (
    are_columns_valid,
    default_index_name,
    find_existing_columns,
    get_columns,
    get_index_names,
    get_index_values,
    is_table_not_empty,
    reset_pandas_index_names,
    set_table_index,
)
from tests.utils import model_path


class TestDataFrameUtils:
    """
    Test the dataframe utils
    """

    @pytest.fixture()
    def df(self) -> pd.DataFrame:
        """
        The DataFrame to test.
        :return: The DataFrame
        """
        return pd.read_csv(model_path() / "files" / "table.csv")

    def test_index(self, df):
        """
        Test the index and column methods.
        """
        # index not set - this returns range index regardless of the passed value
        assert get_index_values(df, "Column 1") == [[0, 1]]

        assert get_index_names(df) == [default_index_name]
        assert get_index_names(None) == [default_index_name]

        # 1. Set index
        assert set_table_index(df, index_names=["Column 1", "Column 3"]) is True
        assert get_index_names(df) == ["Column 1", "Column 3"]

        # 2. get_columns
        assert get_columns(df, include_index=False) == [
            "Demand centre",
            " Date",
        ]
        assert get_columns(df, include_index=True) == [
            "Column 1",
            "Demand centre",
            "Column 3",
            " Date",
        ]

        # 3. get_index_values
        assert get_index_values(df, "Column 1") == [[1, 5]]
        assert get_index_values(df, ["Column 1", "Column 3"]) == [
            [1, 5],
            [3, 7],
        ]
        # one column does not exist
        assert get_index_values(df, ["Column 1", "Column XX"]) == [[1, 5], []]

    def test_validate_columns(self):
        """
        Test the methods to validate the columns.
        """
        # 1. Invalid table
        assert are_columns_valid(None) is False
        assert are_columns_valid(pd.DataFrame()) is False

        # 2. DataFrame without columns
        df = pd.DataFrame(data={"Col 1": [0, 1]})
        assert set_table_index(df, "Col 1") is True
        assert are_columns_valid(df) is False

    def test_empty_table(self):
        """
        Tests to validate an empty table.
        """
        df = pd.DataFrame(data={})
        assert is_table_not_empty(df) is False

    @pytest.mark.parametrize(
        "columns_to_find, index, expected_existing, expected_not_found",
        [
            (["Col 1", "Col 2"], None, ["Col 1", "Col 2"], []),
            # one column name is missing
            (
                ["Col 1", "Col 2", "Not found"],
                None,
                ["Col 1", "Col 2"],
                ["Not found"],
            ),
            # # test sorting
            (
                ["Col 3", "Col 1", "Not found"],
                None,
                ["Col 1", "Col 3"],
                ["Not found"],
            ),
            # test numerical col index
            ([0, 2, 9], None, ["Col 1", "Col 3"], [9]),
            # test with numerical col index and index set on table
            ([0, 2], ["Col 2"], ["Col 1", "Col 4"], []),
            # test empty list
            ([], None, [], []),
            # test wrong type
            ([False], None, [], []),
        ],
    )
    def test_find_existing_columns(
        self, columns_to_find, index, expected_existing, expected_not_found
    ):
        """
        Tests the find_existing_columns method. The method must returns all the columns.
        """
        df = pd.DataFrame(
            data={
                "Col 1": [0, 1],
                "Col 2": [0, 1],
                "Col 3": [0, 1],
                "Col 4": [0, 1],
            },
        )
        if index is not None:
            set_table_index(df, index)

        if columns_to_find == [False]:
            with pytest.raises(TypeError):
                find_existing_columns(df, columns_to_find, include_index=False)
        else:
            existing, not_found = find_existing_columns(
                df, columns_to_find, include_index=False
            )
            assert existing == expected_existing
            assert not_found == expected_not_found

    @pytest.mark.parametrize(
        "index, columns",
        [
            # one index
            ("Col 1", ["Col 1", "Col 2", "Col 3"]),
            # multi-index, indexes when reset are put in front
            (["Col 1", "Col 3"], ["Col 1", "Col 3", "Col 2"]),
            # anonymous index
            ([], ["Col 1", "Col 2", "Col 3"]),
        ],
    )
    def test_reset_index(self, index, columns):
        """
        Tests the reset_pandas_index_names() when the indexes are already set in the
        DataFrame itself.
        """
        df = pd.DataFrame(
            data={
                "Col 1": [0, 1],
                "Col 2": [0, 1],
                "Col 3": [0, 1],
            },
        )
        # do not set index if empty list (index already is anonymous)
        if index:
            df.set_index(index, inplace=True)

        index_names = reset_pandas_index_names(df)
        if not isinstance(index, list):
            assert index_names == [index]
        else:
            assert index_names == index

        assert get_columns(df) == columns
