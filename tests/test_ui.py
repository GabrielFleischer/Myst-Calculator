"""Tests for the user-interface placeholder."""

import unittest
from unittest.mock import Mock, patch

from myst_calculator.ui import launch


class UiTest(unittest.TestCase):
    """Test the placeholder UI entry point."""

    @patch("builtins.print")
    def test_launch_prints_placeholder_message(self, print_mock: Mock) -> None:
        """Launching the UI prints a placeholder message."""
        result = launch()

        self.assertEqual(result, 0)
        print_mock.assert_called_once_with("Myst Calculator UI is not implemented yet :P")


if __name__ == "__main__":
    unittest.main()
