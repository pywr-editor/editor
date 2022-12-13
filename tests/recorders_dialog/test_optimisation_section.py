import pytest
from PySide6.QtCore import QTimer
from pywr_editor.model import ModelConfig
from pywr_editor.dialogs import RecordersDialog
from pywr_editor.dialogs.recorders.recorder_page_widget import (
    RecorderPageWidget,
)
from pywr_editor.form import (
    FormField,
    AggFuncPercentileListWidget,
    AggFuncPercentileOfScoreScoreWidget,
    OptAggFuncWidget,
)
from tests.utils import resolve_model_path, close_message_box


class TestDialogRecorderOptimisationSection:
    """
    Tests the section with the fields to handle a recorder optimisation.
    """

    percentile_fields = [
        OptAggFuncWidget.agg_func_percentile_list,
        OptAggFuncWidget.agg_func_percentile_method,
    ]
    percentileofsocre_fields = [
        OptAggFuncWidget.agg_func_percentileofscore_score,
        OptAggFuncWidget.agg_func_percentileofscore_kind,
    ]

    @pytest.fixture()
    def model_config(self) -> ModelConfig:
        """
        Initialises the model configuration.
        :return: The ModelConfig instance.
        """
        return ModelConfig(
            resolve_model_path("model_dialog_recorders_opt_section.json")
        )

    def test_bound_inequality(self, qtbot, model_config):
        """
        Tests the error message when the lower bound is larger then the upper bound.
        This also tests the IsObjectiveWidget class.
        """
        recorder_name = "node_link_rec"
        dialog = RecordersDialog(model_config, recorder_name)
        dialog.hide()

        # noinspection PyTypeChecker
        selected_page: RecorderPageWidget = dialog.pages_widget.currentWidget()
        form = selected_page.form

        # noinspection PyUnresolvedReferences
        assert (
            selected_page.findChild(FormField, "name").value() == recorder_name
        )

        # set the lower and upper bound
        l_bound = form.find_field_by_name("constraint_lower_bounds")
        l_bound.widget.line_edit.setText("10")
        u_bound: FormField = form.find_field_by_name("constraint_upper_bounds")
        u_bound.widget.line_edit.setText("1")

        # validate form and error is returned
        QTimer.singleShot(100, close_message_box)
        l_bound.form.validate()
        assert "lower bound must be smaller than" in l_bound.message.text()

    @pytest.mark.parametrize(
        "recorder_name, expected",
        [
            ("obj_min", "minimise"),
            ("obj_max", "maximise"),
            ("obj_minimize", "minimise"),
            ("obj_maximize", "maximise"),
        ],
    )
    def test_is_objective(self, qtbot, model_config, recorder_name, expected):
        """
        Tests the IsObjectiveWidget class.
        """
        dialog = RecordersDialog(model_config, recorder_name)
        dialog.hide()

        # noinspection PyTypeChecker
        selected_page: RecorderPageWidget = dialog.pages_widget.currentWidget()
        form = selected_page.form

        # noinspection PyUnresolvedReferences
        assert (
            selected_page.findChild(FormField, "name").value() == recorder_name
        )
        # check constrain field
        objective_field = form.find_field_by_name("is_objective")

        assert objective_field.value() == expected

    @pytest.mark.parametrize(
        "recorder_name, func, expected_agg_func",
        [
            ("agg_func_product_str", "product", "product"),
            ("agg_func_product_dict", "product", "product"),
            (
                "agg_func_percentile",
                "percentile",
                {
                    "func": "percentile",
                    "args": [70, 95],
                    "kwargs": {"method": "weibull"},
                },
            ),
            (
                "agg_func_percentileofscore",
                "percentileofscore",
                {
                    "func": "percentileofscore",
                    "kwargs": {"score": 0.5, "kind": "strict"},
                },
            ),
        ],
    )
    def test_agg_func(
        self,
        qtbot,
        model_config,
        recorder_name,
        func,
        expected_agg_func: dict[str, str | dict] | str,
    ):
        """
        Tests the agg_func field and all connected fields when the function is
        "percentile" or "percentileofscore"
        """
        dialog = RecordersDialog(model_config, recorder_name)
        dialog.show()

        # noinspection PyTypeChecker
        selected_page: RecorderPageWidget = dialog.pages_widget.currentWidget()
        form = selected_page.form

        # noinspection PyUnresolvedReferences
        assert (
            selected_page.findChild(FormField, "name").value() == recorder_name
        )

        # 1. Test init of widgets
        agg_func_widget: OptAggFuncWidget = form.find_field_by_name(
            "agg_func"
        ).widget

        assert agg_func_widget.get_value() == func

        # if function is not "percentile" or "percentileofscore", related fields are
        # hidden
        hidden_fields = self.percentile_fields + self.percentileofsocre_fields
        visible_fields = []
        if func == "percentile":
            hidden_fields = self.percentileofsocre_fields
            visible_fields = self.percentile_fields
            # check value of fields
            assert (
                form.find_field_by_name(
                    agg_func_widget.agg_func_percentile_list
                ).value()
                == expected_agg_func["args"]
            )
            assert (
                form.find_field_by_name(
                    agg_func_widget.agg_func_percentile_method
                ).value()
                == expected_agg_func["kwargs"]["method"]
            )
        elif func == "percentileofscore":
            hidden_fields = self.percentile_fields
            visible_fields = self.percentileofsocre_fields

            # check value of fields
            assert (
                form.find_field_by_name(
                    agg_func_widget.agg_func_percentileofscore_kind
                ).value()
                == expected_agg_func["kwargs"]["kind"]
            )
            assert (
                form.find_field_by_name(
                    agg_func_widget.agg_func_percentileofscore_score
                ).value()
                == expected_agg_func["kwargs"]["score"]
            )

        # 2. Check field visibility
        for field in hidden_fields:
            assert form.find_field_by_name(field).isVisible() is False
        for field in visible_fields:
            assert form.find_field_by_name(field).isVisible() is True

        # 3. Send form and check resulting dictionary
        form_data = form.save()
        assert form_data == {
            "name": recorder_name,
            "type": "node",
            "node": "Reservoir",
            "is_objective": "maximise",
            "agg_func": expected_agg_func,
        }

        # 4. Changing method shows/hides the related fields
        if func not in ["percentile", "percentileofscore"]:
            agg_func_widget.combo_box.setCurrentText("Percentile")
            # percentile fields are shown
            for field in self.percentile_fields:
                assert form.find_field_by_name(field).isVisible() is True
            agg_func_widget.combo_box.setCurrentText("Percentile of score")
            # percentile fields are shown
            for field in self.percentile_fields:
                assert form.find_field_by_name(field).isVisible() is False
            # percentileofscore fields are shown
            for field in self.percentileofsocre_fields:
                assert form.find_field_by_name(field).isVisible() is True
        else:
            agg_func_widget.combo_box.setCurrentText("Sum")
            # percentile and percentileofscore fields are hidden
            for field in self.percentile_fields + self.percentileofsocre_fields:
                assert form.find_field_by_name(field).isVisible() is False

    @pytest.mark.parametrize(
        "value, error_message",
        [
            # valid
            ("73", None),
            ("40, 60, 95", None),
            # empty
            ("", "must provide a value"),
            # number outside range
            ("600", "percentile must be a number between"),
            # list of numbers outside range
            ("-1, 90", "percentiles must be numbers between"),
        ],
    )
    def test_agg_func_percentile_list(
        self, qtbot, model_config, value, error_message
    ):
        """
        Tests the validation of OptAggFuncPercentileListWidget.
        """
        recorder_name = "agg_func_percentile"
        dialog = RecordersDialog(model_config, recorder_name)
        dialog.show()

        # noinspection PyTypeChecker
        selected_page: RecorderPageWidget = dialog.pages_widget.currentWidget()
        form = selected_page.form
        list_widget: AggFuncPercentileListWidget = form.find_field_by_name(
            OptAggFuncWidget.agg_func_percentile_list
        ).widget

        # noinspection PyUnresolvedReferences
        assert (
            selected_page.findChild(FormField, "name").value() == recorder_name
        )

        # set value and validate
        list_widget.line_edit.setText(value)
        out = list_widget.validate("", "", list_widget.get_value())

        if error_message:
            assert out.validation is False
            assert error_message in out.error_message

    def test_agg_func_percentile_of_score_kind(self, qtbot, model_config):
        """
        Tests the validation of OptAggFuncPercentileOfScoreKindWidget.
        """
        recorder_name = "agg_func_percentileofscore"
        dialog = RecordersDialog(model_config, recorder_name)
        dialog.show()

        # noinspection PyTypeChecker
        selected_page: RecorderPageWidget = dialog.pages_widget.currentWidget()
        form = selected_page.form
        score_widget: AggFuncPercentileOfScoreScoreWidget = (
            form.find_field_by_name(
                OptAggFuncWidget.agg_func_percentileofscore_score
            ).widget
        )

        # empty field and validate
        score_widget.line_edit.setText("")
        out = score_widget.validate("", "", score_widget.get_value())
        assert out.validation is False
        assert "must provide a value" in out.error_message
