from datetime import datetime

import pandas as pd
import pytest
from PySide6.QtCore import QDate, Qt
from PySide6.QtTest import QSignalSpy
from PySide6.QtWidgets import QGraphicsItem

from pywr_editor import MainWindow
from pywr_editor.model.pywr_worker import RunMode
from pywr_editor.toolbar.node_library.schematic_items_library import (
    SchematicItemsLibrary,
)
from pywr_editor.toolbar.run_controls.run_widget import RunWidget
from pywr_editor.widgets import DateEdit, SpinBox
from tests.utils import resolve_model_path


class TestRunWidget:
    """
    Tests the widget and thread when a model is run.
    """

    def test_step_one(self, qtbot):
        """
        Tests when the Step button is clicked.
        """
        window = MainWindow(resolve_model_path("model_to_run.json"))
        window.hide()
        # noinspection PyTypeChecker
        run_widget: RunWidget = window.findChild(RunWidget)
        run_status_changed_spy = QSignalSpy(run_widget.run_status_changed)
        node_item = window.schematic.node_items["Input"]

        # check button status before running the model
        assert run_widget.step_button.isEnabled() is True
        assert run_widget.stop_button.isEnabled() is False
        assert run_widget.run_button.isEnabled() is True
        assert run_widget.run_to_button.isEnabled() is True
        assert run_widget.inspector_action.isEnabled() is False

        # 1. Step
        qtbot.mouseClick(run_widget.step_button, Qt.MouseButton.LeftButton)
        # worker instance becomes available when model is running
        worker = run_widget.worker
        finished_spy = QSignalSpy(worker.finished)
        before_step_spy = QSignalSpy(worker.before_step)
        step_done_spy = QSignalSpy(worker.step_done)
        progress_update_spy = QSignalSpy(worker.progress_update)

        # model is running (the test is very fast and captures the instance when
        # the model is still working
        assert worker.mode == RunMode.STEP
        assert worker.is_killed is False
        assert run_widget.is_running is True

        # model has paused
        qtbot.wait(700)
        assert run_widget.step_button.isEnabled() is True
        assert run_widget.stop_button.isEnabled() is True
        assert run_widget.run_button.isEnabled() is True
        assert run_widget.run_to_button.isEnabled() is True
        assert run_widget.inspector_action.isEnabled() is True

        # check signals
        assert run_status_changed_spy.count() == 1
        assert finished_spy.count() == 0
        assert before_step_spy.count() == 1
        assert step_done_spy.count() == 1
        assert progress_update_spy.count() == 1

        # check worker status flags
        assert worker.is_killed is False
        assert worker.is_paused is True
        assert worker.mode is None

        # check schematic
        assert window.schematic.canvas.opacity != 1
        # items are locked and not selectable
        assert (
            bool(
                node_item.flags()
                & QGraphicsItem.GraphicsItemFlag.ItemIsSelectable
            )
            is False
        )
        assert (
            bool(
                node_item.flags() & QGraphicsItem.GraphicsItemFlag.ItemIsMovable
            )
            is False
        )

        # tooltip contains the model results
        assert "Flow" in node_item.toolTip()

        # check toolbar buttons
        disabled_actions = [
            "edit-metadata",
            "edit-scenarios",
            "edit-imports",
            "edit-slots",
            "edit-tables",
            "edit-parameters",
            "edit-recorders",
            "find-orphaned-nodes",
            "find-orphaned-parameters",
        ]
        for action_name in disabled_actions:
            assert (
                window.app_actions.get(action_name).isEnabled() is False
            ), action_name

        # node library is disabled
        node_library: SchematicItemsLibrary = window.toolbar.findChild(
            SchematicItemsLibrary
        )
        assert node_library.isEnabled() is False

        # date widgets are disabled
        for widget_name in [
            "start_date",
            "end_date",
            "run_to_date",
        ]:
            assert (
                window.toolbar.findChild(DateEdit, widget_name).isEnabled()
                is False
            )
        assert (
            window.toolbar.findChild(SpinBox, "time_step").isEnabled() is False
        )

        # 2. Stop the model
        qtbot.mouseClick(run_widget.stop_button, Qt.MouseButton.LeftButton)

        # check worker status just before is killed
        assert worker.is_killed is True
        qtbot.wait(200)
        assert worker.pywr_model is None

        # worker and widget emits the signals
        assert run_status_changed_spy.count() == 2
        assert finished_spy.count() == 1

        assert run_widget.is_running is False

        # check buttons
        assert run_widget.run_button.isEnabled() is True
        assert run_widget.run_to_button.isEnabled() is True
        assert run_widget.step_button.isEnabled() is True
        assert run_widget.stop_button.isEnabled() is False
        assert run_widget.inspector_action.isEnabled() is False

        # schematic status and tooltip are restored
        assert window.schematic.canvas.opacity() == 1
        assert (
            bool(
                node_item.flags()
                & QGraphicsItem.GraphicsItemFlag.ItemIsSelectable
            )
            is True
        )
        assert (
            bool(
                node_item.flags() & QGraphicsItem.GraphicsItemFlag.ItemIsMovable
            )
            is True
        )
        # tooltip contains the model results
        item = window.schematic.node_items["Input"]
        assert item.toolTip() == item.tooltip_text

        # check toolbar buttons
        for action_name in disabled_actions:
            assert window.app_actions.get(action_name).isEnabled(), action_name

        # node library is enabled
        node_library: SchematicItemsLibrary = window.toolbar.findChild(
            SchematicItemsLibrary
        )
        assert node_library.isEnabled()

        # date widgets are enabled
        for widget_name in [
            "start_date",
            "end_date",
            "run_to_date",
        ]:
            assert window.toolbar.findChild(DateEdit, widget_name).isEnabled()
        assert window.toolbar.findChild(SpinBox, "time_step").isEnabled()

    def test_step_until_end(self, qtbot):
        """
        Tests when the Step button is clicked and the end date is reached.
        This also tests that the run to button is disabled past the run-to date.
        """
        window = MainWindow(resolve_model_path("model_to_run.json"))
        window.hide()
        # noinspection PyTypeChecker
        run_widget: RunWidget = window.findChild(RunWidget)
        # noinspection PyTypeChecker
        run_to_date_widget: DateEdit = window.findChild(DateEdit, "run_to_date")

        run_to_date = QDate(2015, 1, 3)
        run_to_date_widget.setDate(run_to_date)
        window.model_config.end_date = "2015-01-05"

        # 1. Step until the end date
        for d in range(5):
            qtbot.mouseClick(run_widget.step_button, Qt.MouseButton.LeftButton)
            qtbot.wait(200)

            # check progress
            # noinspection PyUnresolvedReferences
            t = (
                run_widget.worker.pywr_model.timestepper.current.period.to_timestamp()
            )
            assert t == pd.Timestamp(2015, 1, d + 1)
            assert run_widget.progress_status.text() == pd.Timestamp(
                2015, 1, d + 1
            ).strftime("%d/%m/%Y")

            # the model is still paused to let user inspect results
            assert run_widget.worker.is_paused is True

            # check run-to button status. Button is disabled after the run-to date
            if t < pd.Timestamp(run_to_date.toPython()):
                assert run_widget.run_to_button.isEnabled() is True
            else:
                assert run_widget.run_to_button.isEnabled() is False

            # run button is still enabled until the last time step
            if t != pd.Timestamp(window.model_config.end_date):
                assert run_widget.run_button.isEnabled() is True

            # timestepper fields are disabled
            assert all(
                [not w.isEnabled() for w in window.findChildren(DateEdit)]
            )

        assert run_widget.worker is not None
        assert run_widget.worker.is_paused is True

        # step button is disabled because end date was reached
        assert run_widget.step_button.isEnabled() is False
        assert run_widget.run_to_button.isEnabled() is False
        assert run_widget.stop_button.isEnabled() is True
        assert run_widget.run_button.isEnabled() is False

        # 2. Stop the run
        qtbot.mouseClick(run_widget.stop_button, Qt.MouseButton.LeftButton)
        qtbot.wait(200)

        assert run_widget.progress_status.text() == "Ready to run"

        # model has stopped because it run past the end date
        assert run_widget.worker.is_killed is True
        assert run_widget.run_button.isEnabled() is True
        assert run_widget.run_to_button.isEnabled() is True
        assert run_widget.step_button.isEnabled() is True
        assert run_widget.stop_button.isEnabled() is False

        # timestepper fields are enabled
        assert all([w.isEnabled() for w in window.findChildren(DateEdit)])

    @pytest.mark.parametrize("run_to_date", [(2015, 8, 1), (2015, 12, 31)])
    def test_run_to(self, qtbot, run_to_date: tuple[int]):
        """
        Tests when the "Run to" button is clicked.
        """
        window = MainWindow(resolve_model_path("model_to_run.json"))
        window.hide()

        # noinspection PyTypeChecker
        run_widget: RunWidget = window.findChild(RunWidget)
        run_status_changed_spy = QSignalSpy(run_widget.run_status_changed)

        # check button status before running the model
        assert run_widget.step_button.isEnabled() is True
        assert run_widget.stop_button.isEnabled() is False
        assert run_widget.run_button.isEnabled() is True
        assert run_widget.run_to_button.isEnabled() is True
        assert run_widget.inspector_action.isEnabled() is False

        # 1. Set run to and run the model
        run_to: DateEdit = window.toolbar.findChild(DateEdit, "run_to_date")
        run_to.setDate(QDate(*run_to_date))
        qtbot.mouseClick(run_widget.run_to_button, Qt.MouseButton.LeftButton)

        # worker instance becomes available when model is running
        worker = run_widget.worker
        finished_spy = QSignalSpy(worker.finished)
        before_run_to_spy = QSignalSpy(worker.before_run_to)
        run_to_done_spy = QSignalSpy(worker.run_to_done)
        progress_update_spy = QSignalSpy(worker.progress_update)

        assert worker.mode == RunMode.RUN_TO
        assert worker.is_killed is False
        assert run_widget.is_running is True

        # model has paused
        qtbot.wait(400)
        is_end_date = run_to_date == (2015, 12, 31)
        # step and run buttons are disabled if end date ir reached
        assert run_widget.step_button.isEnabled() is not is_end_date
        assert run_widget.stop_button.isEnabled() is True
        assert run_widget.run_button.isEnabled() is not is_end_date
        assert run_widget.run_to_button.isEnabled() is False
        assert run_widget.inspector_action.isEnabled() is True

        # check signals
        assert run_status_changed_spy.count() == 1
        assert finished_spy.count() == 0
        assert before_run_to_spy.count() == 1
        assert run_to_done_spy.count() == 1
        delta_date = datetime(*run_to_date) - datetime(2015, 1, 1)
        assert progress_update_spy.count() == delta_date.days + 1

        # check worker status flags
        assert worker.is_killed is False
        assert worker.is_paused is True
        assert worker.mode is None

        # 2. Check current date
        assert run_widget.progress_status.text() == datetime(
            *run_to_date
        ).strftime("%d/%m/%Y")

        # noinspection PyUnresolvedReferences
        c = run_widget.worker.pywr_model.timestepper.current
        assert c.day == run_to_date[-1]
        assert c.month == run_to_date[1]
        assert c.year == run_to_date[0]

        # 3. stop run to prevent test to exit with code > 0
        qtbot.mouseClick(run_widget.stop_button, Qt.MouseButton.LeftButton)
