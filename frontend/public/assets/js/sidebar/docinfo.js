// assets/js/sidebar/docinfo.js
// Renders the Document Info code chips into #docMeta and wires goto/remove handlers.
// Delete icon is shown on hover via CSS (.doc-remove).

/** Basic HTML escaper */
function esc(s) {
  return String(s ?? "").replace(/[&<>"']/g, (m) => ({
    "&": "&amp;",
    "<": "&lt;",
    ">": "&gt;",
    '"': "&quot;",
    "'": "&#39;",
  }[m]));
}

/** Build a short code for each doc if none is provided */
function fallbackCode(d, i) {
  if (d?.docCode && /^[A-Z0-9]{2,8}$/.test(d.docCode)) return d.docCode;
  const base = (d?.filename || `DOC${i + 1}`)
    .replace(/\.[^.]+$/, "")
    .replace(/[^\w]/g, "")
    .toUpperCase();
  return (base || "DOC").slice(0, 6);
}

/**
 * Render the #docMeta chips and wire interactions.
 * @param {Array}    docs           Array of docs (e.g., [{filename, html?, text?, docCode?}, ...])
 * @param {number}   currentIndex   Active doc index
 * @param {Function} onGoto         Called with (index) when user clicks a code chip
 * @param {Function} onRemove       Called with (index) when user clicks the hover ✕
 */
export function renderDocInfoPanel(
  docs = [],
  currentIndex = -1,
  onGoto = () => {},
  onRemove = () => {}
) {
  const host = document.getElementById("docMeta");
  if (!host) return;

  if (!Array.isArray(docs) || docs.length === 0) {
    host.textContent = "—";
    return;
  }

  // Render chips (✕ visibility handled by CSS)
  host.innerHTML = docs
    .map((d, idx) => {
      const code = fallbackCode(d, idx);
      const isActive = idx === currentIndex;
      return `
        <span class="doc-chip${isActive ? " is-active" : ""}" data-idx="${idx}">
          <span class="doc-code" data-goto="${idx}" tabindex="0" title="Go to ${esc(code)}">
            ${esc(code)}
          </span>
          <button class="doc-remove" type="button" data-remove="${idx}" aria-label="Remove ${esc(code)}" title="Remove">✕</button>
        </span>
      `;
    })
    .join("");

  // Goto handlers (click or Enter/Space)
  host.querySelectorAll(".doc-code").forEach((el) => {
    const go = () => {
      const i = parseInt(el.getAttribute("data-goto") || "0", 10) || 0;
      try {
        onGoto(i);
      } catch (err) {
        console.error("onGoto callback failed:", err);
      }
    };
    el.addEventListener("click", go);
    el.addEventListener("keydown", (e) => {
      if (e.key === "Enter" || e.key === " ") go();
    });
  });

  // Remove handlers (hover ✕) — simple callback only
  host.querySelectorAll(".doc-remove").forEach((btn) => {
    btn.addEventListener("click", (e) => {
      e.stopPropagation(); // don't trigger goto when clicking ✕
      const i = parseInt(btn.getAttribute("data-remove") || "-1", 10);
      if (i >= 0) {
        try {
          onRemove(i);
        } catch (err) {
          console.error("onRemove callback failed:", err);
        }
      }
    });
  });
}
