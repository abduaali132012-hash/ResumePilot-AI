# 📱 Responsive Design — Testing Guide

This guide helps you test ResumePilot AI's responsive design on mobile, tablet, and desktop devices.

---

## 🧪 Quick Test Setup

### Method 1: Chrome DevTools (Recommended for Quick Testing)

1. **Open the app locally:**
   ```bash
   streamlit run app.py
   ```

2. **Open Chrome DevTools:**
   - Press `F12` or `Ctrl+Shift+I`
   - Click the **Device Toggle** button (top-left, looks like a phone icon)
   - Or press `Ctrl+Shift+M`

3. **Select a device preset:**
   - Mobile: **iPhone 12** (390×844)
   - Tablet: **iPad** (768×1024)
   - Desktop: **Desktop 1920×1080** (or disable device mode)

### Method 2: Real Devices

1. **Deploy to Streamlit Cloud** (see `DEPLOYMENT.md`)
2. **Visit the app URL on:**
   - Phone (iOS or Android)
   - Tablet (iPad or Android)
   - Desktop/Laptop

### Method 3: Manual Resizing

1. **Resize your browser window** to test breakpoints:
   - Mobile: Resize to 375px width
   - Tablet: Resize to 768px width
   - Desktop: Resize to 1920px width

---

## ✅ Mobile (≤600px) Checklist

Test these on a 390px-width viewport (iPhone 12):

- [ ] **Layout**
  - [ ] Content is single-column (no side-by-side sections)
  - [ ] Resume section takes full width
  - [ ] Job description section takes full width
  - [ ] No horizontal scrolling required
  - [ ] Info banner visible at top

- [ ] **Input Fields**
  - [ ] Text areas are 200px tall (comfortable for typing)
  - [ ] Input fields are full-width
  - [ ] Labels are clearly visible above inputs

- [ ] **Buttons**
  - [ ] All buttons are full-width (`use_container_width=True`)
  - [ ] Buttons are easy to tap (at least 44x44 pixels)
  - [ ] Buttons stack vertically (not side-by-side)
  - [ ] Primary button "Analyze Resume" is clearly visible

- [ ] **Sidebar**
  - [ ] Sidebar is collapsed by default
  - [ ] Can be toggled open with menu button (top-left)
  - [ ] Doesn't overlap content when open

- [ ] **Mobile Banner**
  - [ ] Info banner displays: "📱 Optimized for Mobile..."
  - [ ] Banner is visible and readable

---

## 📱 Tablet (601–1200px) Checklist

Test these on a 768px-width viewport (iPad):

- [ ] **Layout**
  - [ ] Two-column layout for resume and job description (side-by-side)
  - [ ] Columns have balanced spacing
  - [ ] No overflow or horizontal scrolling

- [ ] **Input Fields**
  - [ ] Text areas are 300px tall
  - [ ] Comfortable for reading and editing

- [ ] **Buttons**
  - [ ] Buttons are in a grid layout (3 top, 2 bottom)
  - [ ] Buttons use `use_container_width=True` for consistency
  - [ ] Good spacing between buttons

- [ ] **Sidebar**
  - [ ] Sidebar is visible and expanded
  - [ ] Navigation is accessible

- [ ] **Charts/Results**
  - [ ] Charts are 350px tall (responsive height)
  - [ ] Readable and not too cramped

---

## 💻 Desktop (>1200px) Checklist

Test these on a 1920px-width viewport:

- [ ] **Layout**
  - [ ] Multi-column layout fully utilized
  - [ ] Resume and job description side-by-side
  - [ ] Analysis results properly displayed

- [ ] **Input Fields**
  - [ ] Text areas are 400px tall
  - [ ] Plenty of space for content

- [ ] **Buttons**
  - [ ] Buttons in organized grid
  - [ ] Good spacing and alignment
  - [ ] Easy to click with mouse

- [ ] **Sidebar**
  - [ ] Sidebar fully visible and expanded
  - [ ] Navigation items clearly readable

- [ ] **Charts/Results**
  - [ ] Charts are 400px tall (full height)
  - [ ] All visualizations clear and readable

---

## 🔄 Orientation Testing

Test landscape and portrait modes:

### Portrait (Typical)
- [ ] Mobile: Single column, full width
- [ ] Tablet: Two-column layout
- [ ] Desktop: Full multi-column

### Landscape
- [ ] Mobile: Still single column (≤600px width when rotated)
- [ ] Tablet: Two-column layout with adjusted heights
- [ ] Desktop: Full layout

---

## 🎨 Visual Elements Testing

### Step Indicators
- [ ] Mobile: Vertical numbered list
- [ ] Desktop: 3-column grid

### Action Buttons Section
- [ ] Mobile: Vertical stack, labeled "Analysis Tools"
- [ ] Tablet: Grid layout (3 top, 2 bottom)
- [ ] Desktop: Grid layout with good spacing

### Text Area Sizing
- [ ] Heights adapt per device
- [ ] No text is cut off
- [ ] Scrollable when needed

---

## ⚡ Performance Testing

Test performance on different devices:

### Mobile Performance
- [ ] App loads in < 3 seconds
- [ ] No lag when typing in text areas
- [ ] Buttons respond immediately to taps
- [ ] No jank when scrolling

### Tablet Performance
- [ ] App loads in < 2 seconds
- [ ] Smooth interactions
- [ ] Charts render quickly

