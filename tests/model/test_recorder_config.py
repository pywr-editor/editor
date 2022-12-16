import pytest
from pywr_editor.model import RecorderConfig


class TestRecorderConfig:
    @staticmethod
    def recorder_config(
        recorder_props: dict, recorder_name: str | None
    ) -> RecorderConfig:
        """
        Returns the RecorderConfig instance.
        :param recorder_props: The dictionary for the recorder.
        :param recorder_name: The recorder name if available.
        :return: The RecorderConfig instance.
        """
        return RecorderConfig(
            props=recorder_props,
            name=recorder_name,
            model_recorder_names=["A global recorder"],
        )

    @property
    def recorders_dict(self) -> dict:
        """
        Reads the recorder properties.
        :return: The dictionary with the recorder properties to test.
        """
        return {
            "A global recorder": {
                "type": "NodeRecorder",
                "node": "Link",
            },
            "custom_recorder": {
                "type": "CustomClassRecorder",
                "value": 1,
                "node": "Reservoir",
            },
            "anonymous_recorder": {
                "type": "TotalDeficitNodeRecorder",
                "node": "Link",
            },
        }

    @pytest.mark.parametrize(
        "recorder_name",
        [
            "A global recorder",
            "anonymous_recorder",
        ],
    )
    def test_model_recorders(self, recorder_name):
        """
        Tests that the correct value is returned for the recorder properties.
        """
        param_dict = self.recorders_dict

        recorder_config = self.recorder_config(
            param_dict[recorder_name], recorder_name
        )
        if recorder_name == "A global recorder":
            assert recorder_config.is_a_model_recorder is True
        else:
            assert recorder_config.is_a_model_recorder is False

        assert recorder_config.is_custom is False

    def test_custom_recorders(self):
        """
        Tests that the correct value is returned for the is_a_model_recorder and
        is_custom properties.
        """
        recorder_config = self.recorder_config(
            self.recorders_dict["custom_recorder"],
            "custom_recorder",
        )
        assert recorder_config.is_custom is True
        assert recorder_config.is_a_model_recorder is False

    def test_anonymous_recorders(self):
        """
        Tests an anonymous recorder (i.e. a nested recorder in a node configuration
        without a name).
        """
        recorder_config = self.recorder_config(
            self.recorders_dict["anonymous_recorder"], None
        )

        assert recorder_config.is_a_model_recorder is False
        assert recorder_config.is_custom is False
