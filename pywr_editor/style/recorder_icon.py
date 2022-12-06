from pywr_editor.style.icon_with_initials import IconWithInitials


class RecorderIcon(IconWithInitials):
    def __init__(self, recorder_key: str | None):
        """
        Initialises the class.
        :param recorder_key: The recorder key.
        """
        self.recorder_key = recorder_key
        super().__init__(recorder_key, "circle")

    def get_color(self) -> str:
        """
        Gets the icon color based on the recorder key.
        :return: The color name.
        """
        colors = {}

        if self.recorder_key in colors:
            return colors[self.recorder_key]
        else:
            return "red"
