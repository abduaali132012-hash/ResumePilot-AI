# 📱 ResumePilot AI — Responsive Design Guide

ResumePilot AI includes responsive helpers for **mobile**, **tablet**, and
**desktop** viewports. Browser width is measured by a small local Streamlit
component and refreshed when the viewport is resized.

---

## 🎯 Device Classifications

The app classifies the measured viewport width as follows:

| Device | Width | Layout | Sidebar | Use Case |
| -------- | ------- | -------- | --------- | ---------- |
| 📱 **Mobile** | ≤ 600px | Single column, stacked | Collapsed | Phones, small devices |
| 📱 **Tablet** | 601–1200px | 2 columns max, flexible | Expanded | iPads, small laptops |
| 💻 **Desktop** | > 1200px | Up to 2 columns | Expanded | Large laptops, desktops |

---

## ✨ Responsive Features

### 1. **Adaptive Layout**

**Mobile View:**

- Single-column layout for better readability
- Resume and job description stack vertically
- Buttons full-width for easier clicking on touch screens
- Sidebar collapses automatically

**Tablet View:**

- 2-column layout where appropriate
- Balanced spacing and font sizes
- Sidebar visible for navigation

**Desktop View:**
- Up to 2 columns
- Charts at optimal 400px height
- Sidebar fully expanded

### 2. **Dynamic Components**

The `ResponsiveLayout` utility class in `utils/responsive.py` provides:

```python
from utils.responsive import ResponsiveLayout

# Detect device type after the page has been configured
device = ResponsiveLayout.get_device_type()  # Returns: "mobile", "tablet", or "desktop"

# Check specific device
if ResponsiveLayout.is_mobile():
    # Mobile-specific logic
    
# Create at most 1 mobile or 2 tablet/desktop columns.
cols = ResponsiveLayout.get_columns(num_cols=3)

# Get optimal heights
height = ResponsiveLayout.get_text_area_height()  # 200px mobile, 300px tablet, 400px desktop
height = ResponsiveLayout.get_chart_height()      # 300px mobile, 350px tablet, 400px desktop