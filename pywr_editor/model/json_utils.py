from dataclasses import dataclass


@dataclass
class DictMatches:
    occurrences: int
    """ The number of occurrences """
    paths: list[str]
    """ The paths in the dictionary where the occurrences are found """


@dataclass
class JsonUtils:
    d: dict
    """ The dictionary where to find the string """

    def find_str(self, string: str, match_key: str | None = None) -> DictMatches:
        """
        Gets the number of occurrences a string appears as a dictionary value. For
        example given d:
        d = {'nodes': {'table': 'cc', 'param': [{'table': 'cc', 'ss': 1},
                {'cc': 1}], 'dd': ['cc']}}

        find_str("cc", match_key="table") returns
            DictMatches(occurrences=2, paths=["root.nodes.table",
             "root/nodes/param/Item #0/table"])
        find_str("cc") returns
            DictMatches(occurrences=4, paths=[
                "root/nodes/table", "root/nodes/param/Item #0/table",
                "root/nodes/param/Item #1/key/Item #0", "root/nodes/dd/Item #0"
            ])
        :param string: The string to find.
        :param match_key: Search the string only in dictionaries with keys matching the
        provided string (for example "table"). If omitted, the string will be searched
        in all nested dictionary keys and values.
        :return: A DictMatches object,  with the number of occurrences and a list with
        the dictionary/list paths
        """
        if match_key is not None:
            output = self._find_str_in_dict_match_key(self.d, match_key, string)
        else:
            output = self._find_str_in_dict_everywhere(self.d, string)

        return DictMatches(
            occurrences=output[0],
            paths=[a.replace("root/", "") for a in output[1]],
        )

    def _find_str_in_dict_match_key(
        self,
        d: str | dict | list,
        match_key: str,
        string: str,
        parent_key: str = "root",
    ) -> tuple[int, list[str]]:
        """
        Gets the number of occurrences a string appears as a dictionary value for a
        given key.
        :param d: The dictionary where to look for the string.
        :param match_key: The key where to replace the value (for example "table").
        :param string: The string to find.
        :return: A tuple with the number of occurrences and a list with the
        dictionary key paths
        """
        counter = 0
        dict_path = []
        if isinstance(d, dict):
            for k, v in d.items():
                (sub_counter, sub_dict_path) = self._find_str_in_dict_match_key(
                    v, match_key, string, f"{parent_key}/{k}"
                )
                counter += sub_counter
                dict_path = dict_path + sub_dict_path
        elif isinstance(d, list):
            for ii, item in enumerate(d):
                (sub_counter, sub_dict_path) = self._find_str_in_dict_match_key(
                    item, match_key, string, f"{parent_key}/Item #{ii}"
                )
                counter += sub_counter
                dict_path = dict_path + sub_dict_path
        elif (
            isinstance(d, str)
            # ensure exact match
            and parent_key.split("/").count(match_key)
            and d == string
        ):
            counter += 1
            dict_path.append(parent_key)

        return counter, dict_path

    def _find_str_in_dict_everywhere(
        self, d: str | dict | list, string: str, parent_key: str = "root"
    ) -> tuple[int, list[str]]:
        """
        Gets the number of occurrences a string appears in a dictionary (in its keys
        and values) and in nested lists.
        :param d: The dictionary where to look for the string.
        :param string: The string to find.
        :return: A tuple with the number of occurrences and a list with the paths.
        """
        counter = 0
        dict_path = []
        if isinstance(d, dict):
            keys = list(d.keys())
            for k, v in d.items():
                # dictionary key
                (sub_counter, sub_dict_path) = self._find_str_in_dict_everywhere(
                    k, string, f"{parent_key}/key/Item #{keys.index(k)}"
                )
                counter += sub_counter
                dict_path = dict_path + sub_dict_path

                # dictionary values
                (
                    sub_counter,
                    sub_dict_path,
                ) = self._find_str_in_dict_everywhere(v, string, f"{parent_key}/{k}")
                counter += sub_counter
                dict_path = dict_path + sub_dict_path
        elif isinstance(d, list):
            for ii, item in enumerate(d):
                (sub_counter, sub_dict_path) = self._find_str_in_dict_everywhere(
                    item, string, f"{parent_key}/Item #{ii}"
                )
                counter += sub_counter
                dict_path = dict_path + sub_dict_path
        elif isinstance(d, str) and d == string:
            counter += 1
            dict_path.append(parent_key)

        return counter, dict_path

    def replace_str(
        self,
        old: str,
        new: str,
        rename_dict_keys: bool = False,
        match_key: list[str] | str | None = None,
        exclude_key: str | list[str] | None = None,
    ) -> dict:
        """
        Replaces a string in the dictionary:
        d = {'nodes': {'table': 'cc', 'param': [{'table': 'cc', 'ss': 1}, {'cc': 1}],
            'dd': ['cc']}}

        str_replace("cc", "vvvv", match_key="table") returns
            {'nodes': {'table': 'vvvv', 'param': [{'table': 'vvvv', 'ss': 1},
            {'cc': 1}], 'dd': ['cc']}}
        str_replace("cc", "vvvv", rename_dict_keys=True) returns
            {'nodes': {'table': 'vvvv', 'param': [{'table': 'vvvv', 'ss': 1},
            {'vvvv': 1}], 'dd': ['vvvv']}}

        :param old: The string to find.
        :param new: The string to replace.
        :param match_key: Replaces the string only in those dictionary keys matching
        match_key. This can be a string or a list of keys. If None, the string will
        be replaced in list items and, dictionary keys and values. Default to None.
        :param rename_dict_keys: Whether to replace the string in the dictionary keys.
        This cannot be set to True  when match_key is provided. Default to False.
        :param exclude_key: Replace the string everywhere except in those dictionary
        keys matching exclude_key. This can be a string or a list of keys. This is
        optional and cannot be used when match_key is provided.
        :return: The dictionary with the string replaced.
        """
        if match_key is not None and exclude_key is not None:
            ValueError(
                "The match_key and exclude_key parameters cannot be "
                + "provided at the same time"
            )
        if match_key is not None and rename_dict_keys:
            ValueError(
                "The rename_dict_keys cannot be set to True when match_key is provided"
            )

        if match_key is not None:
            return self._str_replace_match_key(
                d=self.d, match_key=match_key, old=old, new=new
            )
        else:
            return self._str_replace_everywhere(
                d=self.d,
                old=old,
                new=new,
                exclude_key=exclude_key,
                rename_dict_keys=rename_dict_keys,
            )

    def _str_replace_match_key(
        self,
        d: str | list | dict,
        match_key: list[str] | str | None,
        old: str,
        new: str,
        tracked_dict_key: str | None = None,
    ) -> dict | list | str:
        """
        Replaces a string value in the dictionary where its key matches match_key.
        :param d: The dictionary where to replace the string.
        :param match_key: The key or a list of keys where to replace the value
        (for example "table").
        :param old: The string to replace.
        :param new: The new string.
        :param tracked_dict_key: A variable used to store the key of the parent
        dictionary for an item.
        :return: The updated dictionary.
        """
        if isinstance(match_key, str):
            match_key = [match_key]

        x = {}
        if isinstance(d, dict):
            for k, v in d.items():
                v = self._str_replace_match_key(
                    d=v,
                    match_key=match_key,
                    old=old,
                    new=new,
                    tracked_dict_key=k,
                )
                x[k] = v
        elif isinstance(d, list):
            new_d = []
            for item in d:
                new_d.append(
                    self._str_replace_match_key(
                        d=item,
                        match_key=match_key,
                        old=old,
                        new=new,
                        tracked_dict_key=tracked_dict_key,
                    )
                )
            return new_d
        elif isinstance(d, str) and tracked_dict_key in match_key and d == old:
            return d.replace(old, new)
        else:
            return d
        return x

    def _str_replace_everywhere(
        self,
        d: str | list | dict,
        old: str,
        new: str,
        rename_dict_keys: bool = False,
        exclude_key: list[str] | str | None = None,
        tracked_dict_key: str | None = None,
    ) -> dict | list | str:
        """
        Replaces a string value in a dictionary (in its keys and values) and in nested
        lists.
        :param d: The dictionary where to replace the string.
        :param old: The string to replace.
        :param new: The new string.
        :param rename_dict_keys: Whether to replace the string in the dictionary keys.
        Default to False.
        :param exclude_key: Replace the string everywhere except in those dictionary
        keys matching exclude_key. Optional.
        :param tracked_dict_key: A variable used to store the key of the parent
        dictionary for an item.
        :return: The updated dictionary.
        """
        if isinstance(exclude_key, str):
            exclude_key = [exclude_key]

        x = {}
        if isinstance(d, dict):
            for k, v in d.items():
                # dict key replacement
                if rename_dict_keys and k == old:
                    k = k.replace(old, new)
                v = self._str_replace_everywhere(
                    d=v,
                    old=old,
                    new=new,
                    rename_dict_keys=rename_dict_keys,
                    exclude_key=exclude_key,
                    tracked_dict_key=k,
                )
                x[k] = v
        elif isinstance(d, list):
            new_d = []
            for item in d:
                new_d.append(
                    self._str_replace_everywhere(
                        d=item,
                        old=old,
                        new=new,
                        exclude_key=exclude_key,
                        rename_dict_keys=rename_dict_keys,
                        tracked_dict_key=tracked_dict_key,
                    )
                )
            return new_d
        elif isinstance(d, str) and d == old:
            if exclude_key is not None and tracked_dict_key in exclude_key:
                return d
            return d.replace(old, new)
        else:
            return d
        return x
