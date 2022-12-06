import pytest
from pywr_editor.model import ParameterConfig


class TestParamConfig:
    @staticmethod
    def parameter_config(
        parameter_props: dict, parameter_name: str | None
    ) -> ParameterConfig:
        """
        Returns the ParameterConfig instance.
        :param parameter_props: The dictionary for the parameter.
        :param parameter_name: The parameter name if available.
        :return: The ParameterConfig instance.
        """
        return ParameterConfig(
            props=parameter_props,
            name=parameter_name,
            model_parameter_names=["A constant global parameter"],
        )

    @property
    def parameters_dict(self) -> dict:
        """
        Reads the parameter properties.
        :return: The dictionary with the parameter properties to test.
        """
        return {
            "A constant global parameter": {"type": "Constant", "value": 4},
            "custom_parameter": {
                "type": "CustomClass",
                "value1": 1,
                "value2": 5,
            },
            "custom_parameter2": {
                "type": "CustomClassParameter",
                "value1": 1,
                "value2": 5,
            },
            "anonymous_parameter": {"type": "constant", "value": 5},
            "anonymous_parameter2": {"type": "constantparameter", "value": 5},
            "anonymous_parameter3": {"type": "ConstantParameter", "value": 5},
            "anonymous_parameter4": {"type": "ConsTantParameteR", "value": 5},
        }

    @pytest.mark.parametrize(
        "parameter_name",
        [
            "A constant global parameter",
            "anonymous_parameter",
            "anonymous_parameter2",
            "anonymous_parameter3",
            "anonymous_parameter4",
        ],
    )
    def test_model_parameters(self, parameter_name):
        """
        Tests that the correct value is returned for the parameter properties.
        """
        param_dict = self.parameters_dict

        parameter_config = self.parameter_config(
            param_dict[parameter_name], parameter_name
        )
        if parameter_name == "A constant global parameter":
            assert parameter_config.is_a_model_parameter is True
        else:
            assert parameter_config.is_a_model_parameter is False

        assert parameter_config.is_custom is False
        assert parameter_config.key == "constant"
        assert parameter_config.humanised_type == "Constant"

    @pytest.mark.parametrize(
        "param_name", ["custom_parameter", "custom_parameter2"]
    )
    def test_custom_parameters(self, param_name):
        """
        Tests that the correct value is returned for the is_a_model_parameter and is_custom
        properties.
        """
        parameter_config = self.parameter_config(
            self.parameters_dict["custom_parameter"],
            param_name,
        )
        assert parameter_config.key == "customclass"
        assert parameter_config.is_custom is True
        assert parameter_config.is_a_model_parameter is False

    def test_anonymous_parameters(self):
        """
        Tests an anonymous parameter (i.e. a nested parameter in a node configuration
        without a name).
        """
        parameter_config = self.parameter_config(
            self.parameters_dict["anonymous_parameter"], None
        )

        assert parameter_config.is_a_model_parameter is False
        assert parameter_config.is_custom is False
