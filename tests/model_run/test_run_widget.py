from PySide6.QtCore import Qt
from PySide6.QtTest import QSignalSpy

from pywr_editor import MainWindow
from pywr_editor.model.pywr_worker import RunMode
from pywr_editor.toolbar.run_controls.run_widget import RunWidget
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
        # tooltip contains the model results
        assert "Flow" in window.schematic.schematic_items["Input"].toolTip()

        # 2. Stop the model
        qtbot.mouseClick(run_widget.stop_button, Qt.MouseButton.LeftButton)

        # check worker status just before is killed
        assert worker.is_killed is True

        qtbot.wait(500)
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
        # tooltip contains the model results
        item = window.schematic.schematic_items["Input"]
        assert item.toolTip() == item.tooltip_text

    def test_step_until_end(self, qtbot):
        """
        Tests when the Step button is clicked and the end date is reached.
        """
        window = MainWindow(resolve_model_path("model_to_run.json"))
        window.hide()
        # noinspection PyTypeChecker
        run_widget: RunWidget = window.findChild(RunWidget)

        window.model_config.end_date = "2015-01-05"

        for _ in range(6):
            qtbot.mouseClick(run_widget.stop_button, Qt.MouseButton.LeftButton)

        # model has stopped because it run past the end date
        assert run_widget.worker is None
        assert run_widget.step_button.isEnabled() is True
        assert run_widget.stop_button.isEnabled() is False
