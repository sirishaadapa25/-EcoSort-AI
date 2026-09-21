"use strict";

// The Flask backend must be running (see README). Change the port here if you change it there.
const API_BASE = "http://localhost:5000";
const ANALYZE_URL = API_BASE + "/api/analyze";
const REQUEST_TIMEOUT_MS = 35000;

const form = document.getElementById("analyze-form");
const input = document.getElementById("waste-input");
const button = document.getElementById("analyze-btn");
const inputError = document.getElementById("input-error");
const panel = document.getElementById("result-panel");
const states = {
  empty: document.getElementById("state-empty"),
  loading: document.getElementById("state-loading"),
  error: document.getElementById("state-error"),
  result: document.getElementById("result"),
};

function showState(name) {
  Object.entries(states).forEach(([key, el]) => { el.hidden = key !== name; });
  panel.setAttribute("aria-busy", name === "loading" ? "true" : "false");
}

function categoryKey(category, needsMoreInfo) {
  if (needsMoreInfo) return "unknown";
  const c = (category || "").toLowerCase();
  if (c.includes("organic")) return "organic";
  if (c.includes("recycl")) return "recyclable";
  if (c.includes("hazard")) return "hazardous";
  if (c.includes("e-waste")) return "ewaste";
  if (c.includes("general")) return "general";
  return "unknown";
}

// All server text goes in with textContent, never innerHTML, so it cannot inject markup.
function setText(id, value) {
  document.getElementById(id).textContent = value || "";
}

function showResult(data) {
  const key = categoryKey(data.category, data.needs_more_info);
  const resultEl = states.result;
  resultEl.dataset.cat = key;

  setText("r-item", data.item);
  setText("r-category", data.category);
  setText("r-action", data.action);
  setText("r-tip", data.tip);
  setText("r-explanation", data.explanation);
  setText("r-uncertainty", data.uncertainty);

  const banner = document.getElementById("demo-banner");
  if (data.mode === "demo") {
    setText("demo-title", data.mode_label || "Demo Mode \u2013 AI service unavailable");
    setText("demo-detail", data.notice);
    banner.hidden = false;
    setText("source-line", "Source: built-in demo dataset (keyword matching, not an AI model).");
  } else {
    banner.hidden = true;
    setText("source-line", data.model ? "Analyzed by AI model: " + data.model : "Analyzed by an AI model.");
  }

  const linkWrap = document.getElementById("cat-link-wrap");
  if (key === "unknown") {
    linkWrap.hidden = true;
  } else {
    document.getElementById("cat-link").href = "categories.html#" + key;
    linkWrap.hidden = false;
  }

  showState("result");
  panel.scrollIntoView({ block: "nearest", behavior: window.matchMedia("(prefers-reduced-motion: reduce)").matches ? "auto" : "smooth" });
}

function showError(message) {
  setText("error-message", message);
  showState("error");
}

function setInputError(message) {
  inputError.textContent = message || "";
  inputError.hidden = !message;
  input.setAttribute("aria-invalid", message ? "true" : "false");
}

async function analyze(waste) {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), REQUEST_TIMEOUT_MS);
  try {
    const response = await fetch(ANALYZE_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ waste: waste }),
      signal: controller.signal,
    });
    let data = null;
    try { data = await response.json(); } catch (_) { /* handled below */ }

    if (!response.ok || !data || data.success !== true) {
      showError((data && data.error) || "The server sent an unexpected response. Please try again.");
      return;
    }
    showResult(data);
  } catch (err) {
    if (err.name === "AbortError") {
      showError("The request took too long. Please try again in a moment.");
    } else {
      showError("Can't reach the EcoSort AI backend. Start it with \"python app.py\" in the backend folder, then try again.");
    }
  } finally {
    clearTimeout(timer);
  }
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  const waste = input.value.trim();
  if (!waste) {
    setInputError("Please enter the waste item you want to dispose of.");
    input.focus();
    return;
  }
  setInputError("");
  button.disabled = true;
  button.textContent = "Analyzing\u2026";
  showState("loading");
  try {
    await analyze(waste);
  } finally {
    button.disabled = false;
    button.textContent = "Analyze Waste";
  }
});

input.addEventListener("input", () => setInputError(""));

document.querySelectorAll(".chip").forEach((chip) => {
  chip.addEventListener("click", () => {
    input.value = chip.dataset.example;
    setInputError("");
    form.requestSubmit();
  });
});
