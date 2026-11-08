import unittest
from types import SimpleNamespace
from unittest.mock import MagicMock, call, patch

from utils import responsive
from utils.responsive import ResponsiveLayout


class ResponsiveLayoutTests(unittest.TestCase):
    def setUp(self):
        self.state = {}
        self.streamlit = SimpleNamespace(
            session_state=self.state,
            columns=MagicMock(),
            info=MagicMock(),
            set_page_config=MagicMock(),
        )
        self.streamlit_patch = patch.object(responsive, "st", self.streamlit)
        self.streamlit_patch.start()
        self.addCleanup(self.streamlit_patch.stop)

    def test_device_classification_tracks_measured_width_and_thresholds(self):
        cases = (
            (600, ResponsiveLayout.MOBILE),
            (601, ResponsiveLayout.TABLET),
            (1200, ResponsiveLayout.TABLET),
            (1201, ResponsiveLayout.DESKTOP),
        )
        for width, expected in cases:
            with self.subTest(width=width):
                self.state[responsive._VIEWPORT_STATE_KEY] = width
                self.assertEqual(ResponsiveLayout.get_device_type(), expected)

    def test_device_helpers_use_current_viewport_classification(self):
        self.state[responsive._VIEWPORT_STATE_KEY] = 500
        self.assertTrue(ResponsiveLayout.is_mobile())
        self.state[responsive._VIEWPORT_STATE_KEY] = 800
        self.assertTrue(ResponsiveLayout.is_tablet())
        self.state[responsive._VIEWPORT_STATE_KEY] = 1400
        self.assertTrue(ResponsiveLayout.is_desktop())

    def test_device_type_ignores_stale_cached_classification(self):
        self.state["device_type"] = ResponsiveLayout.MOBILE
        self.state[responsive._VIEWPORT_STATE_KEY] = 1200
        self.assertEqual(
            ResponsiveLayout.get_device_type(),
            ResponsiveLayout.TABLET,
        )

    def test_unmeasured_viewport_uses_desktop_fallback(self):
        self.assertEqual(
            ResponsiveLayout.get_device_type(),
            ResponsiveLayout.DESKTOP,
        )

    def test_update_viewport_stores_new_measurement(self):
        with patch.object(responsive, "_VIEWPORT_COMPONENT", return_value=390):
            self.assertEqual(ResponsiveLayout.update_viewport(), 390)
        self.assertEqual(self.state[responsive._VIEWPORT_STATE_KEY], 390)

    def test_update_viewport_keeps_last_measurement_when_component_has_no_value(self):
        self.state[responsive._VIEWPORT_STATE_KEY] = 768
        with patch.object(responsive, "_VIEWPORT_COMPONENT", return_value=None):
            self.assertEqual(ResponsiveLayout.update_viewport(), 768)
        self.assertEqual(self.state[responsive._VIEWPORT_STATE_KEY], 768)

    def test_update_viewport_rejects_invalid_measurements(self):
        for width in (0, -1, "390", True):
            with self.subTest(width=width):
                with patch.object(responsive, "_VIEWPORT_COMPONENT", return_value=width):
                    with self.assertRaises(ValueError):
                        ResponsiveLayout.update_viewport()

    def test_chart_and_text_area_heights_follow_device_class(self):
        cases = (
            (500, 300, 200),
            (800, 350, 300),
            (1400, 400, 400),
        )
        for width, chart_height, text_area_height in cases:
            with self.subTest(width=width):
                self.state[responsive._VIEWPORT_STATE_KEY] = width
                self.assertEqual(ResponsiveLayout.get_chart_height(), chart_height)
                self.assertEqual(
                    ResponsiveLayout.get_text_area_height(),
                    text_area_height,
                )

    def test_get_columns_caps_column_count_by_device(self):
        columns = [object(), object(), object()]
        self.streamlit.columns.return_value = columns

        for width, expected_count in ((500, 1), (800, 2), (1400, 2)):
            with self.subTest(width=width):
                self.state[responsive._VIEWPORT_STATE_KEY] = width
                result = ResponsiveLayout.get_columns(3)
                self.assertIs(result, columns)

        self.assertEqual(
            self.streamlit.columns.call_args_list,
            [call(1), call(2), call(2)],
        )

    def test_get_columns_rejects_non_positive_or_non_integer_count(self):
        for count in (0, -1, 1.5, True):
            with self.subTest(count=count):
                with self.assertRaises(ValueError):
                    ResponsiveLayout.get_columns(count)
        self.streamlit.columns.assert_not_called()

    def test_mobile_banner_is_only_shown_on_mobile(self):
        with patch.object(ResponsiveLayout, "get_device_type", return_value="mobile"):
            ResponsiveLayout.show_mobile_banner()
        self.streamlit.info.assert_called_once()

        self.streamlit.info.reset_mock()
        with patch.object(ResponsiveLayout, "get_device_type", return_value="tablet"):
            ResponsiveLayout.show_mobile_banner()
        self.streamlit.info.assert_not_called()

    def test_page_configuration_precedes_viewport_component(self):
        events = []
        self.streamlit.set_page_config.side_effect = lambda **kwargs: events.append(
            ("page_config", kwargs)
        )

        def update_viewport():
            events.append(("viewport", None))

        with patch.object(ResponsiveLayout, "update_viewport", side_effect=update_viewport):
            ResponsiveLayout.configure_page_layout("Test page", icon="🧪")

        self.assertEqual(events[0][0], "page_config")
        self.assertEqual(events[0][1]["initial_sidebar_state"], "auto")
        self.assertEqual(events[1][0], "viewport")

    def test_render_responsive_columns_groups_items_into_rows(self):
        first_row = [MagicMock(), MagicMock()]
        second_row = [MagicMock()]
        self.streamlit.columns.side_effect = [first_row, second_row]
        rendered = []
        content = {
            "One": lambda: rendered.append("One"),
            "Two": lambda: rendered.append("Two"),
            "Three": lambda: rendered.append("Three"),
        }

        ResponsiveLayout.render_responsive_columns(content, num_cols=2)

        self.assertEqual(
            self.streamlit.columns.call_args_list,
            [call(2), call(1)],
        )
        self.assertEqual(rendered, ["One", "Two", "Three"])

    def test_render_responsive_columns_handles_empty_content(self):
        ResponsiveLayout.render_responsive_columns({}, num_cols=2)
        self.streamlit.columns.assert_not_called()

    def test_render_responsive_columns_stacks_all_content_on_mobile(self):
        self.state[responsive._VIEWPORT_STATE_KEY] = 390
        columns = [MagicMock()]
        self.streamlit.columns.return_value = columns
        rendered = []
        content = {
            "One": lambda: rendered.append("One"),
            "Two": lambda: rendered.append("Two"),
            "Three": lambda: rendered.append("Three"),
        }

        ResponsiveLayout.render_responsive_columns(content, num_cols=3)

        self.assertEqual(
            self.streamlit.columns.call_args_list,
            [call(1), call(1), call(1)],
        )
        self.assertEqual(rendered, ["One", "Two", "Three"])


if __name__ == "__main__":
    unittest.main()
