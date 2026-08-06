```js
// Extracts the job posting from the page for ResumePilot AI.
(() => {
  function pickTitle() {
    const selectors = [
      ".job-title", "[data-testid='job-title']", ".jobsearch-JobInfoHeader-title",
      "h1", ".topcard__title", ".job-details-jobs-unified-top-card__job-title"
    ];
    for (const sel of selectors) {
      const el = document.querySelector(sel);
      if (el && el.textContent.trim()) return el.textContent.trim();
    }
    return document.title.replace(/\s*[|\-].*$/, "").trim();
  }

  function pickCompany() {
    const selectors = [
      ".job-company", "[data-testid='job-company']", ".topcard__org-name-link",
      ".job-details-jobs-unified-top-card__company-name", ".employer-name"
    ];
    for (const sel of selectors) {
      const el = document.querySelector(sel);
      if (el && el.textContent.trim()) return el.textContent.trim();
    }
    return "";
  }

  function pickDescription() {
    const selectors = [
      "#job-description", ".job-description", "[data-testid='job-details']",
      ".show-more-less-html", ".jobsearch-JobComponent-description"
    ];
    for (const sel of selectors) {
      const el = document.querySelector(sel);
      if (el && el.textContent.trim().length > 200) return el.textContent.trim();
    }
    // Fallback: use the largest text block in <main>.
    const main = document.querySelector("main") || document.body;
    const text = main.innerText.trim();
    return text.length > 300 ? text.slice(0, 20000) : "";
  }

  chrome.runtime.onMessage.addListener((msg, _sender, sendResponse) => {
    if (msg && msg.type === "EXTRACT_JOB") {
      sendResponse({
        title: pickTitle(),
        company: pickCompany(),
        description: pickDescription(),
        url: window.location.href
      });
    }
    return true;
  });
})();
```
