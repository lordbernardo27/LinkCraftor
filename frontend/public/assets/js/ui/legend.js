// assets/js/sidebar/legend.js
// Renders the Legend panel list into #legendPanel.
// Safe to call multiple times. Falls back to creating the container if missing.

export function mountLegend(containerId = "legendPanel") {
  let host = document.getElementById(containerId);

  // Fallback: create the card + container if HTML wasn't updated yet
  if (!host) {
    let card = document.getElementById("legendCard");
    if (!card) {
      card = document.createElement("div");
      card.className = "card";
      card.id = "legendCard";
      const h3 = document.createElement("h3");
      h3.textContent = "Legend";
      card.appendChild(h3);

      // Try to append to the right sidebar; otherwise append to body
      const right = document.querySelector("aside.right") || document.body;
      right.appendChild(card);
    }
    host = document.createElement("div");
    host.id = containerId;
    card.appendChild(host);
  }

  host.setAttribute("role", "region");
  host.setAttribute("aria-label", "Highlight legend");
  host.innerHTML = `
    <ul class="legend">
      <li>
        <span class="dot" style="background:var(--kw-strong-br);"></span>
        Engine — <strong>Internal (Strong)</strong> (high confidence)
      </li>
      <li>
        <span class="dot" style="background:var(--kw-opt-br);"></span>
        Engine — <strong>Semantic (Optional)</strong> (review first)
      </li>
      <li>
        <span class="dot" style="background:var(--kw-ex-br);"></span>
        Engine — <strong>External</strong> (green)
      </li>
      <li>
        <span class="dot" style="background:#94a3b8;"></span>
        Applied Link (underlined)
      </li>
      <li>
        <span class="dot" style="background:var(--kw-strong-br);"></span>
        Bucket — <strong>Internal (Strong)</strong>
      </li>
      <li>
        <span class="dot" style="background:var(--kw-opt-br);"></span>
        Bucket — <strong>Semantic (Optional)</strong>
      </li>
      <li>
        <span class="dot" style="background:var(--kw-ex-br);"></span>
        Bucket — <strong>External</strong>
      </li>
    </ul>
  `;
}

// Auto-mount on module load
mountLegend();
