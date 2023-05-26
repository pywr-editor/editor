import pytest

from pywr_editor.dialogs import ParametersDialog
from pywr_editor.dialogs.parameters.parameter_page_widget import ParameterPageWidget
from pywr_editor.form import FormField, ValuesAndExternalDataWidget
from pywr_editor.model import ModelConfig
from tests.utils import resolve_model_path


class TestDialogParameterControlCurvePiecewiseInterpolatedParameter:
    """
    Tests the section for ControlCurvePiecewiseInterpolatedParameter.
    """

    model_file = resolve_model_path(
        "model_dialog_parameter_cc_piecewise_interp_section.json"
    )

    @pytest.fixture()
    def model_config(self) -> ModelConfig:
        """
        Initialises the model configuration.
        :return: The ModelConfig instance.
        """
        return ModelConfig(self.model_file)

    def test_validation(self, qtbot, model_config):
        """
        Tests that the values are loaded correctly.
        """
        param_name = "valid"
        dialog = ParametersDialog(model_config, param_name)
        dialog.hide()

        # noinspection PyTypeChecker
        selected_page: ParameterPageWidget = dialog.pages_widget.currentWidget()
        form = selected_page.form

        # noinspection PyUnresolvedReferences
        assert selected_page.findChild(FormField, "name").value() == param_name

        # 1. Check the values in the table widget
        table_widget: ValuesAndExternalDataWidget = form.find_field_by_name(
            "values"
        ).widget
        model = table_widget.model
        assert table_widget.multiple_variables is True

        # check data in the model (each nested list is a column)
        assert model.values[0] == [-0.1, -100]
        assert model.values[1] == [-1, -200]

        # check data in the widget - shift column by 1 for the row labels
        assert model.index(0, 1).data() == -0.1
        assert model.index(0, 2).data() == -1
        assert model.index(1, 1).data() == -100
        assert model.index(1, 2).data() == -200

        # 2. Get value - this is re-transposed
        assert table_widget.get_value() == [[-0.1, -1], [-100, -200]]
