"""
Responsive Layout Utilities for ResumePilot AI

Provides device detection and responsive layout helpers for mobile, tablet, and desktop versions.
Streamlit automatically detects the device based on screen width and browser capabilities.
"""

import streamlit as st
from typing import Literal


class ResponsiveLayout:
    """
    Detects device type and provides responsive layout helpers.
    
    Device Classifications:
    - MOBILE: <= 600px (phones)
    - TABLET: 601px - 1200px (tablets, small laptops)
    - DESKTOP: > 1200px (desktops, large laptops)
    """
    
    # Device type constants
    MOBILE = "mobile"
    TABLET = "tablet"
    DESKTOP = "desktop"
    
    @staticmethod
    def get_device_type() -> Literal["mobile", "tablet", "desktop"]:
        """
        Detect device type from session state.
        Falls back to detecting from browser if available.
        """
        if "device_type" not in st.session_state:
            # Try to get from browser metrics if available
            try:
                # Streamlit 1.28+ supports window dimensions
                if hasattr(st, "session_state") and "_window_size" in st.session_state:
                    width = st.session_state._window_size.get("width", 1200)
                else:
                    width = 1200  # default to desktop
            except:
                width = 1200
            
            # Determine device type based on width
            if width <= 600:
                st.session_state.device_type = ResponsiveLayout.MOBILE
            elif width <= 1200:
                st.session_state.device_type = ResponsiveLayout.TABLET
            else:
                st.session_state.device_type = ResponsiveLayout.DESKTOP
        
        return st.session_state.device_type
    
    @staticmethod
    def is_mobile() -> bool:
        """Check if current device is mobile."""
        return ResponsiveLayout.get_device_type() == ResponsiveLayout.MOBILE
    
    @staticmethod
    def is_tablet() -> bool:
        """Check if current device is tablet."""
        return ResponsiveLayout.get_device_type() == ResponsiveLayout.TABLET
    
    @staticmethod
    def is_desktop() -> bool:
        """Check if current device is desktop."""
        return ResponsiveLayout.get_device_type() == ResponsiveLayout.DESKTOP
    
    @staticmethod
    def get_columns(num_cols: int = 2) -> tuple:
        """
        Return responsive column layout based on device type.
        
        Args:
            num_cols: Desired number of columns on desktop
        
        Returns:
            Tuple of streamlit columns
        
        Example:
            col1, col2 = ResponsiveLayout.get_columns(2)
        """
        device = ResponsiveLayout.get_device_type()
        
        if device == ResponsiveLayout.MOBILE:
            # Mobile: always single column
            return st.columns(1)
        elif device == ResponsiveLayout.TABLET:
            # Tablet: max 2 columns
            return st.columns(min(num_cols, 2))
        else:
            # Desktop: use requested columns
            return st.columns(num_cols)
    
    @staticmethod
    def get_chart_height() -> int:
        """Get responsive chart height based on device."""
        device = ResponsiveLayout.get_device_type()
        
        if device == ResponsiveLayout.MOBILE:
            return 300
        elif device == ResponsiveLayout.TABLET:
            return 350
        else:
            return 400
    
    @staticmethod
    def get_text_area_height() -> int:
        """Get responsive text area height based on device."""
        device = ResponsiveLayout.get_device_type()
        
        if device == ResponsiveLayout.MOBILE:
            return 200
        elif device == ResponsiveLayout.TABLET:
            return 300
        else:
            return 400
    
    @staticmethod
    def configure_page_layout(title: str, icon: str = "🚀"):
        """
        Configure page with responsive settings based on device type.
        
        Args:
            title: Page title
            icon: Page icon emoji
        """
        device = ResponsiveLayout.get_device_type()
        
        # Always use 'wide' layout for better UX on desktop
        # Mobile users will see single column anyway due to responsive design
        st.set_page_config(
            page_title=title,
            page_icon=icon,
            layout="wide",
            initial_sidebar_state="collapsed" if device == ResponsiveLayout.MOBILE else "expanded"
        )
    
    @staticmethod
    def show_mobile_banner() -> None:
        """Show a helpful banner on mobile devices."""
        if ResponsiveLayout.is_mobile():
            st.info(
                "📱 **Optimized for Mobile**\n\n"
                "This app is responsive and works great on your phone! "
                "For the best experience with complex analysis, consider using a tablet or desktop."
            )
    
    @staticmethod
    def render_responsive_columns(content_dict: dict, num_cols: int = 2) -> None:
        """
        Render content across responsive columns.
        
        Args:
            content_dict: Dictionary with column names as keys and content callables as values
            num_cols: Desired columns on desktop
        
        Example:
            ResponsiveLayout.render_responsive_columns({
                "Resume": lambda: st.text_area("Resume"),
                "Job Description": lambda: st.text_area("JD")
            }, num_cols=2)
        """
        cols = ResponsiveLayout.get_columns(num_cols)
        
        for i, (label, content_fn) in enumerate(content_dict.items()):
            if i >= len(cols):
                cols = ResponsiveLayout.get_columns(num_cols)
                i = 0
            
            with cols[i]:
                if content_fn:
                    content_fn()
