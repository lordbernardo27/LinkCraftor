// assets/js/features/external_helix.js
// Fully updated: backend-first resolver (GET), optional provider fallback, no cleanOriginal bug.

(function (global) {
  console.log("[ExternalRefs] external_helix.js loaded");

  // --------------------------------------------
  // CONFIG
  // --------------------------------------------
  const API_BASE = (global.LINKCRAFTOR_API_BASE || "").replace(/\/+$/,"");
  const BACKEND_RESOLVE_URL = (API_BASE ? API_BASE : "") + "/api/external/resolve";

  // If true: when backend returns no match, DO NOT fall back to provider search URLs.
  // If false: backend no match -> fallback providers (search URLs).
  const DISABLE_PROVIDER_FALLBACK = true;

  // --------------------------------------------
  // BACKEND RESOLVER (GET)
  // --------------------------------------------
  async function resolveFromBackend(phrase, lang) {
    const q = String(phrase || "").trim();
    if (!q) return [];

    const langParam = (lang || "en").toLowerCase();

    const url =
      BACKEND_RESOLVE_URL +
      "?phrase=" + encodeURIComponent(q) +
      "&lang=" + encodeURIComponent(langParam);

    try {
      const res = await fetch(url, {
        method: "GET",
        headers: { "Accept": "application/json" }
      });

      if (!res.ok) {
        console.warn("[ExternalRefs] Backend resolver HTTP error:", res.status, res.statusText);
        return [];
      }

      const data = await res.json();

      // Backend may return either:
      //  1) [] or [ { url, title, score, source, providerId?, providerLabel? ... } ]
      //  2) { results: [...] } (legacy)
      const results = Array.isArray(data)
        ? data
        : (Array.isArray(data.results) ? data.results : []);

      if (!results.length) {
        console.log(
          "[ExternalRefs] Backend resolver: no match for",
          `"${q}"`,
          DISABLE_PROVIDER_FALLBACK
            ? "– providers disabled → NO external linking"
            : "– will fall back to providers"
        );
        return [];
      }

      return results
        .filter(r => r && r.url)
        .map(r => ({
          providerId: r.providerId || r.id || "backend",
          providerLabel: r.providerLabel || r.label || r.source || "External Source",
          url: r.url,
          score: typeof r.score === "number" ? r.score : 1.0,
          phrase: q,
          title: r.title || q,
          source: r.source || "backend"
        }));
    } catch (err) {
      console.warn("[ExternalRefs] Backend resolver failed; will fall back to static search URLs.", err);
      return [];
    }
  }

  // --------------------------------------------
  // SEMANTIC NORMALIZATION (lightweight)
  // --------------------------------------------
  const CANONICAL_PHRASES = {
    // Medical examples
    "hypertension": [
      "high blood pressure",
      "elevated blood pressure",
      "raised blood pressure",
      "bp is high",
      "bp high",
      "high bp"
    ],
    "type 2 diabetes": [
      "type ii diabetes",
      "adult-onset diabetes",
      "t2dm",
      "type 2 sugar disease",
      "type 2 diabetes mellitus"
    ],
    "pregnancy due date": [
      "calculate due date",
      "edd calculator",
      "estimated due date",
      "due date calculator",
      "due date from lmp"
    ],
    "ovulation": [
      "ovulation day",
      "fertile window",
      "fertile days",
      "when do i ovulate",
      "calculate ovulation"
    ],

    // Generic examples
    "personal budget": [
      "household budget",
      "family budget",
      "managing monthly expenses",
      "budgeting for a family"
    ],
    "weight loss": [
      "lose weight",
      "fat loss",
      "burn body fat",
      "reduce body fat"
    ],
    "acne": [
      "pimples",
      "breakouts",
      "face pimples",
      "acne breakouts"
    ]
  };

  const PHRASE_TO_CANONICAL = (function () {
    const map = new Map();
    Object.entries(CANONICAL_PHRASES).forEach(function ([canonical, synonyms]) {
      const key = String(canonical || "").trim().toLowerCase();
      if (key) map.set(key, canonical);
      (synonyms || []).forEach(function (s) {
        const sk = String(s || "").trim().toLowerCase();
        if (sk) map.set(sk, canonical);
      });
    });
    return map;
  })();

  function normalizeExternalSearchPhrase(raw) {
    const text = String(raw || "").trim().toLowerCase();
    if (!text) return "";

    if (PHRASE_TO_CANONICAL.has(text)) return PHRASE_TO_CANONICAL.get(text);

    const squeezed = text.replace(/\s+/g, " ");
    if (PHRASE_TO_CANONICAL.has(squeezed)) return PHRASE_TO_CANONICAL.get(squeezed);

    return String(raw || "").trim();
  }

  // --------------------------------------------
  // PROVIDERS (fallback search URLs)
  // --------------------------------------------
  const EXTERNAL_PROVIDERS = [
    // 1. General knowledge
    {
      id: "wikipedia",
      label: "Wikipedia",
      category: "core",
      weight: 1.0,
      buildUrl(phrase, lang) {
        const langCode = (lang || "en").toLowerCase().slice(0, 2);
        return `https://${langCode}.wikipedia.org/w/index.php?search=${encodeURIComponent(phrase)}`;
      }
    },

    // 2–9. Core medical info
    {
      id: "medlineplus",
      label: "MedlinePlus",
      category: "medical",
      weight: 1.35,
      buildUrl(phrase) {
        return `https://medlineplus.gov/search/?query=${encodeURIComponent(phrase)}`;
      }
    },
    {
      id: "nih",
      label: "NIH",
      category: "medical",
      weight: 1.2,
      buildUrl(phrase) {
        return `https://search.nih.gov/search?utf8=%E2%9C%93&query=${encodeURIComponent(phrase)}`;
      }
    },
    {
      id: "cdc",
      label: "CDC",
      category: "medical",
      weight: 1.3,
      buildUrl(phrase) {
        return `https://search.cdc.gov/search/?query=${encodeURIComponent(phrase)}`;
      }
    },
    {
      id: "who",
      label: "WHO",
      category: "medical",
      weight: 1.25,
      buildUrl(phrase) {
        return `https://www.who.int/search?page=1&indexCatalogue=genericsearchindex&searchQuery=${encodeURIComponent(phrase)}`;
      }
    },
    {
      id: "mayo",
      label: "Mayo Clinic",
      category: "medical",
      weight: 1.3,
      buildUrl(phrase) {
        return `https://www.mayoclinic.org/search/search-results?q=${encodeURIComponent(phrase)}`;
      }
    },
    {
      id: "clevelandclinic",
      label: "Cleveland Clinic",
      category: "medical",
      weight: 1.15,
      buildUrl(phrase) {
        return `https://my.clevelandclinic.org/search#q=${encodeURIComponent(phrase)}`;
      }
    },
    {
      id: "nhs",
      label: "NHS UK",
      category: "medical",
      weight: 1.2,
      buildUrl(phrase) {
        return `https://www.nhs.uk/search?collection=nhs-meta&query=${encodeURIComponent(phrase)}`;
      }
    },
    {
      id: "healthline",
      label: "Healthline",
      category: "medical",
      weight: 1.0,
      buildUrl(phrase) {
        return `https://www.healthline.com/search?q1=${encodeURIComponent(phrase)}`;
      }
    },

    // 10–13. Drugs / pharmacology
    {
      id: "drugs",
      label: "Drugs.com",
      category: "drug",
      weight: 1.35,
      buildUrl(phrase) {
        return `https://www.drugs.com/search.php?searchterm=${encodeURIComponent(phrase)}`;
      }
    },
    {
      id: "rxlist",
      label: "RxList",
      category: "drug",
      weight: 1.25,
      buildUrl(phrase) {
        return `https://www.rxlist.com/search/search_results/default.aspx?query=${encodeURIComponent(phrase)}`;
      }
    },
    {
      id: "webmd",
      label: "WebMD",
      category: "drug",
      weight: 1.1,
      buildUrl(phrase) {
        return `https://www.webmd.com/search/search_results/default.aspx?query=${encodeURIComponent(phrase)}`;
      }
    },
    {
      id: "pharmgkb",
      label: "PharmGKB",
      category: "drug",
      weight: 1.0,
      buildUrl(phrase) {
        return `https://www.pharmgkb.org/search?query=${encodeURIComponent(phrase)}`;
      }
    },

    // 14–18. Evidence / guidelines / pregnancy-focused
    {
      id: "pubmed",
      label: "PubMed",
      category: "evidence",
      weight: 1.4,
      buildUrl(phrase) {
        return `https://pubmed.ncbi.nlm.nih.gov/?term=${encodeURIComponent(phrase)}`;
      }
    },
    {
      id: "cochrane",
      label: "Cochrane Library",
      category: "evidence",
      weight: 1.3,
      buildUrl(phrase) {
        return `https://www.cochranelibrary.com/search?q=${encodeURIComponent(phrase)}`;
      }
    },
    {
      id: "nice",
      label: "NICE Guidelines",
      category: "guideline",
      weight: 1.25,
      buildUrl(phrase) {
        return `https://www.nice.org.uk/search?q=${encodeURIComponent(phrase)}`;
      }
    },
    {
      id: "acog",
      label: "ACOG",
      category: "pregnancy",
      weight: 1.5,
      buildUrl(phrase) {
        return `https://www.acog.org/search#q=${encodeURIComponent(phrase)}`;
      }
    },
    {
      id: "who_reproductive",
      label: "WHO Reproductive Health",
      category: "pregnancy",
      weight: 1.35,
      buildUrl(phrase) {
        return `https://www.who.int/health-topics/sexual-and-reproductive-health#tab=tab_3&search=${encodeURIComponent(phrase)}`;
      }
    },

    // 19–20. Pediatrics / child / fertility
    {
      id: "unicef",
      label: "UNICEF",
      category: "child",
      weight: 1.1,
      buildUrl(phrase) {
        return `https://www.unicef.org/search?keyword=${encodeURIComponent(phrase)}`;
      }
    },
    {
      id: "stanford_childrens",
      label: "Stanford Children’s",
      category: "child",
      weight: 1.2,
      buildUrl(phrase) {
        return `https://www.stanfordchildrens.org/en/search?q=${encodeURIComponent(phrase)}`;
      }
    },

    // 21–24. General high-quality hospital / info
    {
      id: "hopkins",
      label: "Johns Hopkins Medicine",
      category: "medical",
      weight: 1.25,
      buildUrl(phrase) {
        return `https://www.hopkinsmedicine.org/search?q=${encodeURIComponent(phrase)}`;
      }
    },
    {
      id: "mount_sinai",
      label: "Mount Sinai",
      category: "medical",
      weight: 1.15,
      buildUrl(phrase) {
        return `https://www.mountsinai.org/search?q=${encodeURIComponent(phrase)}`;
      }
    },
    {
      id: "cleveland_obgyn",
      label: "Cleveland Clinic OBGYN",
      category: "pregnancy",
      weight: 1.35,
      buildUrl(phrase) {
        return `https://health.clevelandclinic.org/?s=${encodeURIComponent(phrase)}`;
      }
    },
    {
      id: "who_maternal",
      label: "WHO Maternal Health",
      category: "pregnancy",
      weight: 1.4,
      buildUrl(phrase) {
        return `https://www.who.int/search?indexCatalogue=genericsearchindex&searchQuery=${encodeURIComponent(phrase + " pregnancy")}`;
      }
    }
  ];

  // --------------------------------------------
  // SCORING
  // --------------------------------------------
  function normalizePhrase(raw) {
    return String(raw || "").trim().toLowerCase();
  }

  function defaultScoreExternalProvider(phrase, provider) {
    const p = normalizePhrase(phrase);
    let score = provider.weight || 1;

    const isPregnancy =
      p.includes("pregnancy") ||
      p.includes("pregnant") ||
      p.includes("ovulation") ||
      p.includes("fertile") ||
      p.includes("due date") ||
      p.includes("conception");

    const isDrug =
      p.includes("mg") ||
      p.includes("tablet") ||
      p.includes("capsule") ||
      p.includes("dose") ||
      p.includes("dosage") ||
      p.includes("side effect") ||
      p.includes("side effects") ||
      p.includes("interaction") ||
      p.includes("drug") ||
      p.includes("medicine");

    const isChild =
      p.includes("baby") ||
      p.includes("newborn") ||
      p.includes("child") ||
      p.includes("toddler") ||
      p.includes("infant");

    if (isPregnancy) {
      if (provider.category === "pregnancy") score += 0.7;
      if (provider.id === "acog") score += 0.8;
      if (provider.id === "who_maternal") score += 0.6;
    }

    if (isDrug) {
      if (provider.category === "drug") score += 0.7;
      if (provider.id === "drugs") score += 0.6;
      if (provider.id === "rxlist") score += 0.5;
      if (provider.id === "pubmed") score += 0.3;
    }

    if (isChild) {
      if (provider.category === "child") score += 0.7;
      if (provider.id === "unicef") score += 0.4;
      if (provider.id === "stanford_childrens") score += 0.5;
    }

    if (provider.category === "evidence" || provider.category === "guideline") {
      score += 0.2;
    }

    return score;
  }

  function scoreProvider(phrase, provider) {
    const base = provider.weight || 1;
    const scoring = global.LinkcraftorScoring;

    if (scoring && typeof scoring.scoreExternalProvider === "function") {
      try {
        return scoring.scoreExternalProvider(phrase, provider.id, base);
      } catch (err) {
        console.warn("[ExternalRefs] scoreExternalProvider error, falling back", err);
      }
    }

    return defaultScoreExternalProvider(phrase, provider);
  }

  // --------------------------------------------
  // PUBLIC API
  // --------------------------------------------
  async function getExternalReferences(phrase, opts) {
    const options = opts || {};
    const limit = options.limit || 10;
    const lang  = options.lang  || "en";

    const cleanOriginal = String(phrase || "").trim();
    if (!cleanOriginal) return [];

    // For fallback providers, use semantic normalized phrase
    const searchPhrase = normalizeExternalSearchPhrase(cleanOriginal) || cleanOriginal;

    let finalCandidates = [];

    // STEP 1: backend-first
    try {
      const backendCandidates = await resolveFromBackend(cleanOriginal, lang);

      if (Array.isArray(backendCandidates) && backendCandidates.length) {
        console.log(
          "[ExternalRefs] Backend resolver returned",
          backendCandidates.length,
          "candidate(s) for:",
          `"${cleanOriginal}"`
        );

        finalCandidates = backendCandidates.map((m) => ({
          providerId:    m.providerId    || "backend",
          providerLabel: m.providerLabel || m.source || "Backend",
          url:           m.url,
          score:         m.score != null ? m.score : 1,
          phrase:        m.phrase || cleanOriginal,
          title:         m.title  || cleanOriginal,
          source:        m.source || "backend"
        }));
      } else {
        console.log(
          "[ExternalRefs] Backend resolver: no match for",
          `"${cleanOriginal}"`,
          DISABLE_PROVIDER_FALLBACK ? "– providers disabled → NO external linking" : "– will fall back to providers"
        );
      }
    } catch (err) {
      console.warn("[ExternalRefs] Error using backend resolver:", err);
    }

    // STEP 2: fallback providers (optional)
    if (!finalCandidates.length) {
      if (DISABLE_PROVIDER_FALLBACK) {
        console.log("[ExternalRefs] No backend match → NO external linking (providers disabled)");
        return [];
      }

      finalCandidates = EXTERNAL_PROVIDERS.map(function (provider) {
        const url = provider.buildUrl(searchPhrase, lang);
        const score = scoreProvider(searchPhrase, provider);

        return {
          providerId: provider.id,
          providerLabel: provider.label,
          url,
          score,
          phrase: cleanOriginal,
          title: cleanOriginal,
          source: "fallback_providers"
        };
      });
    }

    // STEP 3: sort + limit
    finalCandidates.sort(function (a, b) {
      return (b.score || 0) - (a.score || 0);
    });

    return limit > 0 ? finalCandidates.slice(0, limit) : finalCandidates;
  }

  // Expose stable hook
  global.LinkcraftorExternalRefs = {
    getExternalReferences,
    providers: EXTERNAL_PROVIDERS.slice()
  };

  console.log(
    "[ExternalRefs] LinkcraftorExternalRefs is ready with",
    EXTERNAL_PROVIDERS.length,
    "providers"
  );
})(window);
