// assets/js/engine/context-hooks.js
// Optional advanced context + entity/graph hooks for LinkCraftor engine.
// Pure functions, hooked via window.* so app.js can call them safely.

(function(){
  const norm = (s) => String(s || "").toLowerCase().trim();

  // Small helper: find nearest section heading around the phrase.
  // This assumes you have one main viewer element with id="viewer" (or adjust).
  function detectSectionTypeFromDom(phraseText) {
    if (typeof document === "undefined") return null;
    const viewer = document.getElementById("viewer");
    if (!viewer) return null;

    // Very cheap heuristic: look at nearest heading above current selection
    // In future you can wire exact offsets/section ids into PhraseContext.position.
    const sel = window.getSelection && window.getSelection();
    if (!sel || sel.rangeCount === 0) return null;

    const range = sel.getRangeAt(0);
    let node = range.startContainer;
    if (!viewer.contains(node)) return null;

    // Walk up to viewer, remember the last heading
    let lastHeading = null;
    while (node && node !== viewer) {
      if (/^H[1-6]$/i.test(node.nodeName)) {
        lastHeading = node;
        break;
      }
      node = node.parentNode;
    }

    if (!lastHeading) return null;

    const text = norm(lastHeading.textContent || "");
    if (!text) return null;

    if (text.includes("side effect") || text.includes("adverse")) return "BODY";
    if (text.includes("overview") || text.includes("introduction")) return "INTRO";
    if (text.includes("faq") || text.includes("questions")) return "FAQ";
    if (text.includes("conclusion") || text.includes("summary")) return "CONCLUSION";

    return "BODY";
  }

  // Guess high-level contextType from local sentence around the phrase.
  function detectContextTypeFromText(phraseText, ctx) {
    const snippet = norm(ctx.contextText || "");
    const txt     = snippet || norm(phraseText);

    if (!txt) return null;

    if (txt.includes("side effect") ||
        txt.includes("adverse") ||
        txt.includes("risk")) {
      return "SIDE_EFFECTS";
    }

    if (txt.includes("treat") ||
        txt.includes("management") ||
        txt.includes("therapy")) {
      return "TREATMENT";
    }

    if (txt.includes("pregnancy") ||
        txt.includes("pregnant") ||
        txt.includes("breastfeeding")) {
      return "PREGNANCY";
    }

    if (txt.includes("what is") ||
        txt.includes("definition") ||
        txt.includes("overview")) {
      return "OVERVIEW";
    }

    return "GENERAL";
  }

  // Guess intent: WARNING / RECOMMENDATION / COMPARISON / ACTIONABLE
  function detectIntent(phraseText, ctx) {
    const txt = norm(ctx.contextText || phraseText || "");

    if (!txt) return null;

    if (txt.includes("do not") ||
        txt.includes("avoid") ||
        txt.includes("warning") ||
        txt.includes("danger")) {
      return "WARNING";
    }

    if (txt.includes("recommended") ||
        txt.includes("we suggest") ||
        txt.includes("it is best to")) {
      return "RECOMMENDATION";
    }

    if (txt.includes("vs") ||
        txt.includes("versus") ||
        txt.includes("compared to")) {
      return "COMPARISON";
    }

    if (txt.includes("step") ||
        txt.includes("checklist") ||
        txt.includes("how to")) {
      return "ACTIONABLE";
    }

    return null;
  }

  // Guess discourse role for Q&A-like content.
  function detectDiscourseRole(phraseText, ctx) {
    const txt = norm(ctx.contextText || phraseText || "");

    if (!txt) return null;

    if (txt.endsWith("?") ||
        txt.startsWith("what ") ||
        txt.startsWith("why ") ||
        txt.startsWith("how ") ||
        txt.startsWith("when ") ||
        txt.startsWith("can ")) {
      return "QUESTION";
    }

    if (txt.startsWith("yes, ") ||
        txt.startsWith("no, ")  ||
        txt.startsWith("in summary") ||
        txt.startsWith("the short answer")) {
      return "ANSWER";
    }

    if (txt.includes("if you") && txt.includes("then")) {
      return "CONDITION";
    }

    if (txt.includes("you should") ||
        txt.includes("we advise")) {
      return "RECOMMENDATION";
    }

    return null;
  }

  /**
   * Hook: LC_getPhraseContext
   *
   * Called from buildPhraseContext(phraseText) in app.js.
   * It receives the phrase and the partially-built ctx (with docId, etc.)
   * and returns extra fields: contextType, sectionType, intent, discourseRole, etc.
   */
  function LC_getPhraseContext(phraseText, ctxBase) {
    const ctx = ctxBase || {};

    // You can fill ctx.contextText from your own sentence/section extractor.
    // For now, we leave it as-is and only derive labels.
    const sectionType   = ctx.sectionType   || detectSectionTypeFromDom(phraseText);
    const contextType   = ctx.contextType   || detectContextTypeFromText(phraseText, ctx);
    const intent        = ctx.intent        || detectIntent(phraseText, ctx);
    const discourseRole = ctx.discourseRole || detectDiscourseRole(phraseText, ctx);

    return {
      sectionType,
      contextType,
      intent,
      discourseRole,
      // entities, graphVector, graphRelations can be injected by your entity engine later
      entities:       ctx.entities       || [],
      graphVector:    ctx.graphVector    || null,
      graphRelations: ctx.graphRelations || []
    };
  }

  /**
   * Optional hook: LC_enrichCandidate
   *
   * Given a CandidateTarget built in app.js, you can attach advanced info:
   *   - entities
   *   - topicTypes / sectionRoles / intentTags / discourseTags
   *   - graphVector / graphRelations
   *
   * For now this is a no-op passthrough; you can extend later to pull data
   * from your Entity Map / Graph.
   */
  function LC_enrichCandidate(candidate) {
    // Example scaffold (all optional):
    const out = { ...candidate };

    // If you have a global entity map keyed by topicId, you could do:
    // const meta = window.LC_TOPIC_META && window.LC_TOPIC_META[out.id];
    // if (meta) {
    //   out.entities       = meta.entities || out.entities || [];
    //   out.topicTypes     = meta.topicTypes || out.topicTypes || [];
    //   out.sectionRoles   = meta.sectionRoles || out.sectionRoles || [];
    //   out.intentTags     = meta.intentTags || out.intentTags || [];
    //   out.discourseTags  = meta.discourseTags || out.discourseTags || [];
    //   out.graphVector    = meta.graphVector || out.graphVector || null;
    //   out.graphRelations = meta.graphRelations || out.graphRelations || [];
    // }

    return out;
  }

  // Expose hooks to the rest of the engine
  if (typeof window !== "undefined") {
    window.LC_getPhraseContext = LC_getPhraseContext;
    window.LC_enrichCandidate  = LC_enrichCandidate;
  }
})();
