import unittest
from unittest.mock import patch

from utils.responsive import ResponsiveLayout


class ResponsiveLayoutTests(unittest.TestCase):
    def test_get_columns_preserves_requested_count_on_every_device(self):
        columns = [object(), object(), object()]

        for device_type in (
            ResponsiveLayout.MOBILE,
            ResponsiveLayout.TABLET,
            ResponsiveLayout.DESKTOP,
        ):
            with self.subTest(device_type=device_type):
                with patch.object(
                    ResponsiveLayout, "get_device_type", return_value=device_type
                ) as detect_device:
                    with patch(
                        "utils.responsive.st.columns", return_value=columns
                    ) as create_columns:
                        result = ResponsiveLayout.get_columns(3)

                create_columns.assert_called_once_with(3)
                detect_device.assert_not_called()
                self.assertIs(result, columns)
