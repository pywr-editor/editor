from pywr_editor.form import AbstractStringComboBoxWidget, FormField

"""
 Defines a widget to select the compression algorithm for
 the table recorder.
"""


class H5CompressionLibWidget(AbstractStringComboBoxWidget):
    def __init__(
        self,
        name: str,
        value: str | None,
        parent: FormField,
    ):
        """
        Initialises the widget.
        :param name: The field name.
        :param value: The selected method.
        :param parent: The parent widget.
        """
        if value and value == "blosclz":
            value = "blosc:blosclz"

        labels_map = {
            "zlib": "ZLIB",
            "lzo": "LZO",
            "bzip2": "BZIP2",
            "blosc:blosclz": "BLOSC:BLOSCLZ",
            "blosc:lz4": "BLOSC:LZ4",
            "blosc:lz4hc": "BLOSC:LZ4HC",
            "blosc:zlib": "BLOSC:ZLIB",
            "blosc:zstd": "BLOSC:ZSTD",
        }

        super().__init__(
            name=name,
            value=value,
            parent=parent,
            log_name=self.__class__.__name__,
            labels_map=labels_map,
            default_value="zlib",
        )
