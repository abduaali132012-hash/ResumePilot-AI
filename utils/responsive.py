"""Responsive layout helpers backed by a measured browser viewport."""

from pathlib import Path
from typing import Callable, Dict, List, Literal, Optional

import streamlit as st
import streamlit.components.v1 as components

DeviceType = Literal["mobile", "tablet", "desktop"]
ContentCallback = Optional[Callable[[], object]]

_VIEWPORT_STATE_KEY = "_responsive_viewport_width"
_DEFAULT_VIEWPORT_WIDTH = 1280
_VIEWPORT_COMPONENT = components.declare_component(
    "resumepilot_viewport",
    path=str(Path(__file__).parent / "viewport_component"),
)


class ResponsiveLayout:
    """Detect viewport classes and provide responsive Streamlit layout helpers.

    Device widths are measured in the browser: mobile is at most 600px, tablet
    is 601–1200px, and desktop is wider than 1200px. Before the component's
    first measurement, the helpers use a 1280px desktop fallback.
    """

    MOBILE = "mobile"
    TABLET = "tablet"
    DESKTOP = "desktop"

    @staticmethod
    def _validate_width(width: object) -> int:
        if isinstance(width, bool) or not isinstance(width, int) or width <= 0:
            raise ValueError("Viewport width must be a positive integer.")
        return width

    @staticmethod
    def update_viewport() -> Optional[int]:
        """Measure the browser viewport and store the latest reported width."""
        width = _VIEWPORT_COMPONENT(key="resumepilot_viewport_width", default=None)
        if width is None:
            return st.session_state.get(_VIEWPORT_STATE_KEY)

        width = ResponsiveLayout._validate_width(width)
        st.session_state[_VIEWPORT_STATE_KEY] = width
        return width

    @staticmethod
    def get_device_type() -> DeviceType:
        """Classify the latest measured viewport, without caching the result."""
        width = st.session_state.get(_VIEWPORT_STATE_KEY, _DEFAULT_VIEWPORT_WIDTH)
        width = ResponsiveLayout._validate_width(width)
        if width <= 600:
            return ResponsiveLayout.MOBILE
        if width <= 1200:
            return ResponsiveLayout.TABLET
        return ResponsiveLayout.DESKTOP

    @staticmethod
    def is_mobile() -> bool:
        return ResponsiveLayout.get_device_type() == ResponsiveLayout.MOBILE

    @staticmethod
    def is_tablet() -> bool:
        return ResponsiveLayout.get_device_type() == ResponsiveLayout.TABLET

    @staticmethod
    def is_desktop() -> bool:
        return ResponsiveLayout.get_device_type() == ResponsiveLayout.DESKTOP

    @staticmethod
    def _column_count(num_cols: int) -> int:
        device_limits = {
            ResponsiveLayout.MOBILE: 1,
            ResponsiveLayout.TABLET: 2,
            ResponsiveLayout.DESKTOP: 2,
        }
        return min(num_cols, device_limits[ResponsiveLayout.get_device_type()])

    @staticmethod
    def get_columns(num_cols: int = 2) -> List[object]:
        """Create at most one mobile or two tablet/desktop columns."""
        if isinstance(num_cols, bool) or not isinstance(num_cols, int) or num_cols < 1:
            raise ValueError("num_cols must be a positive integer.")
        return st.columns(ResponsiveLayout._column_count(num_cols))

    @staticmethod
    def get_chart_height() -> int:
        """Get the chart height for the current viewport class."""
        return {
            ResponsiveLayout.MOBILE: 300,
            ResponsiveLayout.TABLET: 350,
            ResponsiveLayout.DESKTOP: 400,
        }[ResponsiveLayout.get_device_type()]

    @staticmethod
    def get_text_area_height() -> int:
        """Get the text-area height for the current viewport class."""
        return {
            ResponsiveLayout.MOBILE: 200,
            ResponsiveLayout.TABLET: 300,
            ResponsiveLayout.DESKTOP: 400,
        }[ResponsiveLayout.get_device_type()]

    @staticmethod
    def configure_page_layout(title: str, icon: str = "🚀") -> None:
        """Configure Streamlit before rendering the viewport-measuring component.

        Streamlit must receive page configuration before any other Streamlit
        element. Its ``auto`` sidebar state follows the browser's own
        responsive behavior on the first render.
        """
        st.set_page_config(
            page_title=title,
            page_icon=icon,
            layout="wide",
            initial_sidebar_state="auto",
        )
        ResponsiveLayout.update_viewport()

    @staticmethod
    def show_mobile_banner() -> None:
        """Show a helpful banner on mobile viewports."""
        if ResponsiveLayout.is_mobile():
            st.info(
                "📱 **Optimized for Mobile**\n\n"
                "This app is responsive and works great on your phone! "
                "For the best experience with complex analysis, consider using a tablet or desktop."
            )

    @staticmethod
    def render_responsive_columns(
        content_dict: Dict[str, ContentCallback],
        num_cols: int = 2,
    ) -> None:
        """Render callbacks in predictable rows of at most ``num_cols`` items."""
        if isinstance(num_cols, bool) or not isinstance(num_cols, int) or num_cols < 1:
            raise ValueError("num_cols must be a positive integer.")

        columns_per_row = ResponsiveLayout._column_count(num_cols)
        items = list(content_dict.items())
        for start in range(0, len(items), columns_per_row):
            row = items[start : start + columns_per_row]
            columns = ResponsiveLayout.get_columns(len(row))
            for column, (_, content_fn) in zip(columns, row):
                with column:
                    if content_fn is not None:
                        content_fn()
