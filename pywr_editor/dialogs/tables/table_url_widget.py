from PySide6.QtWidgets import QGroupBox

from pywr_editor.form import FormField, UrlWidget

"""
 This widget loads and handles slots and signals
 for a table file. This extends the UrlWidget but
 handle the QGroupBox visibility differently.
"""


class TableUrlWidget(UrlWidget):
    def toggle_fields(self) -> None:
        """
        Shows or hides additional fields, based on the file extension, to properly
        parse the table file. This also hides empty QGroupBox, when the file does
        not exist.
        :return: None
        """
        super().toggle_fields()

        # hide QGroupBox if all children are hidden
        for group_box in self.form.findChildren(QGroupBox):
            group_box: QGroupBox
            if all(
                [
                    field.isHidden()
                    for field in group_box.findChildren(FormField)
                ]
            ):
                group_box.setVisible(False)
            else:
                group_box.setVisible(True)
