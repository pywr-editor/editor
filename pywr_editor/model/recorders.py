from typing import TYPE_CHECKING

from pywr_editor.model import ComponentsDict, RecorderConfig

if TYPE_CHECKING:
    from pywr_editor.model import ModelConfig

"""
 Handles the model recorders
"""


class Recorders(ComponentsDict):
    model: "ModelConfig"
    """ The ModelConfig instance """

    def __init__(self, model: "ModelConfig"):
        """
        Initialise the class.
        :param model: The ModelConfig instance.
        """
        super().__init__(model=model, key="recorders")

    def recorder(
        self, config: dict, name: str | None = None, deepcopy: bool = False
    ) -> RecorderConfig:
        """
        Returns the RecorderConfig instance.
        :param config: The recorder configuration.
        :param name: The recorder name.
        :param deepcopy: Create a deepcopy of the recorder dictionary.
        :return: The RecorderConfig instance
        """
        return RecorderConfig(
            props=config,
            name=name,
            model_recorder_names=self.names,
            deepcopy=deepcopy,
        )

    def is_a_model_recorder(self, recorder_name: str) -> bool:
        """
        Returns True if the recorder is defined in the model dictionary.
        :parameter recorder_name: The recorder name.
        :return: True if the recorder is a model recorder, False for
        anonymous recorders.
        """
        return recorder_name in self.get_all().keys()

    def config(
        self, recorder_name: str, as_dict: bool = True
    ) -> dict | RecorderConfig | None:
        """
        Return the configuration of a model recorder as dictionary or RecorderConfig
        instance.
        :parameter recorder_name: The recorder name.
        :param as_dict: Return the configuration as dictionary when true, the
        RecorderConfig instance when false.
        :return: The recorder configuration or its instance.
        """
        if self.exists(recorder_name) is False:
            return None

        parameter_config = self.get_all()[recorder_name]
        if as_dict:
            return parameter_config
        else:
            return RecorderConfig(
                props=parameter_config,
                model_recorder_names=self.names,
                name=recorder_name,
            )
