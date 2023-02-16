from pandas import DataFrame

default_index_name = "Anonymous index"


def get_columns(
    table: DataFrame, include_index: bool = False
) -> list[str] | None:
    """
    Returns the table columns except the columns used as index.
    :param table: The DataFrame.
    :param include_index: Whether to include the index names in the DataFrame columns.
    Default to False.
    :return: A list of table column names or None if the table is not available.
    """
    if table is None:
        return None
    else:
        columns = table.columns.values.tolist()
        if include_index:
            return columns

        # filter out the index
        if "index" in table.attrs.keys():
            diff_columns = list(set(columns) - set(table.attrs["index"]))
            # sets are unordered, preserve the same initial colum order
            columns = [
                col_name for col_name in columns if col_name in diff_columns
            ]
        else:
            return columns

    return columns


def get_index_names(table: DataFrame | None) -> list[str]:
    """
    Returns the table index names. When the table is not available or the index is not
    set or is an empty list, this returns the default index name.
    :param table: The DataFrame.
    :return: A list of table index names. The list is empty if the table is not
    available or no index is set.
    """
    if (
        table is not None
        and "index" in table.attrs.keys()
        and table.attrs["index"]
    ):
        index_names = table.attrs["index"]
    else:
        index_names = [default_index_name]

    return index_names


def reset_pandas_index_names(table: DataFrame | None) -> list[str]:
    """
    Resets the indexes set in the DataFrame and returns their names.
    :param table: The DataFrame.
    :return: The name of the indexes or an empty list if no index is set.
    """
    if table is None:
        return []
    index = list(table.index.names)

    # anonymous index
    if index == [None]:
        return []

    table.reset_index(inplace=True)
    return index


def get_index_values(
    table: DataFrame | None, index_names: str | list[str]
) -> list[list]:
    """
    Returns the table index values.
    :param table: The DataFrame.
    :param index_names: A list of column names to extract the values of.
    :return: A list containing all the index values.
    """
    all_index_names = get_index_names(table)

    # the index is not set. Returns range but in a list for multi-index compatibility.
    if all_index_names == [default_index_name]:
        return [list(range(0, len(table)))]

    # convert to list for multi selection
    if not isinstance(index_names, list):
        index_names = [index_names]

    # return data by columns by transposition. If column does not exist, returns
    # empty set. A set is used to collect unique names only.
    return [
        list(set(table[index_name].values.transpose().tolist()))
        if index_name in all_index_names
        else []
        for index_name in index_names
    ]


def set_table_index(
    table: DataFrame | None,
    index_names: str | list[str] | int | list[int],
) -> bool:
    """
    Set the index on the table in attribute field.
    :param table: The DataFrame.
    :param index_names: The index name (or as integer) or list of index names to set.
    :return: True if the indexes are correctly stored, False otherwise.
    """
    if table is None:
        return False
    else:
        if not isinstance(index_names, list):
            index_names = [index_names]
        # provided index names is empty list or None. Skip/reset index
        if not index_names:
            if "index" in table.attrs.keys():
                del table.attrs["index"]
            return True

        # loop through columns to ensure original sorting
        # handle numeric index as columns
        all_columns = table.columns.values.tolist()
        if isinstance(index_names[0], str):
            table.attrs["index"] = [
                column for column in index_names if column in all_columns
            ]
        elif isinstance(index_names[0], int):
            table.attrs["index"] = [
                all_columns[col_id]
                for col_id in index_names
                if 0 <= col_id <= len(all_columns) - 1
            ]

        return True


def are_columns_valid(table: DataFrame | None) -> bool:
    """
    Checks if the table columns are valid.
    :return: True if the columns are valid, False otherwise.
    """
    columns = get_columns(table)
    return table is not None and len(columns) > 0


def is_table_not_empty(table: DataFrame) -> bool:
    """
    Checks if the table is not empty (i.e. has columns and rows).
    :return: True if the table is not empty, False otherwise.
    """
    return are_columns_valid(table) and len(table) > 0


def find_existing_columns(
    table: DataFrame | None,
    columns_to_find: list[str] | list[int],
    include_index: bool = False,
) -> tuple[list[str], list[str]]:
    """
    From a list of column names, return a list of existing columns  in the table and
    a list of wrong colum names.
    :param table: The DataFrame
    :param columns_to_find: The column names or index to search for.
    :param include_index: Whether to include the index names in the DataFrame columns.
    Default to False.
    :return: A tuple with a list containing the column names existing in the table and
    a list with the wrong column names. The names are sorted using the column order in
    the table.
    """
    if table is None or not columns_to_find:
        return [], []

    columns = get_columns(table, include_index)
    if isinstance(columns_to_find[0], str):
        existing_columns = [
            col_name for col_name in columns if col_name in columns_to_find
        ]
        wrong_columns = list(set(columns_to_find) - set(existing_columns))
    elif isinstance(columns_to_find[0], bool):
        # bool is subclass of int
        raise TypeError("Column can only be string or integers")
    elif isinstance(columns_to_find[0], int):
        # always use table sort
        # noinspection PyTypeChecker
        columns_to_find: list[int] = sorted(columns_to_find)
        wrong_columns = [
            col_id
            for col_id in columns_to_find
            if not 0 <= col_id <= len(columns) - 1
        ]
        existing_columns = list(set(columns_to_find) - set(wrong_columns))
        # convert to string
        existing_columns = [columns[col_id] for col_id in existing_columns]
    else:
        raise TypeError("Column can only be string or integers")

    return existing_columns, wrong_columns
