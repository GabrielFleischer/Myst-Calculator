"""Tests for the desktop user-interface entry point."""

import unittest
from unittest.mock import Mock, patch

from myst_calculator.ui.app import MystCalculatorApp, launch


class UiTest(unittest.TestCase):
    """Test desktop application launch behavior."""

    @patch("myst_calculator.ui.app.MystCalculatorApp")
    def test_launch_runs_application_event_loop(self, app_class: Mock) -> None:
        """Launching creates the application and enters its event loop."""
        app = Mock()
        app_class.return_value = app

        result = launch()

        self.assertEqual(result, 0)
        app_class.assert_called_once_with()
        app.mainloop.assert_called_once_with()

    def test_close_cancels_active_work_before_destroying_window(self) -> None:
        """Closing the app requests tab shutdown before destroying the window."""
        app = Mock()
        app._opposed_tab = Mock()

        MystCalculatorApp.close(app)

        app._opposed_tab.shutdown.assert_called_once_with()
        app.destroy.assert_called_once_with()


if __name__ == "__main__":
    unittest.main()
