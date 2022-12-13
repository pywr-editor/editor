from typing import Literal, Any
from PySide6 import QtGui
from PySide6.QtCore import QRegularExpression
from PySide6.QtGui import QFont, QTextCharFormat
from pywr_editor.style import Color


class Rules:
    def __init__(self):
        """
        Initialises the highlighting rules class.
        """
        self.highlighting_rules: list[dict[str, Any]] = []

    def add(
        self,
        pattern: str,
        color: Color,
        style: Literal["italic", "bold"] | None = None,
    ) -> None:
        """
        Adds a new rule.
        :param pattern: The regular expression for the pattern.
        :param color: The Color instance.
        :param style: The style (italic or bold). Optional.
        :return: None
        """
        text_format = QTextCharFormat()
        if style is not None:
            if style == "bold":
                text_format.setFontWeight(QFont.DemiBold)
            elif style == "italic":
                text_format.setFontWeight(QFont.StyleItalic)
        text_format.setForeground(color.qcolor)
        # noinspection PyTypeChecker
        self.highlighting_rules.append(
            {"pattern": QRegularExpression(pattern), "format": text_format}
        )


class JsonHighlighter(QtGui.QSyntaxHighlighter):
    def __init__(self, parent: QtGui.QTextDocument):
        super().__init__(parent)
        self.rules = Rules()

        # braces
        braces = ["{", "}", r"\[", r"\]"]
        [self.rules.add(w, Color("gray", 700), "bold") for w in braces]
        # keywords
        keywords = ["None", "True", "False", "null"]
        [self.rules.add(rf"\b{w}\b", Color("sky", 800)) for w in keywords]
        # all strings
        strings = [r'"[^"\\]*(\\.[^"\\]*)*"', r"'[^'\\]*(\\.[^'\\]*)*'"]
        [self.rules.add(w, Color("orange", 800)) for w in strings]
        # numbers
        self.rules.add('([-0-9.]+)(?!([^"]*"[\\s]*\\:))', Color("rose", 800))
        # middle
        self.rules.add('(?:[ ]*\\,[ ]*)("[^"]*")', Color("gray", 800))
        # last
        self.rules.add('("[^"]*")(?:\\s*\\])', Color("cyan", 500))
        # key
        self.rules.add('("[^"]*")\\s*\\:', Color("blue", 800), "bold")
        # value
        self.rules.add(':+(?:[: []*)("[^"]*")', Color("emerald", 800))

    def highlightBlock(self, text: str) -> None:
        """
        Highlights the text.
        :param text: The text.
        :return: None
        """
        for rule in self.rules.highlighting_rules:
            match_iterator = rule["pattern"].globalMatch(text)
            while match_iterator.hasNext():
                match = match_iterator.next()
                self.setFormat(
                    match.capturedStart(),
                    match.capturedLength(),
                    rule["format"],
                )