### Desktop Performance
- [ ] App loads instantly
- [ ] All features work smoothly
- [ ] No performance issues

---

## 🧩 Component-Specific Tests

### File Uploader
- [ ] Upload button is clearly visible
- [ ] File picker works on mobile
- [ ] Success/error messages display correctly

### Text Areas
- [ ] Can type and paste content
- [ ] Scrolling works smoothly
- [ ] Height is appropriate per device

### Tabs (if used)
- [ ] Tabs are clickable on mobile
- [ ] Tab content switches correctly
- [ ] No overlap or layout issues

### Expandable Sections
- [ ] Click to expand works on mobile
- [ ] Content displays correctly when expanded
- [ ] Click to collapse works

### Charts (if present)
- [ ] Charts display at responsive heights
- [ ] Hover tooltips work on desktop
- [ ] Charts don't overflow container

---

## 🐛 Common Issues to Watch For

### ❌ Horizontal Scrolling
**Problem:** Content extends beyond screen width.
**Solution:** Use responsive columns and `use_container_width=True` for buttons.

### ❌ Cut-off Content
**Problem:** Text or elements are cut off on small screens.
**Solution:** Use responsive text area heights and adjust component sizing.

### ❌ Small Touch Targets
**Problem:** Buttons are too small to tap comfortably.
**Solution:** Ensure buttons are full-width with padding (≥44x44 CSS pixels).

### ❌ Sidebar Always Expanded
**Problem:** Sidebar takes up too much space on mobile.
**Solution:** Use `initial_sidebar_state="collapsed"` for mobile.

### ❌ Unreadable Text on Mobile
**Problem:** Font is too small or text is cramped.
**Solution:** Streamlit handles this automatically, but test readability.

---

## 📊 Test Results Template

Use this template to document your testing:

```
Date: ___________
Tester: ___________

MOBILE (≤600px)
- Layout: [ ] Pass [ ] Fail  Notes: ___________
- Buttons: [ ] Pass [ ] Fail  Notes: ___________
- Input: [ ] Pass [ ] Fail  Notes: ___________
- Performance: [ ] Pass [ ] Fail  Notes: ___________

TABLET (601-1200px)
- Layout: [ ] Pass [ ] Fail  Notes: ___________
- Buttons: [ ] Pass [ ] Fail  Notes: ___________
- Input: [ ] Pass [ ] Fail  Notes: ___________
- Performance: [ ] Pass [ ] Fail  Notes: ___________

DESKTOP (>1200px)
- Layout: [ ] Pass [ ] Fail  Notes: ___________
- Buttons: [ ] Pass [ ] Fail  Notes: ___________
- Input: [ ] Pass [ ] Fail  Notes: ___________
- Performance: [ ] Pass [ ] Fail  Notes: ___________

OVERALL: [ ] Pass [ ] Fail
Issues: ___________
```

---

## 🚀 Automated Testing (Advanced)

For automated testing of responsive layouts, consider:

1. **Playwright** (headless browser automation)
   ```bash
   pip install playwright
   pytest --headed --viewport-size 390,844  # Mobile
   ```

2. **Cypress** (end-to-end testing)
   ```bash
   npm install cypress
   npx cypress run --config viewportWidth=390,viewportHeight=844
   ```

3. **Lighthouse** (Google's audit tool)
   ```bash
   # Built into Chrome DevTools
   F12 → Lighthouse → Generate report
   ```

---

## 📱 Device Emulation Details

### Chrome DevTools Presets

| Device | Viewport | DPI | User Agent |
|--------|----------|-----|-----------|
| iPhone 12 | 390×844 | 460 | Apple/iOS |
| iPad | 768×1024 | 264 | Apple/iOS |
| Galaxy S10 | 360×800 | 412 | Google/Android |
| Desktop | 1920×1080 | 96 | Windows/macOS |

### Testing Checklist by Breakpoint

**375px (Small Mobile)**
- [ ] Content readable without horizontal scroll
- [ ] Buttons are full-width
- [ ] No overlapping elements

**600px (Large Mobile)**
- [ ] Same as 375px
- [ ] Sidebar can be toggled

**768px (Tablet Portrait)**
- [ ] Two-column layout works
- [ ] Charts render well
- [ ] Touch targets are large

**1024px (Tablet Landscape)**
- [ ] Full layout visible
- [ ] All features accessible

**1920px (Desktop)**
- [ ] Maximum columns utilized
- [ ] Professional appearance

---

## ✅ Final Checklist

Before deploying:

- [ ] Tested on at least 3 device sizes (mobile, tablet, desktop)
- [ ] No horizontal scrolling on mobile
- [ ] All buttons are clickable on touch devices
- [ ] Text is readable on all devices
- [ ] Images/charts scale properly
- [ ] Forms are usable on mobile
- [ ] Loading states are visible
- [ ] Error messages display correctly
- [ ] Performance is acceptable on all devices
- [ ] Accessibility is maintained (text contrast, etc.)

---

## 📞 Need Help?

If you encounter issues:

1. Check `RESPONSIVE_DESIGN.md` for implementation details
2. Review `utils/responsive.py` for available utilities
3. Test in Chrome DevTools with exact breakpoints
4. Check browser console (F12 → Console) for JavaScript errors
5. Compare your implementation with the main app.py

---

Happy testing! 🎉
