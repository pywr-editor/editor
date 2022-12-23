import logging

from model import ModelConfig

from pywr_editor import FloatWidget, FormField, ParameterDialogForm

class ValueWidget(FloatWidget):
    logger: logging.Logger

    form: ParameterDialogForm
    model_config: ModelConfig
    def __init__(
        self,
        name: str,
        value: dict,
        parent: FormField,
    ): ...
    def after_field_render(self) -> None: ...
    def get_default_value(self) -> str: ...
