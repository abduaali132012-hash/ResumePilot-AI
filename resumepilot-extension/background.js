```js
chrome.runtime.onInstalled.addListener(() => {
  chrome.contextMenus.create({
    id: "send-to-resumepilot",
    title: "Send selected job text to ResumePilot AI",
    contexts: ["selection"]
  });
});

chrome.contextMenus.onClicked.addListener((info) => {
  if (info.menuItemId === "send-to-resumepilot" && info.selectionText) {
    const base = "https://resumepilot-ai-vngmvb9m6rdgszr7bthtbk.streamlit.app";
    chrome.tabs.create({ url: base + "?jd=" + encodeURIComponent(info.selectionText.slice(0, 12000)) });
  }
});
```

## Install it

1. Open `chrome://extensions`.
2. Enable **Developer mode** (top-right).
3. Click **Load unpacked** and select the `resumepilot-extension/` folder.
4. Pin the extension, open any job posting, and click the icon.

## Accept the job in your Streamlit app

Add this snippet near the top of your **Analyze page** so the extension's `?jd=...` URL auto-fills the job description:

```python
# At the top of the Analyze page:
import streamlit as st

jd = st.query_params.get("jd")
if jd and "jd_pinned" not in st.session_state:
    st.session_state["jd_pinned"] = True

# Then use it as the default value of your job description input, e.g.:
job_description = st.text_area(
    "Job description",
    value=st.session_state.get("jd_text", ""),
    height=220,
)
if jd and not st.session_state.get("jd_text"):
    st.session_state["jd_text"] = jd
```
