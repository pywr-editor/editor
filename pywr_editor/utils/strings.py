def humanise_label(key: str) -> str:
    """
    Returns a human-readable version of a label. For example "minimum_version"
    is converted to "Minimum version".
    :param key: The label to convert.
    :return: The converted string.
    """
    key = str(key).replace("_", " ")
    key = "{}{}".format(key[0].upper(), key[1:])
    return key


def label_to_key(label: str) -> str:
    """
    Converts a human-readable string to a key. For example "Minimum version"
    is converted to "minimum_version".
    :param label: The label to convert.
    :return: The key.
    """
    return str(label).replace(" ", "_").lower().strip()
