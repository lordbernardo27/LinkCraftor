// public/assets/js/features/upload.js
// Minimal, client-only upload wiring so the named export exists and buttons respond.
// This reads .txt/.md/.html/.htm locally and renders into #doc-content.
// .docx needs a backend; we show a toast for now.

import { $, showToast, escapeHtml } from "../core/dom.js";

// Utility: set the file input accept attr and open picker
function setAcceptAndOpen(acceptList) {
  const input = $("#file");
  if (!input) return;
  input.setAttribute("accept", acceptList || ".docx,.md,.html,.htm,.txt");
  input.click();
}

/**
 * SECURITY: Never inject untrusted HTML into innerHTML.
 * We render HTML files as a safe preview (escaped), so no scripts/events run.
 * This is fast and eliminates XSS risk.
 */
function renderIntoEditor({ html = "", text = "", filename = "" }) {
  const viewer = $("#doc-content");
  if (!viewer) return;

  // Clear existing content safely
  viewer.textContent = "";

  if (html && html.trim()) {
    // Render HTML as escaped code preview (safe)
    const pre = document.createElement("pre");
    pre.style.whiteSpace = "pre-wrap";
    pre.style.lineHeight = "1.6";
    pre.textContent = html; // SAFE: treated as text, not executed
    viewer.appendChild(pre);
  } else {
    const safeText = String(text || "");
    const parts = safeText.replace(/\r\n/g, "\n").split(/\n{2,}/);

    // Build DOM without innerHTML (faster + safer)
    if (parts.length) {
      for (const p of parts) {
        const para = document.createElement("p");
        // preserve single newlines
        const lines = p.split("\n");
        for (let i = 0; i < lines.length; i++) {
          if (i) para.appendChild(document.createElement("br"));
          para.appendChild(document.createTextNode(lines[i]));
        }
        viewer.appendChild(para);
      }
    } else {
      const pre = document.createElement("pre");
      pre.style.whiteSpace = "pre-wrap";
      pre.style.lineHeight = "1.6";
      pre.textContent = safeText;
      viewer.appendChild(pre);
    }
  }

  // Top meta labels (purely cosmetic here)
  const topMeta = $("#topMeta");
  if (topMeta) topMeta.textContent = `File: ${filename || "Untitled"} | Code: ----`;
  const docMeta = $("#docMeta");
  if (docMeta) docMeta.textContent = `Loaded: ${filename || "Untitled"} | Code: ----`;
  const countMeta = $("#docCountMeta");
  if (countMeta) countMeta.textContent = "Doc 1 of 1";
}

// Basic file readers
async function readTextFile(file) {
  const text = await file.text();
  return { text, html: "", filename: file.name };
}
async function readHtmlFile(file) {
  const html = await file.text();
  return { text: "", html, filename: file.name };
}

export function wireUpload() {
  const btnUploadMain = $("#btnUploadMain");
  const btnUploadMenu = $("#btnUploadMenu");
  const uploadMenu    = $("#uploadMenu");
  const fileInput     = $("#file");
  const errorBox      = $("#error");

  if (!btnUploadMain || !btnUploadMenu || !uploadMenu || !fileInput) {
    console.warn("[upload] controls not found — skipping wiring");
    return;
  }

  // keep menu accept choice
  let currentAccept = ".docx,.md,.html,.htm,.txt";

  // Main button opens picker with current accept
  btnUploadMain.addEventListener("click", () => setAcceptAndOpen(currentAccept));

  // Toggle the dropdown
  btnUploadMenu.addEventListener("click", (e) => {
    e.stopPropagation();
    const open = uploadMenu.classList.contains("open");
    uploadMenu.classList.toggle("open", !open);
    btnUploadMenu.setAttribute("aria-expanded", String(!open));
  });

  // Choose a filter and open picker immediately
  uploadMenu.querySelectorAll("button").forEach((b) => {
    b.addEventListener("click", (e) => {
      e.stopPropagation();
      const opt = b.getAttribute("data-accept") || "";
      const map = {
        "": ".docx,.md,.html,.htm,.txt",
        ".docx": ".docx",
        ".md": ".md",
        ".html,.htm": ".html,.htm",
        ".txt": ".txt",
      };
      currentAccept = map[opt] || ".docx,.md,.html,.htm,.txt";
      uploadMenu.classList.remove("open");
      btnUploadMenu.setAttribute("aria-expanded", "false");
      setAcceptAndOpen(currentAccept);
    });
  });

  // Close menu on outside click
  document.addEventListener("click", () => {
    if (uploadMenu.classList.contains("open")) {
      uploadMenu.classList.remove("open");
      btnUploadMenu.setAttribute("aria-expanded", "false");
    }
  });

  // Handle selected file (client-only parsing)
  fileInput.addEventListener("change", async () => {
    const file = fileInput.files && fileInput.files[0];
    fileInput.value = ""; // reset for next time
    if (!file) return;

    try {
      const name = file.name || "";
      if (/\.html?$/i.test(name)) {
        const doc = await readHtmlFile(file);
        renderIntoEditor(doc);
        showToast(errorBox, `Loaded ${name} (safe preview)`, 1400);
        return;
      }
      if (/\.md$/i.test(name) || /\.txt$/i.test(name)) {
        const doc = await readTextFile(file);
        renderIntoEditor(doc);
        showToast(errorBox, `Loaded ${name}`, 1200);
        return;
      }
      if (/\.docx$/i.test(name)) {
        // Needs backend in this split build
        showToast(
          errorBox,
          "DOCX upload requires a server endpoint in this split build.",
          2200
        );
        return;
      }

      // Fallback: try as text
      const doc = await readTextFile(file);
      renderIntoEditor(doc);
      showToast(errorBox, `Loaded ${name}`, 1200);
    } catch (e) {
      showToast(errorBox, "Upload failed: " + (e?.message || e), 2200);
    }
  });
}
