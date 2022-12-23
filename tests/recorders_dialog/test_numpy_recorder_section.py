import pytest

from pywr_editor.dialogs import RecordersDialog
from pywr_editor.dialogs.recorders.recorder_page_widget import (
    RecorderPageWidget,
)
from pywr_editor.form import FormField, TemporalAggFuncWidget
from pywr_editor.model import ModelConfig
from tests.utils import resolve_model_path


class TestDialogRecorderNumpyRecorderSection:
    """
    Tests the general section with the fields to handle the "temporal_agg_func" field
    for numpy recorders.
    """

    percentile_fields = [
        TemporalAggFuncWidget.agg_func_percentile_list,
        TemporalAggFuncWidget.agg_func_percentile_method,
    ]
    percentileofsocre_fields = [
        TemporalAggFuncWidget.agg_func_percentileofscore_score,
        TemporalAggFuncWidget.agg_func_percentileofscore_kind,
    ]

    @pytest.fixture()
    def model_config(self) -> ModelConfig:
        """
        Initialises the model configuration.
        :return: The ModelConfig instance.
        """
        return ModelConfig(resolve_model_path("model_dialog_recorders.json"))

    @pytest.mark.parametrize(
        "recorder_name, func, expected_agg_func",
        [
            ("node_numpy_rec_str", "product", "product"),
            (
                "node_numpy_rec_dict",
                "percentile",
                {
                    "func": "percentile",
                    "args": [70, 95],
                    "kwargs": {"method": "weibull"},
                },
            ),
        ],
    )
    def test_temporal_agg_func_filter(
        self,
        qtbot,
        model_config,
        recorder_name,
        func,
        expected_agg_func: dict[str, str | dict] | str,
    ):
        """
        Tests the section filter for the "temporal_agg_func" field.
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
        agg_func_widget: TemporalAggFuncWidget = form.find_field_by_name(
            "temporal_agg_func"
        ).widget

        # dialog.show()
        # qtbot.wait(6000)
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

        # 2. Check field visibility
        for field in hidden_fields:
            assert form.find_field_by_name(field).isVisible() is False
        for field in visible_fields:
            assert form.find_field_by_name(field).isVisible() is True

        # 3. Send form and check resulting dictionary
        form_data = form.save()
        assert form_data == {
            "name": recorder_name,
            "type": "numpyarraynode",
            "node": "Reservoir",
            "temporal_agg_func": expected_agg_func,
        }

        # 4. Changing method shows/hides the related fields
        if func != "percentile":
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
