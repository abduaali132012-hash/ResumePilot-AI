```js
const APP_URL_DEFAULT = "https://resumepilot-ai-vngmvb9m6rdgszr7bthtbk.streamlit.app";

let current = null;

async function getJob() {
  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
  if (!tab || !tab.id) return null;
  try {
    return await chrome.tabs.sendMessage(tab.id, { type: "EXTRACT_JOB" });
  } catch {
    return null;
  }
}

function render(data) {
  document.getElementById("jobTitle").textContent = data.title || "No job detected";
  document.getElementById("jobCompany").textContent = data.company || "";
  document.getElementById("charCount").textContent = (data.description || "").length + " chars";
}

document.getElementById("openApp").addEventListener("click", () => {
  if (!current || !current.description) {
    document.getElementById("error").textContent = "Couldn't find a job description on this page.";
    return;
  }
  const base = document.getElementById("appUrl").value.trim() || APP_URL_DEFAULT;
  const url = base.split("?")[0] + "?jd=" + encodeURIComponent(current.description.slice(0, 12000));
  chrome.tabs.create({ url });
});

document.getElementById("copyJd").addEventListener("click", async () => {
  if (!current || !current.description) {
    document.getElementById("error").textContent = "No job description to copy.";
    return;
  }
  await navigator.clipboard.writeText(current.description);
  document.getElementById("error").textContent = "Copied!";
});

(async () => {
  current = await getJob();
  if (current) {
    render(current);
  } else {
    document.getElementById("error").textContent = "Tip: open a job posting first (LinkedIn, Indeed, Glassdoor…).";
  }
})();
```
