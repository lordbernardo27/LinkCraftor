// ===== Mobile menu =====
const hamb = document.getElementById('hamburger');
const menu = document.getElementById('mobilemenu');

hamb?.addEventListener('click', () => {
  const open = menu.style.display === 'block';
  menu.style.display = open ? 'none' : 'block';
  hamb.setAttribute('aria-expanded', String(!open));
});

document.querySelectorAll('#mobilemenu a').forEach(a => {
  a.addEventListener('click', () => {
    menu.style.display = 'none';
    hamb.setAttribute('aria-expanded', 'false');
  });
});

// ===== Resources mega dropdown =====
const resourcesBtn = document.getElementById('resourcesBtn');
const resourcesMega = document.getElementById('resourcesMega');

function closeMega(){
  if (!resourcesMega || !resourcesBtn) return;
  resourcesMega.classList.remove('open');
  resourcesBtn.setAttribute('aria-expanded', 'false');
}

function toggleMega(){
  if (!resourcesMega || !resourcesBtn) return;
  const isOpen = resourcesMega.classList.contains('open');
  if (isOpen) closeMega();
  else {
    resourcesMega.classList.add('open');
    resourcesBtn.setAttribute('aria-expanded', 'true');
  }
}

resourcesBtn?.addEventListener('click', (e) => {
  e.preventDefault();
  e.stopPropagation();
  toggleMega();
});

// Close when clicking outside
document.addEventListener('click', () => closeMega());

// Close on ESC
document.addEventListener('keydown', (e) => {
  if (e.key === 'Escape') closeMega();
});

// ===== Sticky CTA show-on-scroll =====
const sticky = document.getElementById('stickyCta');
const closeBtn = document.getElementById('ctaClose');
const STORAGE_KEY = "lc_hide_sticky_cta_v1";

function maybeShowSticky(){
  if (!sticky) return;
  const hidden = localStorage.getItem(STORAGE_KEY) === "1";
  if (hidden) return;

  const y = window.scrollY || document.documentElement.scrollTop;
  sticky.style.display = y > 520 ? 'block' : 'none';
}

window.addEventListener('scroll', maybeShowSticky, { passive:true });
window.addEventListener('load', maybeShowSticky);

closeBtn?.addEventListener('click', () => {
  localStorage.setItem(STORAGE_KEY, "1");
  sticky.style.display = 'none';
});

// ===== Editor mock: click marks to populate sidebar (Accept/Reject) =====
const marks = Array.from(document.querySelectorAll('.mark'));
const anchorEl = document.getElementById('anchorText');
const typeEl = document.getElementById('typeText');
const scoreEl = document.getElementById('scoreText');
const reasonEl = document.getElementById('reasonText');
const titleEl = document.getElementById('titleText');
const urlInput = document.getElementById('urlInput');
const kindLabel = document.getElementById('kindLabel');

const DATA = {
  internal: {
    score: 92,
    title: "Internal Linking Guide",
    reason: "Matches site structure + strengthens topical cluster.",
    url: "https://example.com/internal-linking-guide"
  },
  semantic: {
    score: 88,
    title: "Entity SEO & Semantic Relevance",
    reason: "Concept-level match improves topical authority.",
    url: "https://example.com/entity-seo"
  },
  external: {
    score: 84,
    title: "Authority Reference (Trusted Source)",
    reason: "Adds credibility and supports factual claims.",
    url: "https://example.com/authority-source"
  }
};

function setActive(mark){
  marks.forEach(m => m.classList.remove('active'));
  mark.classList.add('active');

  const kind = mark.getAttribute('data-kind');
  const phrase = mark.getAttribute('data-phrase') || mark.textContent.trim();
  const d = DATA[kind] || { score:"—", title:"—", reason:"—", url:"" };

  if (anchorEl) anchorEl.textContent = phrase;
  if (typeEl) typeEl.textContent = String(kind || "—").toUpperCase();
  if (scoreEl) scoreEl.textContent = String(d.score);
  if (reasonEl) reasonEl.textContent = d.reason;
  if (titleEl) titleEl.textContent = d.title;
  if (urlInput) urlInput.value = d.url;
  if (kindLabel) kindLabel.textContent = String(kind || "—").toUpperCase();
}

marks.forEach(m => m.addEventListener('click', () => setActive(m)));

document.getElementById('acceptBtn')?.addEventListener('click', () => {
  const active = document.querySelector('.mark.active');
  if (!active) return;
  if (!active.textContent.includes("✓")) active.textContent = active.textContent + " ✓";
  active.classList.remove('active');
  if (kindLabel) kindLabel.textContent = "Accepted";
});

document.getElementById('rejectBtn')?.addEventListener('click', () => {
  const active = document.querySelector('.mark.active');
  if (!active) return;
  active.style.opacity = "0.5";
  active.classList.remove('active');
  if (kindLabel) kindLabel.textContent = "Rejected";
});

// Auto-select first mark on load
window.addEventListener('load', () => {
  if (marks[0]) setActive(marks[0]);
});
