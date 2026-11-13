/*
Universal Runtime Owner Control Tower
Phase 1.19 — Runtime Owner Frontend Module

Responsibilities:
- Runtime Owner section navigation.
- Active-section state.
- Legacy route-to-section hints.
- Owner shell status targets.
- No runtime authority.
- No direct runtime mutation.
*/

(function () {
  "use strict";

  const RUNTIME_OWNER_SECTIONS = Object.freeze([
    "overview",
    "pipeline_operations",
    "jobs",
    "queues",
    "workers_leases",
    "orchestration",
    "execution",
    "reliability_recovery",
    "resource_governance",
    "runtime_apis",
    "persistence_state_integrity",
    "observability",
    "security",
    "owner_actions",
    "evidence_audit"
  ]);

  const LEGACY_ROUTE_SECTION_MAP = Object.freeze({
    queues: "queues",
    jobs: "jobs",
    workers: "workers_leases",
    recovery: "reliability_recovery",
    selfhealing: "reliability_recovery"
  });

  function getRuntimePage() {
    return document.getElementById("runtimePage");
  }

  function getSubnav() {
    return document.getElementById("runtimeOwnerSubnav");
  }

  function getContentPanel() {
    return document.getElementById("runtimeOwnerContentPanel");
  }

  function isValidSection(section) {
    return RUNTIME_OWNER_SECTIONS.includes(section);
  }

  function normalizeSection(section) {
    if (isValidSection(section)) {
      return section;
    }

    if (Object.prototype.hasOwnProperty.call(
      LEGACY_ROUTE_SECTION_MAP,
      section
    )) {
      return LEGACY_ROUTE_SECTION_MAP[section];
    }

    return "overview";
  }

  function setActiveSection(section) {
    const runtimePage = getRuntimePage();
    const subnav = getSubnav();
    const contentPanel = getContentPanel();

    // PART F 15-B6C-R2: the nested sidebar replaced the legacy subnav.
    // Panel switching requires the page and content panel; the legacy subnav is optional.
    if (!runtimePage || !contentPanel) {
      return false;
    }

    const normalized = normalizeSection(section);

    // Preserve legacy subnav synchronization when that optional shell exists.
    if (subnav) {
      const buttons = subnav.querySelectorAll(
        "[data-runtime-owner-section]"
      );

      buttons.forEach((button) => {
        const isActive =
          button.dataset.runtimeOwnerSection === normalized;

        button.classList.toggle("active", isActive);

        button.setAttribute(
          "aria-selected",
          isActive ? "true" : "false"
        );
      });
    }

    const panels = contentPanel.querySelectorAll(
      "[data-runtime-owner-section-panel]"
    );

    panels.forEach((panel) => {
      const isActive =
        panel.dataset.runtimeOwnerSectionPanel === normalized;

      panel.classList.toggle("active", isActive);
      panel.hidden = !isActive;
    });

    // PART F 15-B6C-R3: keep the installed Owner Actions workspace
    // synchronized with the shared Runtime Owner section authority.
    const ownerActionsWorkspace = document.getElementById(
      "runtimeOwnerActionsWorkspace"
    );

    if (ownerActionsWorkspace) {
      const ownerActionsActive = normalized === "owner_actions";
      ownerActionsWorkspace.hidden = !ownerActionsActive;
      ownerActionsWorkspace.setAttribute(
        "aria-hidden",
        ownerActionsActive ? "false" : "true"
      );
    }

    contentPanel.dataset.runtimeOwnerActiveSection = normalized;

    runtimePage.dispatchEvent(
      new CustomEvent("runtimeowner:sectionchange", {
        detail: {
          section: normalized
        }
      })
    );

    return true;
  }

  function getActiveSection() {
    const contentPanel = getContentPanel();

    if (!contentPanel) {
      return "overview";
    }

    return normalizeSection(
      contentPanel.dataset.runtimeOwnerActiveSection
    );
  }

  function setStatus(id, value) {
    const element = document.getElementById(id);

    if (!element) {
      return false;
    }

    element.textContent = String(value);
    return true;
  }

  function updateShellStatus(payload = {}) {
    if (
      Object.prototype.hasOwnProperty.call(
        payload,
        "runtimeStatus"
      )
    ) {
      setStatus(
        "runtimeOwnerStatus",
        payload.runtimeStatus
      );
    }

    if (
      Object.prototype.hasOwnProperty.call(
        payload,
        "ownerAttention"
      )
    ) {
      setStatus(
        "runtimeOwnerAttention",
        payload.ownerAttention
      );
    }

    if (
      Object.prototype.hasOwnProperty.call(
        payload,
        "architecture"
      )
    ) {
      setStatus(
        "runtimeOwnerArchitecture",
        payload.architecture
      );
    }

    if (
      Object.prototype.hasOwnProperty.call(
        payload,
        "lastRefresh"
      )
    ) {
      setStatus(
        "runtimeOwnerLastRefresh",
        payload.lastRefresh
      );
    }
  }

  function bindRuntimeOwnerNavigation() {
    const subnav = getSubnav();

    if (!subnav) {
      return false;
    }

    if (subnav.dataset.runtimeOwnerBound === "true") {
      return true;
    }

    subnav.addEventListener("click", (event) => {
      const button = event.target.closest(
        "[data-runtime-owner-section]"
      );

      if (!button) {
        return;
      }

      const section =
        button.dataset.runtimeOwnerSection;

      setActiveSection(section);
    });

    subnav.dataset.runtimeOwnerBound = "true";
    return true;
  }

  function initializeRuntimeOwner() {
    if (!getRuntimePage()) {
      return false;
    }

    bindRuntimeOwnerNavigation();

    setActiveSection(
      getActiveSection()
    );

    return true;
  }

  window.LinkCraftorRuntimeOwner = Object.freeze({
    sections: RUNTIME_OWNER_SECTIONS,
    legacyRouteSectionMap: LEGACY_ROUTE_SECTION_MAP,
    initialize: initializeRuntimeOwner,
    setActiveSection,
    getActiveSection,
    updateShellStatus
  });

  if (document.readyState === "loading") {
    document.addEventListener(
      "DOMContentLoaded",
      initializeRuntimeOwner
    );
  } else {
    initializeRuntimeOwner();
  }
})();

// BEGIN PHASE 2.19 RUNTIME OVERVIEW WIRING
(() => {
  "use strict";

  const SUMMARY_ENDPOINT =
    "/owner/api/runtime/summary";

  const byId = (id) =>
    document.getElementById(id);

  const text = (id, value) => {
    const node = byId(id);

    if (!node) {
      return;
    }

    if (
      value === null ||
      value === undefined ||
      value === ""
    ) {
      node.textContent = "?";
      return;
    }

    node.textContent = String(value);
  };

  const formatBooleanAttention = (value) => {
    if (value === true) {
      return "Required";
    }

    if (value === false) {
      return "None";
    }

    return "Unknown";
  };

  const alertCount = (alerts) => {
    if (!alerts || typeof alerts !== "object") {
      return "?";
    }

    for (const key of [
      "active",
      "count",
      "total",
      "active_count",
    ]) {
      if (
        Object.prototype.hasOwnProperty.call(
          alerts,
          key
        )
      ) {
        return alerts[key];
      }
    }

    if (Array.isArray(alerts.items)) {
      return alerts.items.length;
    }

    return "?";
  };

  const architectureVersion = (
    architecture
  ) => {
    if (!architecture) {
      return "?";
    }

    return (
      architecture.architecture_registry_version ||
      architecture.read_model_version ||
      architecture.version ||
      architecture.architecture_name ||
      "?"
    );
  };

  const updateTopStatus = (summary) => {
    const health =
      summary?.health || {};

    const architecture =
      summary?.architecture || {};

    const security =
      summary?.security_api_alert_attention || {};

    text(
      "runtimeOwnerStatus",
      health.runtime_health || "Unknown"
    );

    text(
      "runtimeOwnerAttention",
      formatBooleanAttention(
        security.owner_attention_required
      )
    );

    text(
      "runtimeOwnerArchitecture",
      architecture.architecture_name ||
        "Universal Runtime"
    );

    text(
      "runtimeOwnerLastRefresh",
      summary.generated_at || "Unknown"
    );
  };

  const updateOverview = (summary) => {
    const health =
      summary?.health || {};

    const architecture =
      summary?.architecture || {};

    const activity =
      summary?.activity || {};

    const work =
      summary?.work_state || {};

    const infrastructure =
      summary?.infrastructure || {};

    const security =
      summary?.security_api_alert_attention || {};

    text(
      "runtimeOverviewRuntimeHealth",
      health.runtime_health
    );

    text(
      "runtimeOverviewHealthReasons",
      Array.isArray(
        health.health_reasons
      ) && health.health_reasons.length
        ? health.health_reasons.join(", ")
        : "None reported"
    );

    text(
      "runtimeOverviewArchitectureVersion",
      architectureVersion(
        architecture
      )
    );

    text(
      "runtimeOverviewActiveJobs",
      activity.active_jobs
    );

    text(
      "runtimeOverviewQueuedJobs",
      activity.queued_jobs
    );

    text(
      "runtimeOverviewRunningExecutions",
      activity.running_executions
    );

    text(
      "runtimeOverviewActiveWorkers",
      activity.active_workers
    );

    text(
      "runtimeOverviewActiveLeases",
      activity.active_leases
    );

    text(
      "runtimeOverviewActiveOrchestrations",
      work.active_orchestrations
    );

    text(
      "runtimeOverviewFailedWork",
      work.failed_work
    );

    text(
      "runtimeOverviewRecoveringWork",
      work.recovering_work
    );

    text(
      "runtimeOverviewQueuePressure",
      infrastructure.queue_pressure
    );

    text(
      "runtimeOverviewResourcePressure",
      infrastructure.resource_pressure
    );

    text(
      "runtimeOverviewPersistenceHealth",
      infrastructure.persistence_health
    );

    text(
      "runtimeOverviewSecurityHealth",
      security.security_health
    );

    text(
      "runtimeOverviewApiHealth",
      security.api_health
    );

    text(
      "runtimeOverviewRuntimeAlerts",
      alertCount(
        security.runtime_alerts
      )
    );

    text(
      "runtimeOverviewOwnerAttention",
      formatBooleanAttention(
        security.owner_attention_required
      )
    );

    updateTopStatus(summary);
  };

  const clearOverview = () => {
    for (const id of [
      "runtimeOverviewRuntimeHealth",
      "runtimeOverviewHealthReasons",
      "runtimeOverviewArchitectureVersion",
      "runtimeOverviewActiveJobs",
      "runtimeOverviewQueuedJobs",
      "runtimeOverviewRunningExecutions",
      "runtimeOverviewActiveWorkers",
      "runtimeOverviewActiveLeases",
      "runtimeOverviewActiveOrchestrations",
      "runtimeOverviewFailedWork",
      "runtimeOverviewRecoveringWork",
      "runtimeOverviewQueuePressure",
      "runtimeOverviewResourcePressure",
      "runtimeOverviewPersistenceHealth",
      "runtimeOverviewSecurityHealth",
      "runtimeOverviewApiHealth",
      "runtimeOverviewRuntimeAlerts",
      "runtimeOverviewOwnerAttention",
    ]) {
      text(id, "?");
    }
  };

  const setUnavailableState = (
    message
  ) => {
    clearOverview();

    text(
      "runtimeOwnerStatus",
      "Unavailable"
    );

    text(
      "runtimeOwnerAttention",
      "Unknown"
    );

    text(
      "runtimeOwnerLastRefresh",
      "Unavailable"
    );

    const notice =
      byId("runtimeOverviewNotice");

    if (notice) {
      notice.textContent =
        message ||
        "Runtime summary is currently unavailable.";
    }
  };

  const refreshRuntimeOverview =
    async () => {

      const notice =
        byId("runtimeOverviewNotice");

      const button =
        byId("runtimeOverviewRefreshButton");

      if (button) {
        button.disabled = true;
      }

      if (notice) {
        notice.textContent =
          "Loading Runtime summary?";
      }

      try {
        const response = await fetch(
          SUMMARY_ENDPOINT,
          {
            method: "GET",
            headers: {
              Accept: "application/json",
            },
            cache: "no-store",
            credentials: "same-origin",
          }
        );

        let payload = null;

        try {
          payload = await response.json();
        } catch (_) {
          payload = null;
        }

        if (!response.ok) {
          const detail =
            payload?.detail || {};

          const message =
            detail.message ||
            `Runtime summary unavailable (${response.status}).`;

          setUnavailableState(
            message
          );

          return;
        }

        updateOverview(payload);

        if (notice) {
          notice.textContent =
            "Runtime summary loaded from the canonical read-only Runtime Owner API.";
        }
      } catch (error) {
        setUnavailableState(
          error?.message ||
          "Runtime summary request failed."
        );
      } finally {
        if (button) {
          button.disabled = false;
        }
      }
    };

  const bindRuntimeOverview = () => {
    const page =
      byId("runtimePage");

    if (!page) {
      return;
    }

    const refreshButton =
      byId("runtimeOverviewRefreshButton");

    if (refreshButton) {
      refreshButton.addEventListener(
        "click",
        refreshRuntimeOverview
      );
    }

    const overviewButton =
      page.querySelector(
        '[data-runtime-owner-section="overview"]'
      );

    if (overviewButton) {
      overviewButton.addEventListener(
        "click",
        refreshRuntimeOverview
      );
    }

    refreshRuntimeOverview();
  };

  if (
    document.readyState === "loading"
  ) {
    document.addEventListener(
      "DOMContentLoaded",
      bindRuntimeOverview,
      { once: true }
    );
  } else {
    bindRuntimeOverview();
  }

  window.RuntimeOwnerOverview =
    Object.freeze({
      endpoint:
        SUMMARY_ENDPOINT,

      refresh:
        refreshRuntimeOverview,
    });
})();
// END PHASE 2.19 RUNTIME OVERVIEW WIRING

// BEGIN PART F 15-B4C ALL PIPELINES OVERVIEW
(() => {
  "use strict";

  const PIPELINE_INDEX_ENDPOINT =
    "/owner/api/runtime/pipelines";

  const byId = (id) =>
    document.getElementById(id);

  const HTML_ENTITIES = Object.freeze({
    "&": "&amp;",
    "<": "&lt;",
    ">": "&gt;",
    '"': "&quot;",
    "'": "&#039;",
  });

  const escapeHtml = (value) =>
    String(value ?? "").replace(
      /[&<>"']/g,
      (character) => HTML_ENTITIES[character]
    );

  const identifierLabel = (identifier) => {
    const words = String(identifier ?? "")
      .split(/[_-]+/)
      .filter(Boolean)
      .map((word) =>
        word.charAt(0).toUpperCase() +
        word.slice(1)
      );

    return words.join(" ") || "Unnamed Pipeline";
  };

  const pipelineLabel = (pipelineId) => {
    if (String(pipelineId ?? "") === "connect_domain") {
      return "Connected Domain";
    }

    return identifierLabel(pipelineId);
  };

  const countValue = (value) => {
    const number = Number(value);

    if (!Number.isFinite(number)) {
      return "0";
    }

    return String(Math.max(0, number));
  };

  const metric = (label, value) => `
    <div class="pipeline-operations-card-metric">
      <span>${escapeHtml(label)}</span>
      <strong>${escapeHtml(countValue(value))}</strong>
    </div>
  `;

  const renderPipelineCard = (pipeline) => {
    const pipelineId = String(
      pipeline?.pipeline_id || ""
    );

    const health = String(
      pipeline?.health_status || "UNKNOWN"
    ).toUpperCase();

    const healthToken = health
      .toLowerCase()
      .replace(/[^a-z0-9_-]+/g, "-");

    const counts =
      pipeline?.counts &&
      typeof pipeline.counts === "object"
        ? pipeline.counts
        : {};

    const readiness =
      pipeline?.output_readiness &&
      typeof pipeline.output_readiness === "object"
        ? pipeline.output_readiness
        : {};

    const stages = Array.isArray(
      pipeline?.stage_order
    )
      ? pipeline.stage_order
      : [];

    const stageMarkup = stages.length
      ? stages.map((stage) => `
          <span class="pipeline-operations-card-stage">
            ${escapeHtml(identifierLabel(stage))}
          </span>
        `).join("")
      : `
          <span class="pipeline-operations-card-stage">
            No registered stages
          </span>
        `;

    const outputState =
      readiness.all_completed_outputs_ready === true
        ? "All completed outputs ready"
        : "Output readiness pending";

    return `
      <article
        class="pipeline-operations-card"
        role="listitem"
        data-pipeline-id="${escapeHtml(pipelineId)}"
      >
        <div class="pipeline-operations-card-header">
          <div class="pipeline-operations-card-title">
            <strong>${escapeHtml(pipelineLabel(pipelineId))}</strong>
            <span>${escapeHtml(pipelineId)}</span>
          </div>
          <span
            class="pipeline-operations-card-health"
            data-health="${escapeHtml(healthToken)}"
          >
            ${escapeHtml(health)}
          </span>
        </div>

        <div class="pipeline-operations-card-metrics">
          ${metric("Workflows", counts.workflow_count)}
          ${metric("Active workflows", counts.active_workflow_count)}
          ${metric("Failed workflows", counts.failed_workflow_count)}
          ${metric("Jobs", counts.job_count)}
          ${metric("Queued jobs", counts.queued_job_count)}
          ${metric("Running jobs", counts.running_job_count)}
          ${metric("Failed jobs", counts.failed_job_count)}
          ${metric("Registrations", counts.registration_count)}
        </div>

        <div
          class="pipeline-operations-card-stage-list"
          aria-label="${escapeHtml(pipelineLabel(pipelineId))} stage order"
        >
          ${stageMarkup}
        </div>

        <div class="pipeline-operations-card-output">
          <span>
            Final stage: ${escapeHtml(
              identifierLabel(readiness.final_stage_id)
            )}
          </span>
          <span>
            ${escapeHtml(outputState)} ·
            ${escapeHtml(countValue(readiness.ready_workflow_count))} ready
          </span>
        </div>
      </article>
    `;
  };

  const renderIndexState = (
    state,
    title,
    message
  ) => {
    const list = byId(
      "pipelineOperationsPipelineList"
    );

    if (!list) {
      return false;
    }

    list.dataset.pipelineIndexState = state;
    list.innerHTML = `
      <div
        class="pipeline-operations-index-state"
        data-pipeline-index-state="${escapeHtml(state)}"
      >
        <strong>${escapeHtml(title)}</strong>
        <span>${escapeHtml(message)}</span>
      </div>
    `;

    return true;
  };

  const renderPipelineIndex = (payload) => {
    const list = byId(
      "pipelineOperationsPipelineList"
    );

    if (!list) {
      return false;
    }

    const pipelines = Array.isArray(
      payload?.pipelines
    )
      ? payload.pipelines
      : [];

    if (!pipelines.length) {
      renderIndexState(
        "empty",
        "No registered pipelines",
        "Pipeline Operations will list a pipeline after its Runtime registrations are published."
      );

      return true;
    }

    list.dataset.pipelineIndexState = "loaded";
    list.innerHTML = pipelines
      .map(renderPipelineCard)
      .join("");

    return true;
  };

  let requestPromise = null;
  let loaded = false;
  let latestPayload = null;

  const loadPipelineIndex = async (
    force = false
  ) => {
    if (requestPromise) {
      return requestPromise;
    }

    if (loaded && !force) {
      return latestPayload;
    }

    const list = byId(
      "pipelineOperationsPipelineList"
    );

    if (!list) {
      return null;
    }

    list.setAttribute("aria-busy", "true");

    renderIndexState(
      "loading",
      "Loading pipelines",
      "Reading the certified Runtime Pipeline Operations index."
    );

    requestPromise = (async () => {
      try {
        const response = await fetch(
          PIPELINE_INDEX_ENDPOINT,
          {
            method: "GET",
            headers: {
              Accept: "application/json",
            },
            cache: "no-store",
            credentials: "same-origin",
          }
        );

        let payload = null;

        try {
          payload = await response.json();
        } catch (_) {
          payload = null;
        }

        if (!response.ok) {
          const message =
            payload?.detail?.message ||
            `Pipeline index unavailable (${response.status}).`;

          throw new Error(message);
        }

        if (!Array.isArray(payload?.pipelines)) {
          throw new Error(
            "Pipeline index response is missing its pipelines collection."
          );
        }

        latestPayload = payload;
        loaded = true;
        renderPipelineIndex(payload);
        return payload;
      } catch (error) {
        loaded = false;
        latestPayload = null;

        renderIndexState(
          "unavailable",
          "Pipeline index unavailable",
          error?.message ||
            "The Pipeline Operations index request failed."
        );

        return null;
      } finally {
        list.setAttribute("aria-busy", "false");
        requestPromise = null;
      }
    })();

    return requestPromise;
  };

  const pipelineOperationsActive = () =>
    window.LinkCraftorRuntimeOwner?.getActiveSection?.() ===
      "pipeline_operations";

  const bindPipelineOperationsIndex = () => {
    const page = byId("runtimePage");

    if (!page) {
      return false;
    }

    if (
      page.dataset.pipelineOperationsIndexBound ===
      "true"
    ) {
      return true;
    }

    page.addEventListener(
      "runtimeowner:sectionchange",
      (event) => {
        if (
          event?.detail?.section ===
          "pipeline_operations"
        ) {
          void loadPipelineIndex();
        }
      }
    );

    page.dataset.pipelineOperationsIndexBound =
      "true";

    if (pipelineOperationsActive()) {
      void loadPipelineIndex();
    }

    return true;
  };

  window.LinkCraftorPipelineOperationsIndex =
    Object.freeze({
      endpoint: PIPELINE_INDEX_ENDPOINT,
      load: loadPipelineIndex,
      refresh: () => loadPipelineIndex(true),
      render: renderPipelineIndex,
      pipelineLabel,
    });

  if (document.readyState === "loading") {
    document.addEventListener(
      "DOMContentLoaded",
      bindPipelineOperationsIndex,
      { once: true }
    );
  } else {
    bindPipelineOperationsIndex();
  }
})();
// END PART F 15-B4C ALL PIPELINES OVERVIEW
// BEGIN PART F 15-B4D2 NESTED UNIVERSAL RUNTIME SIDEBAR
(() => {
  "use strict";

  const SECTION_GROUPS = Object.freeze({
    overview: "runtimeSidebarCommandCenter",
    pipeline_operations: "runtimeSidebarPipelineOperations",
    jobs: "runtimeSidebarInfrastructure",
    queues: "runtimeSidebarInfrastructure",
    workers_leases: "runtimeSidebarInfrastructure",
    orchestration: "runtimeSidebarInfrastructure",
    execution: "runtimeSidebarInfrastructure",
    reliability_recovery: "runtimeSidebarHealth",
    resource_governance: "runtimeSidebarHealth",
    observability: "runtimeSidebarHealth",
    security: "runtimeSidebarHealth",
    runtime_apis: "runtimeSidebarAdministration",
    persistence_state_integrity: "runtimeSidebarAdministration",
    owner_actions: "runtimeSidebarAdministration",
    evidence_audit: "runtimeSidebarAdministration"
  });

  const byId = (id) => document.getElementById(id);

  const setDisclosure = (button, panel, expanded) => {
    if (!button || !panel) {
      return false;
    }

    button.setAttribute(
      "aria-expanded",
      expanded ? "true" : "false"
    );
    panel.hidden = !expanded;
    return true;
  };

  const collapseMainGroups = (exceptButton = null) => {
    const tree = byId("runtimeSidebarTree");

    if (!tree) {
      return false;
    }

    tree.querySelectorAll(
      ".runtime-sidebar-group > .runtime-sidebar-group-toggle"
    ).forEach((button) => {
      if (button === exceptButton) {
        return;
      }

      const panel = byId(
        button.getAttribute("aria-controls")
      );

      setDisclosure(button, panel, false);
    });

    return true;
  };

  const openRuntimeTree = () => {
    const toggle = byId("runtimeSidebarToggle");
    const tree = byId("runtimeSidebarTree");

    if (!setDisclosure(toggle, tree, true)) {
      return false;
    }

    toggle.setAttribute(
      "aria-label",
      "Collapse Universal Runtime navigation"
    );
    return true;
  };

  const toggleRuntimeTree = () => {
    const toggle = byId("runtimeSidebarToggle");
    const tree = byId("runtimeSidebarTree");

    if (!toggle || !tree) {
      return false;
    }

    const expanded =
      toggle.getAttribute("aria-expanded") === "true";

    setDisclosure(toggle, tree, !expanded);
    toggle.setAttribute(
      "aria-label",
      expanded
        ? "Expand Universal Runtime navigation"
        : "Collapse Universal Runtime navigation"
    );
    return true;
  };

  const openGroupForSection = (section) => {
    const panelId = SECTION_GROUPS[section];
    const panel = panelId ? byId(panelId) : null;

    if (!panel) {
      return false;
    }

    const button = document.querySelector(
      `[data-runtime-sidebar-group-toggle]` +
      `[aria-controls="${panelId}"]`
    );

    collapseMainGroups(button);
    return setDisclosure(button, panel, true);
  };

  const syncRuntimeSidebar = (section) => {
    const tree = byId("runtimeSidebarTree");

    if (!tree) {
      return false;
    }

    tree.querySelectorAll(
      "[data-runtime-sidebar-section]"
    ).forEach((button) => {
      const active =
        button.dataset.runtimeSidebarSection === section;

      button.classList.toggle("active", active);

      if (active) {
        button.setAttribute("aria-current", "page");
      } else {
        button.removeAttribute("aria-current");
      }
    });

    openRuntimeTree();
    openGroupForSection(section);
    return true;
  };

  const showRuntimePage = () => {
    const runtimePage = byId("runtimePage");
    const runtimeButton = byId("runtimeSidebarPageButton");

    if (
      runtimePage &&
      !runtimePage.classList.contains("active")
    ) {
      runtimeButton?.click();
    }
  };

  const bindRuntimeSidebar = () => {
    const entry = byId("runtimeSidebarEntry");
    const runtimePage = byId("runtimePage");
    const runtimeButton = byId("runtimeSidebarPageButton");
    const treeToggle = byId("runtimeSidebarToggle");

    if (!entry || !runtimePage || !runtimeButton || !treeToggle) {
      return false;
    }

    if (entry.dataset.runtimeSidebarBound === "true") {
      return true;
    }

    runtimeButton.addEventListener("click", () => {
      openRuntimeTree();
      syncRuntimeSidebar(
        window.LinkCraftorRuntimeOwner?.getActiveSection() ||
        "overview"
      );
    });
    treeToggle.addEventListener("click", toggleRuntimeTree);

    entry.addEventListener("click", (event) => {
      const groupToggle = event.target.closest(
        "[data-runtime-sidebar-group-toggle]"
      );

      if (groupToggle) {
        const panel = byId(
          groupToggle.getAttribute("aria-controls")
        );
        const expanded =
          groupToggle.getAttribute("aria-expanded") === "true";
        const opening = !expanded;
        const nested = groupToggle.classList.contains(
          "runtime-sidebar-subgroup-toggle"
        );

        if (opening && !nested) {
          collapseMainGroups(groupToggle);
        }

        setDisclosure(groupToggle, panel, opening);
        return;
      }

      const sectionButton = event.target.closest(
        "[data-runtime-sidebar-section]"
      );

      if (!sectionButton || sectionButton.disabled) {
        return;
      }

      showRuntimePage();

      window.LinkCraftorRuntimeOwner?.setActiveSection(
        sectionButton.dataset.runtimeSidebarSection
      );
    });

    runtimePage.addEventListener(
      "runtimeowner:sectionchange",
      (event) => {
        syncRuntimeSidebar(event.detail?.section || "overview");
      }
    );

    entry.dataset.runtimeSidebarBound = "true";

    if (runtimePage.classList.contains("active")) {
      syncRuntimeSidebar(
        window.LinkCraftorRuntimeOwner?.getActiveSection() ||
        "overview"
      );
    }

    return true;
  };

  window.LinkCraftorRuntimeSidebar = Object.freeze({
    bind: bindRuntimeSidebar,
    open: openRuntimeTree,
    sync: syncRuntimeSidebar
  });

  if (document.readyState === "loading") {
    document.addEventListener(
      "DOMContentLoaded",
      bindRuntimeSidebar,
      { once: true }
    );
  } else {
    bindRuntimeSidebar();
  }
})();
// END PART F 15-B4D2 NESTED UNIVERSAL RUNTIME SIDEBAR

// PART F 15-B4D2R COMPACT RUNTIME SIDEBAR CORRECTION
// BEGIN PART F 15-B4D3-D5 COMBINED RUNTIME UI REDESIGN
(() => {
  "use strict";

  const SECTION_PRESENTATION = Object.freeze({
    overview: [
      "Runtime Overview",
      "Shared operational health, activity, capacity, and infrastructure state."
    ],
    pipeline_operations: [
      "Pipeline Operations",
      "Registered pipeline directory and selected-pipeline operations workspace."
    ],
    jobs: ["Jobs", "Runtime job inventory, state, and execution evidence."],
    queues: ["Queues", "Queue depth, pressure, claims, and dispatch state."],
    workers_leases: ["Workers & Leases", "Worker availability and lease ownership."],
    orchestration: ["Orchestration", "Workflow orchestration and dependency state."],
    execution: ["Execution", "Runtime execution activity and terminal outcomes."],
    reliability_recovery: ["Reliability & Recovery", "Failure, retry, and recovery posture."],
    resource_governance: ["Resource Governance", "Runtime capacity and resource controls."],
    observability: ["Observability", "Runtime signals, diagnostics, and evidence."],
    security: ["Security", "Runtime security posture and owner attention."],
    runtime_apis: ["Runtime APIs", "Canonical Runtime API availability and health."],
    persistence_state_integrity: ["Persistence & Integrity", "Durable state and persistence integrity."],
    owner_actions: ["Owner Actions & Recovery", "Governed owner operations, recovery requests, and approvals."],
    evidence_audit: ["Evidence & Audit", "Runtime certification and audit evidence."]
  });

  const updateRuntimeCommandHeader = (section) => {
    const presentation = SECTION_PRESENTATION[section] || SECTION_PRESENTATION.overview;
    const breadcrumb = document.getElementById("runtimeOwnerBreadcrumbCurrent");
    const context = document.getElementById("runtimeOwnerHeaderContext");
    const page = document.getElementById("runtimePage");

    if (breadcrumb) {
      breadcrumb.textContent = presentation[0];
    }

    if (context) {
      context.textContent = presentation[1];
    }

    if (page) {
      page.dataset.runtimeOwnerVisualSection = section;
    }
  };

  const initializeRuntimeCommandHeader = () => {
    const page = document.getElementById("runtimePage");

    if (!page || page.dataset.runtimeCommandHeaderBound === "true") {
      return false;
    }

    page.addEventListener("runtimeowner:sectionchange", (event) => {
      updateRuntimeCommandHeader(event.detail?.section || "overview");
    });

    page.dataset.runtimeCommandHeaderBound = "true";
    updateRuntimeCommandHeader(
      window.LinkCraftorRuntimeOwner?.getActiveSection?.() || "overview"
    );
    return true;
  };

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initializeRuntimeCommandHeader);
  } else {
    initializeRuntimeCommandHeader();
  }
})();
// END PART F 15-B4D3-D5 COMBINED RUNTIME UI REDESIGN
// BEGIN PART F 15-B4D6-D8 COMPONENT SHELLS NAVIGATION AND STATES
(() => {
  "use strict";

  const VIEW_ALIASES = Object.freeze({
    failures_attention: "failures"
  });

  const normalizeView = (view) =>
    VIEW_ALIASES[view] || view || "overview";

  const pipelineLabel = (pipelineId) => {
    if (pipelineId === "connect_domain") {
      return "Connected Domain";
    }

    return String(pipelineId || "")
      .split(/[_-]+/)
      .filter(Boolean)
      .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
      .join(" ") || "Selected Pipeline";
  };

  const setSelectedPipeline = (pipelineId) => {
    const name = document.getElementById("pipelineOperationsSelectedPipeline");
    const summary = document.getElementById("pipelineOperationsSelectedPipelineSummary");
    const health = document.getElementById("pipelineOperationsSelectedPipelineHealth");
    const workspace = document.getElementById("pipelineOperationsWorkspace");
    const label = pipelineLabel(pipelineId);

    if (name) name.textContent = label;
    if (summary) {
      summary.textContent = pipelineId === "connect_domain"
        ? "Six-stage Connected Domain monitoring workspace."
        : "Universal monitoring shell for the selected registered pipeline.";
    }
    if (health) health.textContent = "Structure ready";
    if (workspace) workspace.dataset.selectedPipelineId = pipelineId;
    return true;
  };

  const setPipelineView = (requestedView) => {
    const view = normalizeView(requestedView);
    const mount = document.getElementById("pipelineOperationsViewMount");
    const nav = document.getElementById("pipelineOperationsViewNav");

    if (!mount || !nav) return false;

    let matched = false;
    mount.querySelectorAll("[data-pipeline-operations-view-panel]").forEach((panel) => {
      const active = panel.dataset.pipelineOperationsViewPanel === view;
      panel.hidden = !active;
      panel.classList.toggle("active", active);
      if (active) matched = true;
    });

    nav.querySelectorAll("[data-pipeline-operations-view]").forEach((button) => {
      const active = button.dataset.pipelineOperationsView === view;
      button.classList.toggle("active", active);
      button.setAttribute("aria-selected", active ? "true" : "false");
    });

    document.querySelectorAll("[data-runtime-pipeline-view]").forEach((button) => {
      const active = normalizeView(button.dataset.runtimePipelineView) === view;
      button.classList.toggle("active", active);
      if (active) button.setAttribute("aria-current", "page");
      else button.removeAttribute("aria-current");
    });

    if (matched) {
      mount.dataset.activePipelineView = view;
      if (view === "workflows") {
        window.LinkCraftorConnectedDomainWorkflowExplorer?.activate?.();
      }
      if (view === "stage_progress") {
        window.LinkCraftorConnectedDomainStageProgress?.activate?.();
      }
      if (view === "jobs_attempts") {
        window.LinkCraftorConnectedDomainJobsAttempts?.activate?.();
      }
      if (view === "dependencies_handoffs") {
        window.LinkCraftorConnectedDomainDependenciesHandoffs?.activate?.();
      }
      if (view === "events_timeline") {
        window.LinkCraftorConnectedDomainEventsTimeline?.activate?.();
      }
      if (view === "failures") {
        window.LinkCraftorConnectedDomainFailuresAttention?.activate?.();
      }
      if (view === "output_readiness") {
        window.LinkCraftorConnectedDomainOutputReadiness?.activate?.();
      }
    }
    return matched;
  };

  const openPipelineWorkspace = (pipelineId, view = "overview") => {
    window.LinkCraftorRuntimeOwner?.setActiveSection?.("pipeline_operations");
    setSelectedPipeline(pipelineId);
    setPipelineView(view);
    window.LinkCraftorConnectedDomainOverview?.load?.(pipelineId);
    return true;
  };

  const decoratePipelineCards = () => {
    document.querySelectorAll(".pipeline-operations-card[data-pipeline-id]").forEach((card) => {
      card.tabIndex = 0;
      card.setAttribute("role", "button");
      card.setAttribute("data-component-selectable", "true");
      card.setAttribute("aria-label", `Open ${pipelineLabel(card.dataset.pipelineId)} operations`);
    });
  };

  const initializePipelineComponentShells = () => {
    const page = document.getElementById("runtimePage");
    const nav = document.getElementById("pipelineOperationsViewNav");
    const list = document.getElementById("pipelineOperationsPipelineList");

    if (!page || !nav || !list || page.dataset.pipelineComponentShellsBound === "true") {
      return false;
    }

    nav.addEventListener("click", (event) => {
      const button = event.target.closest("[data-pipeline-operations-view]");
      if (button) setPipelineView(button.dataset.pipelineOperationsView);
    });

    // PART F 15-B4D9 SIDEBAR NAVIGATION BOUNDARY CORRECTION
    document.addEventListener("click", (event) => {
      const destination = event.target.closest("[data-runtime-pipeline-view]");
      if (destination) {
        openPipelineWorkspace(
          destination.dataset.runtimePipelineId || "connect_domain",
          destination.dataset.runtimePipelineView
        );
        return;
      }

      const card = event.target.closest(".pipeline-operations-card[data-pipeline-id]");
      if (card) openPipelineWorkspace(card.dataset.pipelineId, "overview");
    });

    list.addEventListener("keydown", (event) => {
      if (event.key !== "Enter" && event.key !== " ") return;
      const card = event.target.closest(".pipeline-operations-card[data-pipeline-id]");
      if (!card) return;
      event.preventDefault();
      openPipelineWorkspace(card.dataset.pipelineId, "overview");
    });

    new MutationObserver(decoratePipelineCards).observe(list, { childList: true, subtree: true });
    decoratePipelineCards();
    setPipelineView("overview");
    page.dataset.pipelineComponentShellsBound = "true";
    return true;
  };

  window.LinkCraftorPipelineComponentShells = Object.freeze({
    open: openPipelineWorkspace,
    selectPipeline: setSelectedPipeline,
    setView: setPipelineView
  });

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initializePipelineComponentShells, { once: true });
  } else {
    initializePipelineComponentShells();
  }
})();
// END PART F 15-B4D6-D8 COMPONENT SHELLS NAVIGATION AND STATES
// BEGIN PART F 15-B4D10 CONNECTED DOMAIN OVERVIEW LIVE EVIDENCE
(() => {
  "use strict";

  const PIPELINE_ID = "connect_domain";
  const DETAIL_ENDPOINT = "/owner/api/runtime/pipelines/connect_domain";
  let requestSequence = 0;
  let latestSnapshot = null;

  const byId = (id) => document.getElementById(id);
  const setText = (id, value) => {
    const element = byId(id);
    if (element) element.textContent = String(value ?? "—");
  };
  const integer = (value) => {
    const number = Number(value);
    return Number.isFinite(number) && number >= 0 ? Math.trunc(number) : 0;
  };
  const label = (value) => String(value || "unknown")
    .split(/[_-]+/)
    .filter(Boolean)
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(" ");

  const updateMessage = (state, title, message, symbol) => {
    const panel = byId("pipelineOperationsViewOverview");
    const status = byId("pipelineConnectedDomainOverviewState");
    const container = byId("pipelineConnectedDomainOverviewMessage");
    if (panel) {
      panel.dataset.componentState = state;
      panel.setAttribute("aria-busy", state === "loading" ? "true" : "false");
    }
    if (status) status.textContent = label(state);
    if (container) {
      container.dataset.state = state;
      const icon = container.querySelector(":scope > span");
      const heading = container.querySelector("strong");
      const paragraph = container.querySelector("p");
      if (icon) icon.textContent = symbol;
      if (heading) heading.textContent = title;
      if (paragraph) paragraph.textContent = message;
    }
  };

  const resetValues = () => {
    [
      "pipelineConnectedDomainActiveWorkflows",
      "pipelineConnectedDomainWorkflowCount",
      "pipelineConnectedDomainFailedWorkflows",
      "pipelineConnectedDomainJobCount",
      "pipelineConnectedDomainFailedJobs",
      "pipelineConnectedDomainRegistrationCount",
      "pipelineConnectedDomainReadyWorkflows",
      "pipelineConnectedDomainFinalStage",
      "pipelineConnectedDomainGeneratedAt"
    ].forEach((id) => setText(id, "—"));
    setText("pipelineConnectedDomainHealth", "Loading");
    setText("pipelineConnectedDomainOutputReadiness", "Evaluating");
  };

  const renderSnapshot = (payload) => {
    if (!payload || payload.pipeline_id !== PIPELINE_ID) {
      throw new Error("Connected Domain detail evidence has an invalid identity.");
    }
    const counts = payload.counts && typeof payload.counts === "object"
      ? payload.counts : {};
    const readiness = payload.output_readiness && typeof payload.output_readiness === "object"
      ? payload.output_readiness : {};
    const stageOrder = Array.isArray(payload.stage_order) ? payload.stage_order : [];
    if (stageOrder.length !== 6) {
      throw new Error("Connected Domain detail evidence does not contain six stages.");
    }
    latestSnapshot = payload;

    const workflowCount = integer(counts.workflow_count);
    const completedCount = integer(readiness.completed_workflow_count);
    const readyCount = integer(readiness.ready_workflow_count);
    const readinessStatus = String(readiness.readiness_status || "")
      .trim()
      .toUpperCase();
    const readinessLabels = Object.freeze({
      NOT_EVALUATED: "Not evaluated",
      PENDING: "Pending",
      BLOCKED: "Blocked",
      VERIFIED: "Verified"
    });
    // BEGIN PART F 15-B4D10R OUTPUT READINESS PRESENTATION
    if (!Object.prototype.hasOwnProperty.call(readinessLabels, readinessStatus)) {
      throw new Error("Connected Domain output-readiness status is unavailable.");
    }
    if (readyCount > completedCount || completedCount > workflowCount) {
      throw new Error("Connected Domain output-readiness counts are inconsistent.");
    }
    // END PART F 15-B4D10R OUTPUT READINESS PRESENTATION
    const health = label(payload.health_status);
    setText("pipelineConnectedDomainHealth", health);
    setText("pipelineConnectedDomainActiveWorkflows", integer(counts.active_workflow_count));
    setText("pipelineConnectedDomainWorkflowCount", workflowCount);
    setText("pipelineConnectedDomainFailedWorkflows", integer(counts.failed_workflow_count));
    setText("pipelineConnectedDomainJobCount", integer(counts.job_count));
    setText("pipelineConnectedDomainFailedJobs", integer(counts.failed_job_count));
    setText("pipelineConnectedDomainRegistrationCount", integer(counts.registration_count));
    setText("pipelineConnectedDomainReadyWorkflows", readyCount);
    setText("pipelineConnectedDomainFinalStage", label(readiness.final_stage_id));
    setText("pipelineConnectedDomainGeneratedAt", payload.generated_at || "Unavailable");
    setText(
      "pipelineConnectedDomainOutputReadiness",
      readinessLabels[readinessStatus]
    );
    setText("pipelineOperationsSelectedPipelineHealth", health);

    if (workflowCount === 0) {
      updateMessage(
        "empty",
        "No Connected Domain workflows",
        "The pipeline is registered and healthy, but no workflow evidence is currently stored.",
        "◎"
      );
    } else {
      updateMessage(
        "ready",
        "Live Connected Domain evidence loaded",
        `${workflowCount} workflow${workflowCount === 1 ? "" : "s"} projected from canonical Runtime authorities.`,
        "✓"
      );
    }
  };

  const renderUnavailable = (message) => {
    latestSnapshot = null;
    resetValues();
    setText("pipelineConnectedDomainHealth", "Unavailable");
    setText("pipelineConnectedDomainOutputReadiness", "Unavailable");
    updateMessage(
      "unavailable",
      "Connected Domain evidence unavailable",
      message || "The read-only Pipeline Operations projection could not be loaded.",
      "!"
    );
    window.LinkCraftorConnectedDomainWorkflowExplorer?.renderUnavailable?.(
      message || "The read-only Pipeline Operations projection could not be loaded."
    );
    window.LinkCraftorConnectedDomainStageProgress?.renderUnavailable?.(
      message || "The read-only Pipeline Operations projection could not be loaded."
    );
    window.LinkCraftorConnectedDomainJobsAttempts?.renderUnavailable?.(
      message || "The read-only Pipeline Operations projection could not be loaded."
    );
    window.LinkCraftorConnectedDomainDependenciesHandoffs?.renderUnavailable?.(
      message || "The read-only Pipeline Operations projection could not be loaded."
    );
    window.LinkCraftorConnectedDomainEventsTimeline?.renderUnavailable?.(
      message || "The read-only Pipeline Operations projection could not be loaded."
    );
    window.LinkCraftorConnectedDomainFailuresAttention?.renderUnavailable?.(
      message || "The read-only Pipeline Operations projection could not be loaded."
    );
    window.LinkCraftorConnectedDomainOutputReadiness?.renderUnavailable?.(
      message || "The read-only Pipeline Operations projection could not be loaded."
    );
  };

  const load = async (pipelineId = PIPELINE_ID) => {
    if (pipelineId !== PIPELINE_ID) {
      renderUnavailable("Detailed monitoring is not yet connected for this pipeline.");
      return false;
    }
    const sequence = ++requestSequence;
    resetValues();
    updateMessage(
      "loading",
      "Loading Connected Domain evidence",
      "Reading the canonical Pipeline Operations projection.",
      "◌"
    );
    try {
      const response = await fetch(DETAIL_ENDPOINT, {
        method: "GET",
        headers: { Accept: "application/json" },
        cache: "no-store"
      });
      if (!response.ok) {
        throw new Error(`Pipeline detail request failed with HTTP ${response.status}.`);
      }
      const payload = await response.json();
      if (sequence !== requestSequence) return false;
      renderSnapshot(payload);
      window.LinkCraftorConnectedDomainWorkflowExplorer?.render?.(payload);
      window.LinkCraftorConnectedDomainStageProgress?.render?.(payload);
      window.LinkCraftorConnectedDomainJobsAttempts?.render?.(payload);
      window.LinkCraftorConnectedDomainDependenciesHandoffs?.render?.(payload);
      window.LinkCraftorConnectedDomainEventsTimeline?.render?.(payload);
      window.LinkCraftorConnectedDomainFailuresAttention?.render?.(payload);
      window.LinkCraftorConnectedDomainOutputReadiness?.render?.(payload);
      return true;
    } catch (error) {
      if (sequence !== requestSequence) return false;
      renderUnavailable(error?.message);
      return false;
    }
  };

  window.LinkCraftorConnectedDomainOverview = Object.freeze({
    load,
    getSnapshot: () => latestSnapshot
  });
})();
// END PART F 15-B4D10 CONNECTED DOMAIN OVERVIEW LIVE EVIDENCE
// BEGIN PART F 15-B4E WORKFLOW EXPLORER
(() => {
  "use strict";

  const PIPELINE_ID = "connect_domain";
  let latestPayload = null;
  let selectedWorkflowId = "";
  let activeStatus = "all";
  let searchQuery = "";
  let bound = false;

  const byId = (id) => document.getElementById(id);
  const escapeHtml = (value) => String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
  const label = (value) => String(value || "unknown")
    .split(/[_-]+/)
    .filter(Boolean)
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(" ");
  const array = (value) => Array.isArray(value) ? value : [];
  const integer = (value) => {
    const number = Number(value);
    return Number.isFinite(number) && number >= 0 ? Math.trunc(number) : 0;
  };
  const timestamp = (value) => {
    if (!value) return "Unavailable";
    const date = new Date(value);
    return Number.isNaN(date.getTime()) ? String(value) : date.toLocaleString();
  };

  const normalizeWorkflow = (workflow) => {
    const workflowId = String(workflow?.workflow_id || "").trim();
    if (!workflowId) {
      throw new Error("Workflow evidence contains an empty workflow identity.");
    }
    return Object.freeze({
      workflowId,
      correlationId: String(workflow?.correlation_id || "Unavailable"),
      workspaceId: String(workflow?.workspace_id || "Unavailable"),
      status: String(workflow?.status || "unknown").toLowerCase(),
      currentStage: String(workflow?.current_stage || ""),
      createdAt: workflow?.created_at || null,
      updatedAt: workflow?.updated_at || null,
      jobCount: integer(workflow?.job_count),
      stageCount: integer(workflow?.stage_count),
      completedStages: array(workflow?.completed_stages).map(String),
      pendingStages: array(workflow?.pending_stages).map(String),
      failedStages: array(workflow?.failed_stages).map(String),
      outputReady: workflow?.output_ready === true
    });
  };

  const inspect = (payload) => {
    if (!payload || payload.pipeline_id !== PIPELINE_ID) {
      throw new Error("Workflow Explorer received an invalid pipeline identity.");
    }
    if (!Array.isArray(payload.stage_order) || payload.stage_order.length !== 6) {
      throw new Error("Workflow Explorer requires the six-stage Connected Domain contract.");
    }
    if (!Array.isArray(payload.workflows)) {
      throw new Error("Workflow Explorer requires a persisted workflows collection.");
    }
    return payload.workflows.map(normalizeWorkflow);
  };

  const updateMessage = (state, title, message, symbol) => {
    const panel = byId("pipelineOperationsViewWorkflows");
    const stateLabel = byId("pipelineWorkflowExplorerState");
    const container = byId("pipelineWorkflowExplorerMessage");
    if (panel) {
      panel.dataset.componentState = state;
      panel.setAttribute("aria-busy", state === "loading" ? "true" : "false");
    }
    if (stateLabel) stateLabel.textContent = label(state);
    if (container) {
      container.dataset.state = state;
      const icon = container.querySelector(":scope > span");
      const heading = container.querySelector("strong");
      const paragraph = container.querySelector("p");
      if (icon) icon.textContent = symbol;
      if (heading) heading.textContent = title;
      if (paragraph) paragraph.textContent = message;
    }
  };

  const placeholder = (title, message) => `
    <div class="pipeline-workflow-placeholder">
      <strong>${escapeHtml(title)}</strong>
      <p>${escapeHtml(message)}</p>
    </div>
  `;

  const workflowMatches = (workflow) => {
    const statusMatches = activeStatus === "all" || workflow.status === activeStatus;
    const query = searchQuery.trim().toLowerCase();
    if (!query) return statusMatches;
    return statusMatches && [
      workflow.workflowId,
      workflow.correlationId,
      workflow.workspaceId
    ].some((value) => value.toLowerCase().includes(query));
  };

  const renderDetail = (workflow) => {
    const detail = byId("pipelineWorkflowExplorerDetail");
    if (!detail) return false;
    detail.innerHTML = `
      <header class="pipeline-workflow-detail-head">
        <div><span>Selected workflow</span><strong>${escapeHtml(workflow.workflowId)}</strong></div>
        <span class="pipeline-workflow-status" data-status="${escapeHtml(workflow.status)}">${escapeHtml(label(workflow.status))}</span>
      </header>
      <div class="pipeline-workflow-identity-grid">
        <article><span>Correlation identity</span><strong>${escapeHtml(workflow.correlationId)}</strong></article>
        <article><span>Workspace identity</span><strong>${escapeHtml(workflow.workspaceId)}</strong></article>
        <article><span>Current stage</span><strong>${escapeHtml(workflow.currentStage ? label(workflow.currentStage) : "No active stage")}</strong></article>
        <article><span>Final output</span><strong>${workflow.outputReady ? "Ready" : "Pending"}</strong></article>
      </div>
      <div class="pipeline-workflow-lifecycle-grid">
        <article><span>Created</span><strong>${escapeHtml(timestamp(workflow.createdAt))}</strong></article>
        <article><span>Last updated</span><strong>${escapeHtml(timestamp(workflow.updatedAt))}</strong></article>
      </div>
      <div class="pipeline-workflow-stage-summary" aria-label="Selected workflow evidence counts">
        <article><strong>${escapeHtml(workflow.stageCount)}</strong><span>Stages</span></article>
        <article><strong>${escapeHtml(workflow.completedStages.length)}</strong><span>Completed</span></article>
        <article><strong>${escapeHtml(workflow.pendingStages.length)}</strong><span>Pending</span></article>
        <article><strong>${escapeHtml(workflow.jobCount)}</strong><span>Jobs</span></article>
      </div>
    `;
    return true;
  };

  const renderDirectory = (workflows) => {
    const directory = byId("pipelineWorkflowExplorerDirectory");
    const count = byId("pipelineWorkflowExplorerCount");
    if (!directory) return false;
    const filtered = workflows.filter(workflowMatches);
    if (count) count.textContent = `${filtered.length} of ${workflows.length}`;
    if (!filtered.length) {
      selectedWorkflowId = "";
      directory.innerHTML = placeholder(
        workflows.length ? "No workflows match" : "No persisted workflows",
        workflows.length
          ? "Change the status filter or identity search."
          : "Connected Domain has no stored workflow evidence."
      );
      directory.setAttribute("aria-busy", "false");
      const detail = byId("pipelineWorkflowExplorerDetail");
      if (detail) detail.innerHTML = placeholder(
        "No workflow selected",
        workflows.length ? "No filtered workflow is available." : "Workflow detail will appear after activation."
      );
      return filtered;
    }
    if (!filtered.some((item) => item.workflowId === selectedWorkflowId)) {
      selectedWorkflowId = filtered[0].workflowId;
    }
    directory.innerHTML = filtered.map((workflow) => `
      <button class="pipeline-workflow-row${workflow.workflowId === selectedWorkflowId ? " active" : ""}" type="button" role="option" aria-selected="${workflow.workflowId === selectedWorkflowId ? "true" : "false"}" data-workflow-explorer-id="${escapeHtml(workflow.workflowId)}">
        <span class="pipeline-workflow-row-head"><strong>${escapeHtml(workflow.workflowId)}</strong><span class="pipeline-workflow-status" data-status="${escapeHtml(workflow.status)}">${escapeHtml(label(workflow.status))}</span></span>
        <span class="pipeline-workflow-row-meta"><span>${escapeHtml(workflow.workspaceId)}</span><span>${escapeHtml(timestamp(workflow.updatedAt))}</span></span>
      </button>
    `).join("");
    directory.setAttribute("aria-busy", "false");
    renderDetail(filtered.find((item) => item.workflowId === selectedWorkflowId));
    return filtered;
  };

  const currentWorkflows = () => latestPayload ? inspect(latestPayload) : [];

  const applyFilters = () => {
    const workflows = currentWorkflows();
    const filtered = renderDirectory(workflows);
    if (!workflows.length) {
      updateMessage("empty", "No persisted workflows", "Connected Domain is registered, but no workflow evidence is stored.", "◎");
    } else if (!filtered.length) {
      updateMessage("ready", "No matching workflow", "The explorer is connected; adjust the local filters to display evidence.", "⌕");
    } else {
      updateMessage("ready", "Workflow evidence loaded", `${workflows.length} persisted workflow${workflows.length === 1 ? "" : "s"} available for inspection.`, "✓");
    }
  };

  const ensureBound = () => {
    if (bound) return true;
    const panel = byId("pipelineOperationsViewWorkflows");
    const statusFilter = byId("pipelineWorkflowExplorerStatusFilter");
    const search = byId("pipelineWorkflowExplorerSearch");
    if (!panel || !statusFilter || !search) return false;
    panel.addEventListener("click", (event) => {
      const row = event.target.closest("[data-workflow-explorer-id]");
      if (!row) return;
      selectedWorkflowId = row.dataset.workflowExplorerId || "";
      applyFilters();
    });
    statusFilter.addEventListener("change", () => {
      activeStatus = String(statusFilter.value || "all").toLowerCase();
      applyFilters();
    });
    search.addEventListener("input", () => {
      searchQuery = String(search.value || "");
      applyFilters();
    });
    bound = true;
    return true;
  };

  const render = (payload) => {
    ensureBound();
    try {
      const workflows = inspect(payload);
      latestPayload = payload;
      const count = byId("pipelineWorkflowExplorerCount");
      if (count) count.textContent = String(workflows.length);
      applyFilters();
      return true;
    } catch (error) {
      renderUnavailable(error?.message);
      return false;
    }
  };

  const renderUnavailable = (message) => {
    latestPayload = null;
    const directory = byId("pipelineWorkflowExplorerDirectory");
    const detail = byId("pipelineWorkflowExplorerDetail");
    const count = byId("pipelineWorkflowExplorerCount");
    if (directory) {
      directory.innerHTML = placeholder("Workflow evidence unavailable", message || "The canonical detail projection could not be loaded.");
      directory.setAttribute("aria-busy", "false");
    }
    if (detail) detail.innerHTML = placeholder("No workflow detail", "Restore the read-only projection before inspecting workflows.");
    if (count) count.textContent = "Unavailable";
    updateMessage("unavailable", "Workflow evidence unavailable", message || "The canonical detail projection could not be loaded.", "!");
    return false;
  };

  const activate = () => {
    ensureBound();
    const snapshot = window.LinkCraftorConnectedDomainOverview?.getSnapshot?.();
    if (snapshot) return render(snapshot);
    const directory = byId("pipelineWorkflowExplorerDirectory");
    if (directory) {
      directory.innerHTML = placeholder("Loading workflows", "Waiting for the existing Connected Domain detail request.");
      directory.setAttribute("aria-busy", "true");
    }
    updateMessage("loading", "Loading workflow evidence", "Waiting for the existing Connected Domain detail snapshot.", "◌");
    return false;
  };

  window.LinkCraftorConnectedDomainWorkflowExplorer = Object.freeze({
    activate,
    render,
    renderUnavailable,
    inspect
  });
})();
// END PART F 15-B4E WORKFLOW EXPLORER
// BEGIN PART F 15-B4F SIX-STAGE PROGRESS COMPONENT
(() => {
  "use strict";
  const PIPELINE_ID = "connect_domain";
  const STAGE_LABELS = Object.freeze({
    connect_domain: "Connect Domain",
    site_sources: "Site Sources",
    url_cleaner: "URL Cleaner",
    site_pages: "Site Pages",
    live_domain_target_pool: "Live Domain Target Pool",
    active_target_set: "Active Target Set"
  });
  let latestPayload = null;
  let selectedWorkflowId = "";
  let bound = false;
  const byId = (id) => document.getElementById(id);
  const escapeHtml = (value) => String(value ?? "").replaceAll("&", "&amp;").replaceAll("<", "&lt;").replaceAll(">", "&gt;").replaceAll('"', "&quot;").replaceAll("'", "&#039;");
  const label = (value) => STAGE_LABELS[String(value || "")] || String(value || "Unknown").split(/[_-]+/).filter(Boolean).map((part) => part.charAt(0).toUpperCase() + part.slice(1)).join(" ");
  const array = (value) => Array.isArray(value) ? value.map(String) : [];
  const inspect = (payload) => {
    if (!payload || payload.pipeline_id !== PIPELINE_ID) throw new Error("Stage Progress received an invalid pipeline identity.");
    if (!Array.isArray(payload.stage_order) || payload.stage_order.length !== 6) throw new Error("Stage Progress requires the six-stage Connected Domain contract.");
    if (!Array.isArray(payload.workflows)) throw new Error("Stage Progress requires persisted workflow evidence.");
    const workflows = payload.workflows.map((workflow) => {
      const workflowId = String(workflow?.workflow_id || "").trim();
      if (!workflowId) throw new Error("Stage Progress received an empty workflow identity.");
      return Object.freeze({
        workflowId,
        status: String(workflow?.status || "unknown").toLowerCase(),
        currentStage: String(workflow?.current_stage || ""),
        completed: array(workflow?.completed_stages),
        pending: array(workflow?.pending_stages),
        failed: array(workflow?.failed_stages),
        outputReady: workflow?.output_ready === true
      });
    });
    return Object.freeze({ stageOrder: payload.stage_order.map(String), workflows });
  };
  const updateMessage = (state, title, message, symbol) => {
    const panel = byId("pipelineOperationsViewStageProgress");
    const stateLabel = byId("pipelineStageProgressState");
    const container = byId("pipelineStageProgressMessage");
    if (panel) { panel.dataset.componentState = state; panel.setAttribute("aria-busy", state === "loading" ? "true" : "false"); }
    if (stateLabel) stateLabel.textContent = state === "ready" ? "Live evidence" : label(state);
    if (container) {
      container.dataset.state = state;
      const icon = container.querySelector(":scope > span");
      const heading = container.querySelector("strong");
      const paragraph = container.querySelector("p");
      if (icon) icon.textContent = symbol;
      if (heading) heading.textContent = title;
      if (paragraph) paragraph.textContent = message;
    }
  };
  const stageState = (stage, workflow) => {
    if (workflow.failed.includes(stage)) return "failed";
    if (workflow.completed.includes(stage)) return "completed";
    if (workflow.currentStage === stage) return "current";
    if (workflow.pending.includes(stage)) return "pending";
    return "not_evaluated";
  };
  const renderWorkflow = (contract, workflow) => {
    const list = byId("pipelineStageProgressList");
    const lifecycle = byId("pipelineStageProgressLifecycle");
    const current = byId("pipelineStageProgressCurrent");
    const count = byId("pipelineStageProgressCount");
    const meter = byId("pipelineStageProgressMeter");
    if (!list) return false;
    const completeCount = contract.stageOrder.filter((stage) => workflow.completed.includes(stage)).length;
    list.innerHTML = contract.stageOrder.map((stage, index) => {
      const state = stageState(stage, workflow);
      const text = state === "completed" ? "Completed" : state === "current" ? "Current stage" : state === "failed" ? "Failed" : state === "pending" ? "Awaiting execution" : "Not evaluated";
      return `<li class="is-${escapeHtml(state)}" data-stage-id="${escapeHtml(stage)}"><span>${String(index + 1).padStart(2, "0")}</span><div><strong>${escapeHtml(label(stage))}</strong><small>${escapeHtml(text)}</small></div><b>${escapeHtml(state.replace("_", " "))}</b></li>`;
    }).join("");
    list.setAttribute("aria-busy", "false");
    if (lifecycle) lifecycle.textContent = label(workflow.status);
    if (current) current.textContent = workflow.currentStage ? label(workflow.currentStage) : workflow.outputReady ? "Complete" : "No active stage";
    if (count) count.textContent = `${completeCount} of ${contract.stageOrder.length}`;
    if (meter) meter.style.width = `${Math.round((completeCount / contract.stageOrder.length) * 100)}%`;
    const state = workflow.failed.length ? "failed" : workflow.outputReady ? "complete" : workflow.currentStage ? "active" : "pending";
    updateMessage("ready", "Stage evidence loaded", `${label(state)} workflow · ${completeCount} of ${contract.stageOrder.length} stages completed.`, "✓");
    return true;
  };
  const populateWorkflowSelector = (workflows) => {
    const select = byId("pipelineStageProgressWorkflow");
    if (!select) return false;
    if (!workflows.length) { select.innerHTML = '<option value="">No workflows</option>'; select.disabled = true; return false; }
    select.disabled = false;
    if (!workflows.some((workflow) => workflow.workflowId === selectedWorkflowId)) selectedWorkflowId = workflows[0].workflowId;
    select.innerHTML = workflows.map((workflow) => `<option value="${escapeHtml(workflow.workflowId)}"${workflow.workflowId === selectedWorkflowId ? " selected" : ""}>${escapeHtml(workflow.workflowId)} · ${escapeHtml(label(workflow.status))}</option>`).join("");
    return true;
  };
  const render = (payload) => {
    try {
      const contract = inspect(payload);
      latestPayload = payload;
      ensureBound();
      if (!contract.workflows.length) {
        populateWorkflowSelector([]);
        const list = byId("pipelineStageProgressList");
        if (list) { list.innerHTML = '<li class="is-not_evaluated"><span>—</span><div><strong>No persisted workflow</strong><small>Stage evidence will appear after workflow activation.</small></div><b>empty</b></li>'; list.setAttribute("aria-busy", "false"); }
        updateMessage("empty", "No workflow stage evidence", "Connected Domain has no persisted workflow to evaluate.", "◎");
        return true;
      }
      populateWorkflowSelector(contract.workflows);
      return renderWorkflow(contract, contract.workflows.find((workflow) => workflow.workflowId === selectedWorkflowId) || contract.workflows[0]);
    } catch (error) { return renderUnavailable(error?.message); }
  };
  const renderUnavailable = (message) => {
    latestPayload = null;
    const list = byId("pipelineStageProgressList");
    const select = byId("pipelineStageProgressWorkflow");
    if (select) { select.innerHTML = '<option value="">Unavailable</option>'; select.disabled = true; }
    if (list) { list.innerHTML = '<li class="is-failed"><span>!</span><div><strong>Stage evidence unavailable</strong><small>Restore the canonical read-only projection.</small></div><b>unavailable</b></li>'; list.setAttribute("aria-busy", "false"); }
    updateMessage("unavailable", "Stage evidence unavailable", message || "The canonical detail projection could not be loaded.", "!");
    return false;
  };
  const ensureBound = () => {
    if (bound) return true;
    const select = byId("pipelineStageProgressWorkflow");
    if (!select) return false;
    select.addEventListener("change", () => { selectedWorkflowId = String(select.value || ""); if (latestPayload) render(latestPayload); });
    bound = true;
    return true;
  };
  const activate = () => {
    ensureBound();
    const snapshot = window.LinkCraftorConnectedDomainOverview?.getSnapshot?.();
    if (snapshot) return render(snapshot);
    updateMessage("loading", "Loading stage evidence", "Waiting for the existing Connected Domain detail snapshot.", "◌");
    return false;
  };
  window.LinkCraftorConnectedDomainStageProgress = Object.freeze({ activate, render, renderUnavailable, inspect });
})();
// END PART F 15-B4F SIX-STAGE PROGRESS COMPONENT
// BEGIN PART F 15-B4G JOBS AND ATTEMPTS COMPONENT
(() => {
  "use strict";
  const PIPELINE_ID = "connect_domain";
  let latestPayload = null;
  let selectedWorkflowId = "";
  let selectedJobId = "";
  let activeStatus = "all";
  let searchQuery = "";
  let bound = false;
  const byId = (id) => document.getElementById(id);
  const escapeHtml = (value) => String(value ?? "").replaceAll("&", "&amp;").replaceAll("<", "&lt;").replaceAll(">", "&gt;").replaceAll('"', "&quot;").replaceAll("'", "&#039;");
  const label = (value) => String(value || "unknown").split(/[_-]+/).filter(Boolean).map((part) => part.charAt(0).toUpperCase() + part.slice(1)).join(" ");
  const array = (value) => Array.isArray(value) ? value : [];
  const integer = (value) => { const number = Number(value); return Number.isFinite(number) && number >= 0 ? Math.trunc(number) : 0; };
  const percent = (value) => { const number = Number(value); return Number.isFinite(number) ? Math.max(0, Math.min(100, number)) : 0; };
  const timestamp = (value) => { if (!value) return "Unavailable"; const date = new Date(value); return Number.isNaN(date.getTime()) ? String(value) : date.toLocaleString(); };
  const normalizeJob = (job, stageId, workflowId) => {
    const jobId = String(job?.job_id || "").trim();
    if (!jobId) throw new Error("Jobs & Attempts received an empty job identity.");
    return Object.freeze({
      jobId, workflowId, stageId, jobType: String(job?.job_type || "Unavailable"), status: String(job?.status || "unknown").toLowerCase(),
      priority: job?.priority ?? "Unavailable", progressPercent: percent(job?.progress_percent), progressMessage: String(job?.progress_message || "No progress message"),
      assignedWorkerId: String(job?.assigned_worker_id || "Unassigned"), createdAt: job?.created_at || null, startedAt: job?.started_at || null,
      completedAt: job?.completed_at || null, updatedAt: job?.updated_at || null, errorMessage: job?.error_message ? String(job.error_message) : "",
      attempt: integer(job?.attempt), maximumAttempts: integer(job?.maximum_attempts), retryScheduled: job?.retry_scheduled === true,
      retryExhausted: job?.retry_exhausted === true, dispatchResultAvailable: job?.runtime_dispatch_result_available === true,
      eventCount: array(job?.events).length
    });
  };
  const inspect = (payload) => {
    if (!payload || payload.pipeline_id !== PIPELINE_ID) throw new Error("Jobs & Attempts received an invalid pipeline identity.");
    if (!Array.isArray(payload.workflows)) throw new Error("Jobs & Attempts requires persisted workflow evidence.");
    const workflows = payload.workflows.map((workflow) => {
      const workflowId = String(workflow?.workflow_id || "").trim();
      if (!workflowId) throw new Error("Jobs & Attempts received an empty workflow identity.");
      const jobs = array(workflow?.stages).flatMap((stage) => array(stage?.jobs).map((job) => normalizeJob(job, String(stage?.stage_id || "unknown"), workflowId)));
      return Object.freeze({ workflowId, status: String(workflow?.status || "unknown").toLowerCase(), jobs });
    });
    return Object.freeze({ workflows });
  };
  const updateMessage = (state, title, message, symbol) => {
    const panel = byId("pipelineOperationsViewJobsAttempts"); const stateLabel = byId("pipelineJobsAttemptsState"); const container = byId("pipelineJobsMessage");
    if (panel) { panel.dataset.componentState = state; panel.setAttribute("aria-busy", state === "loading" ? "true" : "false"); }
    if (stateLabel) stateLabel.textContent = state === "ready" ? "Live evidence" : label(state);
    if (container) { container.dataset.state = state; const icon = container.querySelector(":scope > span"); const heading = container.querySelector("strong"); const paragraph = container.querySelector("p"); if (icon) icon.textContent = symbol; if (heading) heading.textContent = title; if (paragraph) paragraph.textContent = message; }
  };
  const placeholder = (title, message) => `<div class="pipeline-jobs-placeholder"><strong>${escapeHtml(title)}</strong><p>${escapeHtml(message)}</p></div>`;
  const currentContract = () => latestPayload ? inspect(latestPayload) : Object.freeze({ workflows: [] });
  const selectedWorkflow = (contract) => contract.workflows.find((workflow) => workflow.workflowId === selectedWorkflowId) || contract.workflows[0] || null;
  const jobMatches = (job) => {
    const statusMatches = activeStatus === "all" || job.status === activeStatus;
    const query = searchQuery.trim().toLowerCase();
    return statusMatches && (!query || [job.jobId, job.stageId, job.jobType, job.assignedWorkerId].some((value) => String(value).toLowerCase().includes(query)));
  };
  const renderDetail = (job) => {
    const detail = byId("pipelineJobDetail"); if (!detail) return false;
    const attempts = job.maximumAttempts ? `${job.attempt} of ${job.maximumAttempts}` : String(job.attempt);
    const retry = job.retryExhausted ? "Exhausted" : job.retryScheduled ? "Scheduled" : "Not scheduled";
    detail.innerHTML = `
      <header class="pipeline-job-detail-head"><div><span>Selected job</span><strong>${escapeHtml(job.jobId)}</strong></div><span class="pipeline-job-status" data-status="${escapeHtml(job.status)}">${escapeHtml(label(job.status))}</span></header>
      <div class="pipeline-job-facts">
        <article><span>Stage</span><strong>${escapeHtml(label(job.stageId))}</strong></article><article><span>Job type</span><strong>${escapeHtml(label(job.jobType))}</strong></article><article><span>Priority</span><strong>${escapeHtml(job.priority)}</strong></article>
        <article><span>Attempt</span><strong>${escapeHtml(attempts)}</strong></article><article><span>Retry</span><strong>${escapeHtml(retry)}</strong></article><article><span>Worker</span><strong>${escapeHtml(job.assignedWorkerId)}</strong></article>
        <article><span>Created</span><strong>${escapeHtml(timestamp(job.createdAt))}</strong></article><article><span>Started</span><strong>${escapeHtml(timestamp(job.startedAt))}</strong></article><article><span>Updated</span><strong>${escapeHtml(timestamp(job.updatedAt))}</strong></article>
        <article><span>Completed</span><strong>${escapeHtml(timestamp(job.completedAt))}</strong></article><article><span>Dispatch result</span><strong>${job.dispatchResultAvailable ? "Available" : "Unavailable"}</strong></article><article><span>Events</span><strong>${escapeHtml(job.eventCount)}</strong></article>
      </div>
      <div class="pipeline-job-progress"><span>${escapeHtml(job.progressMessage)} · ${escapeHtml(Math.round(job.progressPercent))}%</span><div><i style="width:${escapeHtml(job.progressPercent)}%"></i></div></div>
      ${job.errorMessage ? `<div class="pipeline-job-error"><strong>Terminal error:</strong> ${escapeHtml(job.errorMessage)}</div>` : ""}
    `;
    return true;
  };
  const populateWorkflowSelector = (workflows) => {
    const select = byId("pipelineJobsWorkflow"); if (!select) return false;
    if (!workflows.length) { select.innerHTML = '<option value="">No workflows</option>'; select.disabled = true; selectedWorkflowId = ""; return false; }
    if (!workflows.some((workflow) => workflow.workflowId === selectedWorkflowId)) selectedWorkflowId = workflows[0].workflowId;
    select.disabled = false;
    select.innerHTML = workflows.map((workflow) => `<option value="${escapeHtml(workflow.workflowId)}"${workflow.workflowId === selectedWorkflowId ? " selected" : ""}>${escapeHtml(workflow.workflowId)} · ${workflow.jobs.length} job${workflow.jobs.length === 1 ? "" : "s"}</option>`).join("");
    return true;
  };
  const renderJobs = () => {
    const contract = currentContract(); const directory = byId("pipelineJobsDirectory"); const detail = byId("pipelineJobDetail"); const count = byId("pipelineJobsCount");
    if (!directory) return false;
    populateWorkflowSelector(contract.workflows);
    const workflow = selectedWorkflow(contract);
    if (!workflow) {
      directory.innerHTML = placeholder("No persisted workflows", "Job evidence will appear after workflow activation."); directory.setAttribute("aria-busy", "false");
      if (detail) detail.innerHTML = placeholder("No job selected", "No workflow is available for inspection."); if (count) count.textContent = "0";
      updateMessage("empty", "No workflow job evidence", "Connected Domain has no persisted workflow to inspect.", "◎"); return true;
    }
    const filtered = workflow.jobs.filter(jobMatches); if (count) count.textContent = `${filtered.length} of ${workflow.jobs.length}`;
    if (!filtered.length) {
      selectedJobId = "";
      directory.innerHTML = placeholder(workflow.jobs.length ? "No jobs match" : "No jobs projected", workflow.jobs.length ? "Change the status filter or job search." : "This workflow exists, but no Universal Job has been created for it.");
      directory.setAttribute("aria-busy", "false"); if (detail) detail.innerHTML = placeholder("No job selected", workflow.jobs.length ? "No filtered job is available." : "Attempt evidence will appear after a job is created.");
      updateMessage(workflow.jobs.length ? "ready" : "empty", workflow.jobs.length ? "No matching job" : "No jobs for selected workflow", workflow.jobs.length ? "The component is connected; adjust the local filters." : "The empty state is canonical and no activity was invented.", workflow.jobs.length ? "⌕" : "◎"); return true;
    }
    if (!filtered.some((job) => job.jobId === selectedJobId)) selectedJobId = filtered[0].jobId;
    directory.innerHTML = filtered.map((job) => `<button class="pipeline-job-row${job.jobId === selectedJobId ? " active" : ""}" type="button" role="option" aria-selected="${job.jobId === selectedJobId ? "true" : "false"}" data-jobs-attempts-id="${escapeHtml(job.jobId)}"><span class="pipeline-job-row-head"><strong>${escapeHtml(job.jobId)}</strong><span class="pipeline-job-status" data-status="${escapeHtml(job.status)}">${escapeHtml(label(job.status))}</span></span><span class="pipeline-job-row-meta"><span>${escapeHtml(label(job.stageId))} · Attempt ${escapeHtml(job.attempt)}</span><span>${escapeHtml(job.assignedWorkerId)}</span></span></button>`).join("");
    directory.setAttribute("aria-busy", "false"); renderDetail(filtered.find((job) => job.jobId === selectedJobId));
    updateMessage("ready", "Job evidence loaded", `${workflow.jobs.length} Universal Job${workflow.jobs.length === 1 ? "" : "s"} projected for the selected workflow.`, "✓"); return true;
  };
  const ensureBound = () => {
    if (bound) return true; const panel = byId("pipelineOperationsViewJobsAttempts"); const workflow = byId("pipelineJobsWorkflow"); const status = byId("pipelineJobsStatus"); const search = byId("pipelineJobsSearch");
    if (!panel || !workflow || !status || !search) return false;
    panel.addEventListener("click", (event) => { const row = event.target.closest("[data-jobs-attempts-id]"); if (!row) return; selectedJobId = row.dataset.jobsAttemptsId || ""; renderJobs(); });
    workflow.addEventListener("change", () => { selectedWorkflowId = String(workflow.value || ""); selectedJobId = ""; renderJobs(); });
    status.addEventListener("change", () => { activeStatus = String(status.value || "all").toLowerCase(); selectedJobId = ""; renderJobs(); });
    search.addEventListener("input", () => { searchQuery = String(search.value || ""); selectedJobId = ""; renderJobs(); });
    bound = true; return true;
  };
  const render = (payload) => { try { inspect(payload); latestPayload = payload; ensureBound(); return renderJobs(); } catch (error) { return renderUnavailable(error?.message); } };
  const renderUnavailable = (message) => {
    latestPayload = null; const directory = byId("pipelineJobsDirectory"); const detail = byId("pipelineJobDetail"); const count = byId("pipelineJobsCount"); const select = byId("pipelineJobsWorkflow");
    if (select) { select.innerHTML = '<option value="">Unavailable</option>'; select.disabled = true; }
    if (directory) { directory.innerHTML = placeholder("Job evidence unavailable", message || "The canonical projection could not be loaded."); directory.setAttribute("aria-busy", "false"); }
    if (detail) detail.innerHTML = placeholder("No job detail", "Restore the read-only projection before inspecting attempts."); if (count) count.textContent = "Unavailable";
    updateMessage("unavailable", "Jobs and attempts unavailable", message || "The canonical detail projection could not be loaded.", "!"); return false;
  };
  const activate = () => { ensureBound(); const snapshot = window.LinkCraftorConnectedDomainOverview?.getSnapshot?.(); if (snapshot) return render(snapshot); updateMessage("loading", "Loading jobs and attempts", "Waiting for the existing Connected Domain detail snapshot.", "◌"); return false; };
  window.LinkCraftorConnectedDomainJobsAttempts = Object.freeze({ activate, render, renderUnavailable, inspect });
})();
// END PART F 15-B4G JOBS AND ATTEMPTS COMPONENT
// BEGIN PART F 15-B4H DEPENDENCIES AND HANDOFFS COMPONENT
(() => {
  "use strict";
  const PIPELINE_ID = "connect_domain";
  const EXPECTED_ORDER = Object.freeze(["connect_domain", "site_sources", "url_cleaner", "site_pages", "live_domain_target_pool", "active_target_set"]);
  let latestPayload = null;
  let selectedWorkflowId = "";
  let bound = false;
  const byId = (id) => document.getElementById(id);
  const escapeHtml = (value) => String(value ?? "").replaceAll("&", "&amp;").replaceAll("<", "&lt;").replaceAll(">", "&gt;").replaceAll('"', "&quot;").replaceAll("'", "&#039;");
  const label = (value) => String(value || "unknown").split(/[_-]+/).filter(Boolean).map((part) => part.charAt(0).toUpperCase() + part.slice(1)).join(" ");
  const array = (value) => Array.isArray(value) ? value.map(String) : [];
  const inspect = (payload) => {
    if (!payload || payload.pipeline_id !== PIPELINE_ID) throw new Error("Dependencies & Handoffs received an invalid pipeline identity.");
    const order = array(payload.stage_order);
    if (order.length !== EXPECTED_ORDER.length || !order.every((stage, index) => stage === EXPECTED_ORDER[index])) throw new Error("Dependencies & Handoffs requires the canonical six-stage order.");
    if (!Array.isArray(payload.workflows)) throw new Error("Dependencies & Handoffs requires persisted workflow evidence.");
    const workflows = payload.workflows.map((workflow) => {
      const workflowId = String(workflow?.workflow_id || "").trim();
      if (!workflowId) throw new Error("Dependencies & Handoffs received an empty workflow identity.");
      if (!Array.isArray(workflow?.stages) || workflow.stages.length !== 6) throw new Error("A workflow does not contain six stage projections.");
      const stages = workflow.stages.map((stage, index) => {
        const stageId = String(stage?.stage_id || "");
        if (stageId !== order[index]) throw new Error("Workflow stage evidence does not preserve canonical order.");
        return Object.freeze({
          stageId, status: String(stage?.status || "pending").toLowerCase(), predecessors: array(stage?.predecessor_stages), successors: array(stage?.successor_stages),
          persistent: stage?.persistent_registration === true, jobCount: Number.isFinite(Number(stage?.job_count)) ? Math.max(0, Math.trunc(Number(stage.job_count))) : 0,
          outputReady: stage?.output_ready === true
        });
      });
      for (let index = 0; index < stages.length; index += 1) {
        const expectedPredecessors = index ? [order[index - 1]] : [];
        const expectedSuccessors = index < order.length - 1 ? [order[index + 1]] : [];
        if (stages[index].predecessors.join("|") !== expectedPredecessors.join("|") || stages[index].successors.join("|") !== expectedSuccessors.join("|")) throw new Error("Persisted dependency declarations do not match the canonical chain.");
      }
      return Object.freeze({ workflowId, status: String(workflow?.status || "unknown").toLowerCase(), currentStage: String(workflow?.current_stage || ""), stages });
    });
    return Object.freeze({ order, workflows });
  };
  const updateMessage = (state, title, message, symbol) => {
    const panel = byId("pipelineOperationsViewDependenciesHandoffs"); const stateLabel = byId("pipelineHandoffsState"); const container = byId("pipelineHandoffsMessage");
    if (panel) { panel.dataset.componentState = state; panel.setAttribute("aria-busy", state === "loading" ? "true" : "false"); }
    if (stateLabel) stateLabel.textContent = state === "ready" ? "Contract verified" : label(state);
    if (container) { container.dataset.state = state; const icon = container.querySelector(":scope > span"); const heading = container.querySelector("strong"); const paragraph = container.querySelector("p"); if (icon) icon.textContent = symbol; if (heading) heading.textContent = title; if (paragraph) paragraph.textContent = message; }
  };
  const selectedWorkflow = (contract) => contract.workflows.find((workflow) => workflow.workflowId === selectedWorkflowId) || contract.workflows[0] || null;
  const stageRuntimeState = (stage, workflow) => {
    if (stage.status === "failed") return "failed";
    if (stage.status === "completed") return "completed";
    if (workflow.currentStage === stage.stageId) return "current";
    return stage.status || "pending";
  };
  const handoffState = (upstream, downstream, workflow) => {
    const upstreamState = stageRuntimeState(upstream, workflow); const downstreamState = stageRuntimeState(downstream, workflow);
    if (upstreamState === "failed" || downstreamState === "failed") return "blocked";
    if (upstreamState === "completed" && upstream.outputReady) return "delivered";
    if (upstreamState === "completed") return "awaiting_output";
    if (upstreamState === "current") return "active";
    return "waiting";
  };
  const gateMessage = (state) => ({ delivered: "Result evidence available for successor hydration.", awaiting_output: "Stage completed; dispatch-result evidence is not yet available.", active: "Upstream stage is currently active.", blocked: "Failure evidence blocks this handoff.", waiting: "Waiting for upstream stage completion." }[state] || "Not evaluated.");
  const populateWorkflowSelector = (workflows) => {
    const select = byId("pipelineHandoffsWorkflow"); if (!select) return false;
    if (!workflows.length) { select.innerHTML = '<option value="">No workflows</option>'; select.disabled = true; selectedWorkflowId = ""; return false; }
    if (!workflows.some((workflow) => workflow.workflowId === selectedWorkflowId)) selectedWorkflowId = workflows[0].workflowId;
    select.disabled = false; select.innerHTML = workflows.map((workflow) => `<option value="${escapeHtml(workflow.workflowId)}"${workflow.workflowId === selectedWorkflowId ? " selected" : ""}>${escapeHtml(workflow.workflowId)} · ${escapeHtml(label(workflow.status))}</option>`).join(""); return true;
  };
  const renderContract = (contract, workflow) => {
    const container = byId("pipelineHandoffsContract"); const current = byId("pipelineHandoffsCurrent"); const stageCount = byId("pipelineHandoffsStageCount"); const gateCount = byId("pipelineHandoffsGateCount");
    if (!container) return false;
    const gates = workflow.stages.slice(0, -1).map((upstream, index) => ({ upstream, downstream: workflow.stages[index + 1], state: handoffState(upstream, workflow.stages[index + 1], workflow) }));
    container.innerHTML = gates.map((gate, index) => `
      <article class="pipeline-handoff-gate" data-gate-state="${escapeHtml(gate.state)}">
        <div class="pipeline-handoff-stage"><span>Upstream · ${String(index + 1).padStart(2, "0")}</span><strong>${escapeHtml(label(gate.upstream.stageId))}</strong><small>${escapeHtml(label(stageRuntimeState(gate.upstream, workflow)))} · ${gate.upstream.jobCount} job${gate.upstream.jobCount === 1 ? "" : "s"}</small></div>
        <div class="pipeline-handoff-arrow"><b aria-hidden="true">→</b><em>${escapeHtml(label(gate.state))}</em></div>
        <div class="pipeline-handoff-stage"><span>Successor · ${String(index + 2).padStart(2, "0")}</span><strong>${escapeHtml(label(gate.downstream.stageId))}</strong><small>${escapeHtml(label(stageRuntimeState(gate.downstream, workflow)))} · persistent ${gate.downstream.persistent ? "yes" : "no"}</small></div>
        <div class="pipeline-handoff-evidence"><span>Gate evidence</span><strong>${gate.upstream.outputReady ? "Dispatch result available" : "Dispatch result unavailable"}</strong><small>${escapeHtml(gateMessage(gate.state))}</small></div>
      </article>
    `).join("");
    container.setAttribute("aria-busy", "false"); if (current) current.textContent = workflow.currentStage ? label(workflow.currentStage) : label(workflow.status); if (stageCount) stageCount.textContent = String(contract.order.length); if (gateCount) gateCount.textContent = String(gates.length);
    const blocked = gates.filter((gate) => gate.state === "blocked").length; const delivered = gates.filter((gate) => gate.state === "delivered").length; const active = gates.filter((gate) => gate.state === "active").length;
    updateMessage("ready", "Dependency contract verified", `${gates.length} canonical handoffs · ${delivered} delivered · ${active} active · ${blocked} blocked.`, "✓"); return true;
  };
  const render = (payload) => {
    try {
      const contract = inspect(payload); latestPayload = payload; ensureBound(); populateWorkflowSelector(contract.workflows); const workflow = selectedWorkflow(contract); const container = byId("pipelineHandoffsContract");
      if (!workflow) { if (container) { container.innerHTML = '<div class="pipeline-handoffs-placeholder"><strong>No persisted workflows</strong><p>Dependency evidence will appear after workflow activation.</p></div>'; container.setAttribute("aria-busy", "false"); } updateMessage("empty", "No workflow handoff evidence", "The six-stage contract exists, but no workflow is available to evaluate.", "◎"); return true; }
      return renderContract(contract, workflow);
    } catch (error) { return renderUnavailable(error?.message); }
  };
  const renderUnavailable = (message) => {
    latestPayload = null; const container = byId("pipelineHandoffsContract"); const select = byId("pipelineHandoffsWorkflow");
    if (select) { select.innerHTML = '<option value="">Unavailable</option>'; select.disabled = true; }
    if (container) { container.innerHTML = `<div class="pipeline-handoffs-placeholder"><strong>Dependency evidence unavailable</strong><p>${escapeHtml(message || "The canonical projection could not be loaded.")}</p></div>`; container.setAttribute("aria-busy", "false"); }
    updateMessage("unavailable", "Dependencies and handoffs unavailable", message || "The canonical detail projection could not be loaded.", "!"); return false;
  };
  const ensureBound = () => { if (bound) return true; const select = byId("pipelineHandoffsWorkflow"); if (!select) return false; select.addEventListener("change", () => { selectedWorkflowId = String(select.value || ""); if (latestPayload) render(latestPayload); }); bound = true; return true; };
  const activate = () => { ensureBound(); const snapshot = window.LinkCraftorConnectedDomainOverview?.getSnapshot?.(); if (snapshot) return render(snapshot); updateMessage("loading", "Loading handoff evidence", "Waiting for the existing Connected Domain detail snapshot.", "◌"); return false; };
  window.LinkCraftorConnectedDomainDependenciesHandoffs = Object.freeze({ activate, render, renderUnavailable, inspect });
})();
// END PART F 15-B4H DEPENDENCIES AND HANDOFFS COMPONENT
// BEGIN PART F 15-B4I EVENTS TIMELINE COMPONENT
(() => {
  "use strict";
  const PIPELINE_ID = "connect_domain";
  let latestPayload = null;
  let selectedWorkflowId = "";
  let activeCategory = "all";
  let activeOrder = "newest";
  let searchQuery = "";
  let bound = false;
  const byId = (id) => document.getElementById(id);
  const escapeHtml = (value) => String(value ?? "").replaceAll("&", "&amp;").replaceAll("<", "&lt;").replaceAll(">", "&gt;").replaceAll('"', "&quot;").replaceAll("'", "&#039;");
  const label = (value) => String(value || "unknown").split(/[_-]+/).filter(Boolean).map((part) => part.charAt(0).toUpperCase() + part.slice(1)).join(" ");
  const array = (value) => Array.isArray(value) ? value : [];
  const recordedTime = (event) => event?.created_at ?? event?.timestamp ?? event?.occurred_at ?? event?.updated_at ?? null;
  const timeValue = (value) => { if (!value) return null; const parsed = new Date(value).getTime(); return Number.isNaN(parsed) ? null : parsed; };
  const timestamp = (value) => { if (!value) return "Timestamp unavailable"; const date = new Date(value); return Number.isNaN(date.getTime()) ? String(value) : date.toLocaleString(); };
  const metadataText = (event) => { try { return JSON.stringify(event?.metadata ?? {}); } catch (_error) { return ""; } };
  const eventType = (event) => String(event?.event_type ?? event?.type ?? event?.kind ?? event?.name ?? event?.metadata?.event_type ?? ((event?.old_status != null || event?.new_status != null) ? "status_transition" : "job_event"));
  const eventCategory = (event, type) => {
    const detailText = `${type} ${event?.severity ?? ""} ${event?.level ?? ""} ${event?.message ?? ""} ${event?.error_message ?? ""} ${metadataText(event)}`.toLowerCase();
    if (String(event?.new_status ?? "").toLowerCase() === "failed" || detailText.includes("failure") || detailText.includes("error") || detailText.includes("exception")) return "failure";
    if (detailText.includes("retry") || detailText.includes("attempt")) return "retry";
    if (detailText.includes("dispatch") || detailText.includes("handler") || detailText.includes("queue")) return "dispatch";
    if (event?.old_status != null || event?.new_status != null || detailText.includes("status")) return "transition";
    return "other";
  };
  const eventMessage = (event, type) => {
    const explicit = event?.message ?? event?.detail ?? event?.reason ?? event?.error_message ?? event?.metadata?.message ?? event?.metadata?.detail ?? event?.metadata?.reason ?? event?.metadata?.error_message;
    if (explicit != null && String(explicit).trim()) return String(explicit);
    if (event?.old_status != null || event?.new_status != null) return `${label(event?.old_status || "unknown")} → ${label(event?.new_status || "unknown")}`;
    return `${label(type)} recorded by the canonical Runtime event store.`;
  };
  const normalizeEvent = (event, context) => {
    if (!event || typeof event !== "object" || Array.isArray(event)) throw new Error("Events Timeline received a non-object event record.");
    const type = eventType(event); const time = recordedTime(event);
    return Object.freeze({
      key: String(event?.event_id || `${context.jobId}:${context.sequence}`), eventId: String(event?.event_id || "Identity unavailable"), jobId: context.jobId, stageId: context.stageId, eventIndex: context.eventIndex, sequence: context.sequence,
      type, category: eventCategory(event, type), message: eventMessage(event, type), time, timeValue: timeValue(time),
      oldStatus: event?.old_status != null ? String(event.old_status) : "", newStatus: event?.new_status != null ? String(event.new_status) : "",
      severity: String(event?.severity ?? event?.level ?? "recorded"), metadataText: metadataText(event), fieldCount: Object.keys(event).length, metadataFieldCount: event?.metadata && typeof event.metadata === "object" && !Array.isArray(event.metadata) ? Object.keys(event.metadata).length : 0
    });
  };
  const inspect = (payload) => {
    if (!payload || payload.pipeline_id !== PIPELINE_ID) throw new Error("Events Timeline received an invalid pipeline identity.");
    if (!Array.isArray(payload.workflows)) throw new Error("Events Timeline requires persisted workflow evidence.");
    const workflows = payload.workflows.map((workflow) => {
      const workflowId = String(workflow?.workflow_id || "").trim(); if (!workflowId) throw new Error("Events Timeline received an empty workflow identity.");
      let sequence = 0;
      const events = array(workflow?.stages).flatMap((stage) => array(stage?.jobs).flatMap((job) => {
        const jobId = String(job?.job_id || "").trim(); if (!jobId) throw new Error("An event-bearing job has an empty job identity.");
        return array(job?.events).map((event, eventIndex) => normalizeEvent(event, { jobId, stageId: String(stage?.stage_id || "unknown"), eventIndex, sequence: sequence++ }));
      }));
      return Object.freeze({ workflowId, status: String(workflow?.status || "unknown").toLowerCase(), events });
    });
    return Object.freeze({ workflows });
  };
  const updateMessage = (state, title, message, symbol) => {
    const panel = byId("pipelineOperationsViewEventsTimeline"); const stateLabel = byId("pipelineEventsState"); const container = byId("pipelineEventsMessage");
    if (panel) { panel.dataset.componentState = state; panel.setAttribute("aria-busy", state === "loading" ? "true" : "false"); }
    if (stateLabel) stateLabel.textContent = state === "ready" ? "Recorded evidence" : label(state);
    if (container) { container.dataset.state = state; const icon = container.querySelector(":scope > span"); const heading = container.querySelector("strong"); const paragraph = container.querySelector("p"); if (icon) icon.textContent = symbol; if (heading) heading.textContent = title; if (paragraph) paragraph.textContent = message; }
  };
  const placeholder = (title, message) => `<div class="pipeline-events-placeholder"><strong>${escapeHtml(title)}</strong><p>${escapeHtml(message)}</p></div>`;
  const populateWorkflowSelector = (workflows) => {
    const select = byId("pipelineEventsWorkflow"); if (!select) return false;
    if (!workflows.length) { select.innerHTML = '<option value="">No workflows</option>'; select.disabled = true; selectedWorkflowId = ""; return false; }
    if (!workflows.some((workflow) => workflow.workflowId === selectedWorkflowId)) selectedWorkflowId = workflows[0].workflowId;
    select.disabled = false; select.innerHTML = workflows.map((workflow) => `<option value="${escapeHtml(workflow.workflowId)}"${workflow.workflowId === selectedWorkflowId ? " selected" : ""}>${escapeHtml(workflow.workflowId)} · ${workflow.events.length} event${workflow.events.length === 1 ? "" : "s"}</option>`).join(""); return true;
  };
  const selectedWorkflow = (contract) => contract.workflows.find((workflow) => workflow.workflowId === selectedWorkflowId) || contract.workflows[0] || null;
  const eventMatches = (event) => {
    const categoryMatches = activeCategory === "all" || event.category === activeCategory; const query = searchQuery.trim().toLowerCase();
    return categoryMatches && (!query || [event.eventId, event.type, event.message, event.jobId, event.stageId, event.oldStatus, event.newStatus, event.severity, event.metadataText].some((value) => String(value).toLowerCase().includes(query)));
  };
  const sortEvents = (events) => [...events].sort((left, right) => {
    const leftTime = left.timeValue; const rightTime = right.timeValue;
    if (leftTime == null && rightTime == null) return left.sequence - right.sequence;
    if (leftTime == null) return 1; if (rightTime == null) return -1;
    const difference = activeOrder === "oldest" ? leftTime - rightTime : rightTime - leftTime;
    return difference || left.sequence - right.sequence;
  });
  const renderEvents = () => {
    const contract = latestPayload ? inspect(latestPayload) : Object.freeze({ workflows: [] }); const timeline = byId("pipelineEventsTimeline"); const count = byId("pipelineEventsCount"); if (!timeline) return false;
    populateWorkflowSelector(contract.workflows); const workflow = selectedWorkflow(contract);
    if (!workflow) { timeline.innerHTML = placeholder("No persisted workflows", "Event evidence will appear after workflow activation."); timeline.setAttribute("aria-busy", "false"); if (count) count.textContent = "0"; updateMessage("empty", "No workflow event evidence", "No persisted workflow is available for event inspection.", "◎"); return true; }
    const visible = sortEvents(workflow.events.filter(eventMatches)); if (count) count.textContent = `${visible.length} of ${workflow.events.length}`;
    if (!visible.length) {
      timeline.innerHTML = placeholder(workflow.events.length ? "No events match" : "No recorded events", workflow.events.length ? "Change the category filter or evidence search." : "This workflow has no projected job events; no timeline activity was invented."); timeline.setAttribute("aria-busy", "false");
      updateMessage(workflow.events.length ? "ready" : "empty", workflow.events.length ? "No matching event" : "No events for selected workflow", workflow.events.length ? "The timeline is connected; adjust the local filters." : "The canonical event collection is empty.", workflow.events.length ? "⌕" : "◎"); return true;
    }
    timeline.innerHTML = visible.map((event) => `
      <article class="pipeline-event-entry" data-category="${escapeHtml(event.category)}">
        <div class="pipeline-event-time"><span>Recorded occurrence</span><strong>${escapeHtml(timestamp(event.time))}</strong><p>${event.time ? "Canonical event timestamp" : "No timestamp was inferred"}</p></div>
        <div class="pipeline-event-content"><span>${escapeHtml(label(event.category))}</span><strong>${escapeHtml(label(event.type))}</strong><p>${escapeHtml(event.message)}</p>${event.oldStatus || event.newStatus ? `<div class="pipeline-event-transition"><b>${escapeHtml(label(event.oldStatus || "unknown"))}</b><span>→</span><b>${escapeHtml(label(event.newStatus || "unknown"))}</b></div>` : ""}</div>
        <div class="pipeline-event-context"><span>Runtime context</span><strong>${escapeHtml(label(event.stageId))}</strong><p>${escapeHtml(event.eventId)} · ${escapeHtml(event.jobId)} · ${escapeHtml(label(event.severity))} · ${event.fieldCount} event fields · ${event.metadataFieldCount} metadata fields</p></div>
      </article>
    `).join(""); timeline.setAttribute("aria-busy", "false"); updateMessage("ready", "Recorded event evidence loaded", `${workflow.events.length} canonical job event${workflow.events.length === 1 ? "" : "s"} available for inspection.`, "✓"); return true;
  };
  const ensureBound = () => {
    if (bound) return true; const workflow = byId("pipelineEventsWorkflow"); const category = byId("pipelineEventsCategory"); const order = byId("pipelineEventsOrder"); const search = byId("pipelineEventsSearch");
    if (!workflow || !category || !order || !search) return false;
    workflow.addEventListener("change", () => { selectedWorkflowId = String(workflow.value || ""); renderEvents(); });
    category.addEventListener("change", () => { activeCategory = String(category.value || "all"); renderEvents(); });
    order.addEventListener("change", () => { activeOrder = String(order.value || "newest"); renderEvents(); });
    search.addEventListener("input", () => { searchQuery = String(search.value || ""); renderEvents(); });
    bound = true; return true;
  };
  const render = (payload) => { try { inspect(payload); latestPayload = payload; ensureBound(); return renderEvents(); } catch (error) { return renderUnavailable(error?.message); } };
  const renderUnavailable = (message) => {
    latestPayload = null; const timeline = byId("pipelineEventsTimeline"); const select = byId("pipelineEventsWorkflow"); const count = byId("pipelineEventsCount");
    if (select) { select.innerHTML = '<option value="">Unavailable</option>'; select.disabled = true; }
    if (timeline) { timeline.innerHTML = placeholder("Event evidence unavailable", message || "The canonical projection could not be loaded."); timeline.setAttribute("aria-busy", "false"); }
    if (count) count.textContent = "Unavailable"; updateMessage("unavailable", "Events Timeline unavailable", message || "The canonical detail projection could not be loaded.", "!"); return false;
  };
  const activate = () => { ensureBound(); const snapshot = window.LinkCraftorConnectedDomainOverview?.getSnapshot?.(); if (snapshot) return render(snapshot); updateMessage("loading", "Loading event evidence", "Waiting for the existing Connected Domain detail snapshot.", "◌"); return false; };
  window.LinkCraftorConnectedDomainEventsTimeline = Object.freeze({ activate, render, renderUnavailable, inspect });
})();
// END PART F 15-B4I EVENTS TIMELINE COMPONENT
// BEGIN PART F 15-B4J FAILURES AND ATTENTION COMPONENT
(() => {
  "use strict";
  const PIPELINE_ID = "connect_domain";
  let latestPayload = null;
  let selectedWorkflowId = "all";
  let selectedAttentionId = "";
  let activeScope = "all";
  let searchQuery = "";
  let bound = false;
  const byId = (id) => document.getElementById(id);
  const escapeHtml = (value) => String(value ?? "").replaceAll("&", "&amp;").replaceAll("<", "&lt;").replaceAll(">", "&gt;").replaceAll('"', "&quot;").replaceAll("'", "&#039;");
  const label = (value) => String(value || "unknown").split(/[_-]+/).filter(Boolean).map((part) => part.charAt(0).toUpperCase() + part.slice(1)).join(" ");
  const array = (value) => Array.isArray(value) ? value : [];
  const integer = (value) => { const number = Number(value); return Number.isFinite(number) && number >= 0 ? Math.trunc(number) : 0; };
  const timestamp = (value) => { if (!value) return "Unavailable"; const date = new Date(value); return Number.isNaN(date.getTime()) ? String(value) : date.toLocaleString(); };
  const timeValue = (value) => { if (!value) return null; const parsed = new Date(value).getTime(); return Number.isNaN(parsed) ? null : parsed; };
  const eventLine = (event, index) => {
    if (!event || typeof event !== "object" || Array.isArray(event)) return null;
    const oldStatus = event?.old_status != null ? label(event.old_status) : "Unknown";
    const newStatus = event?.new_status != null ? label(event.new_status) : label(event?.event_type || event?.type || "Recorded event");
    const recordedAt = event?.created_at ?? event?.timestamp ?? event?.occurred_at ?? event?.updated_at ?? null;
    return Object.freeze({ id: String(event?.event_id || `event-${index + 1}`), transition: `${oldStatus} → ${newStatus}`, recordedAt });
  };
  const normalizeJob = (job, stageId, workflowId) => {
    const jobId = String(job?.job_id || "").trim();
    if (!jobId) throw new Error("Failures & Attention received an empty job identity.");
    return Object.freeze({
      jobId, workflowId, stageId, jobType: String(job?.job_type || "Unavailable"), status: String(job?.status || "unknown").toLowerCase(),
      errorMessage: job?.error_message ? String(job.error_message) : "", attempt: integer(job?.attempt), maximumAttempts: integer(job?.maximum_attempts),
      retryScheduled: job?.retry_scheduled === true, retryExhausted: job?.retry_exhausted === true, assignedWorkerId: String(job?.assigned_worker_id || "Unassigned"),
      createdAt: job?.created_at || null, updatedAt: job?.updated_at || null, completedAt: job?.completed_at || null,
      events: array(job?.events).map(eventLine).filter(Boolean)
    });
  };
  const jobAttention = (job) => {
    if (!(job.status === "failed" || job.errorMessage || job.retryScheduled || job.retryExhausted)) return null;
    const kind = job.retryExhausted ? "retry_exhausted" : job.status === "failed" ? "failed_job" : job.errorMessage ? "terminal_error" : "retry_scheduled";
    const severity = job.retryScheduled && !job.retryExhausted && job.status !== "failed" && !job.errorMessage ? "warning" : "critical";
    const title = kind === "retry_exhausted" ? "Retry limit exhausted" : kind === "failed_job" ? "Universal Job failed" : kind === "terminal_error" ? "Terminal error recorded" : "Retry scheduled";
    const message = job.errorMessage || (kind === "retry_exhausted" ? "The recorded attempt limit has been exhausted." : kind === "retry_scheduled" ? "A retry is recorded as scheduled; execution remains outside this view." : "The job is in a failed terminal state.");
    return Object.freeze({ attentionId: `job:${job.jobId}`, source: "job", kind, severity, title, message, workflowId: job.workflowId, stageId: job.stageId, jobId: job.jobId, jobType: job.jobType, status: job.status, attempt: job.attempt, maximumAttempts: job.maximumAttempts, retryScheduled: job.retryScheduled, retryExhausted: job.retryExhausted, assignedWorkerId: job.assignedWorkerId, recordedAt: job.updatedAt || job.completedAt || job.createdAt, events: job.events });
  };
  const inspect = (payload) => {
    if (!payload || payload.pipeline_id !== PIPELINE_ID) throw new Error("Failures & Attention received an invalid pipeline identity.");
    if (!Array.isArray(payload.workflows)) throw new Error("Failures & Attention requires persisted workflow evidence.");
    const workflows = payload.workflows.map((workflow) => {
      const workflowId = String(workflow?.workflow_id || "").trim(); if (!workflowId) throw new Error("Failures & Attention received an empty workflow identity.");
      const status = String(workflow?.status || "unknown").toLowerCase(); const failedStages = array(workflow?.failed_stages).map((stage) => String(stage));
      const jobs = array(workflow?.stages).flatMap((stage) => array(stage?.jobs).map((job) => normalizeJob(job, String(stage?.stage_id || "unknown"), workflowId)));
      const items = jobs.map(jobAttention).filter(Boolean); const coveredStages = new Set(items.map((item) => item.stageId));
      failedStages.filter((stageId) => !coveredStages.has(stageId)).forEach((stageId) => items.push(Object.freeze({ attentionId: `stage:${workflowId}:${stageId}`, source: "stage", kind: "failed_stage", severity: "critical", title: "Workflow stage failed", message: "The persisted workflow records this stage as failed without a projected failed job.", workflowId, stageId, jobId: "Unavailable", jobType: "Unavailable", status: "failed", attempt: 0, maximumAttempts: 0, retryScheduled: false, retryExhausted: false, assignedWorkerId: "Unassigned", recordedAt: workflow?.updated_at || null, events: [] })));
      if (status === "failed" && !items.length) items.push(Object.freeze({ attentionId: `workflow:${workflowId}`, source: "workflow", kind: "failed_workflow", severity: "critical", title: "Workflow failed", message: "The persisted workflow is failed without a more specific projected job or stage concern.", workflowId, stageId: String(workflow?.current_stage || "Unavailable"), jobId: "Unavailable", jobType: "Unavailable", status, attempt: 0, maximumAttempts: 0, retryScheduled: false, retryExhausted: false, assignedWorkerId: "Unassigned", recordedAt: workflow?.updated_at || null, events: [] }));
      return Object.freeze({ workflowId, status, failedStages, jobs, items });
    });
    const jobs = workflows.flatMap((workflow) => workflow.jobs); const items = workflows.flatMap((workflow) => workflow.items);
    return Object.freeze({ workflows, items, summary: Object.freeze({ failedWorkflows: workflows.filter((workflow) => workflow.status === "failed").length, failedStages: workflows.reduce((total, workflow) => total + workflow.failedStages.length, 0), failedJobs: jobs.filter((job) => job.status === "failed").length, retriesScheduled: jobs.filter((job) => job.retryScheduled).length, retriesExhausted: jobs.filter((job) => job.retryExhausted).length, terminalErrors: jobs.filter((job) => Boolean(job.errorMessage)).length }) });
  };
  const updateMessage = (state, title, message, symbol) => {
    const panel = byId("pipelineOperationsViewFailures"); const stateLabel = byId("pipelineFailuresState"); const container = byId("pipelineFailuresMessage");
    if (panel) { panel.dataset.componentState = state; panel.setAttribute("aria-busy", state === "loading" ? "true" : "false"); }
    if (stateLabel) stateLabel.textContent = state === "ready" ? "Attention evidence" : state === "empty" ? "All clear" : label(state);
    if (container) { container.dataset.state = state; const icon = container.querySelector(":scope > span"); const heading = container.querySelector("strong"); const paragraph = container.querySelector("p"); if (icon) icon.textContent = symbol; if (heading) heading.textContent = title; if (paragraph) paragraph.textContent = message; }
  };
  const placeholder = (title, message) => `<div class="pipeline-failures-placeholder"><strong>${escapeHtml(title)}</strong><p>${escapeHtml(message)}</p></div>`;
  const setSummary = (summary) => {
    const bindings = { pipelineFailuresFailedWorkflows: summary.failedWorkflows, pipelineFailuresFailedStages: summary.failedStages, pipelineFailuresFailedJobs: summary.failedJobs, pipelineFailuresRetriesScheduled: summary.retriesScheduled, pipelineFailuresRetriesExhausted: summary.retriesExhausted, pipelineFailuresTerminalErrors: summary.terminalErrors };
    Object.entries(bindings).forEach(([id, value]) => { const node = byId(id); if (node) node.textContent = String(value); });
  };
  const populateWorkflowSelector = (contract) => {
    const select = byId("pipelineFailuresWorkflow"); if (!select) return false;
    const options = [`<option value="all"${selectedWorkflowId === "all" ? " selected" : ""}>All workflows · ${contract.items.length} concern${contract.items.length === 1 ? "" : "s"}</option>`, ...contract.workflows.map((workflow) => `<option value="${escapeHtml(workflow.workflowId)}"${workflow.workflowId === selectedWorkflowId ? " selected" : ""}>${escapeHtml(workflow.workflowId)} · ${workflow.items.length} concern${workflow.items.length === 1 ? "" : "s"}</option>` )];
    if (selectedWorkflowId !== "all" && !contract.workflows.some((workflow) => workflow.workflowId === selectedWorkflowId)) selectedWorkflowId = "all";
    select.innerHTML = options.join(""); select.disabled = false; return true;
  };
  const itemMatches = (item) => {
    const workflowMatches = selectedWorkflowId === "all" || item.workflowId === selectedWorkflowId;
    const scopeMatches = activeScope === "all" || (activeScope === "critical" && item.severity === "critical") || (activeScope === "retry" && ["retry_scheduled", "retry_exhausted"].includes(item.kind)) || (activeScope === "workflow_stage" && item.source !== "job");
    const query = searchQuery.trim().toLowerCase(); const searchMatches = !query || [item.title, item.message, item.workflowId, item.stageId, item.jobId, item.jobType, item.status, item.kind].some((value) => String(value).toLowerCase().includes(query));
    return workflowMatches && scopeMatches && searchMatches;
  };
  const sortItems = (items) => [...items].sort((left, right) => { const severity = Number(right.severity === "critical") - Number(left.severity === "critical"); if (severity) return severity; const leftTime = timeValue(left.recordedAt); const rightTime = timeValue(right.recordedAt); if (leftTime == null && rightTime == null) return left.attentionId.localeCompare(right.attentionId); if (leftTime == null) return 1; if (rightTime == null) return -1; return rightTime - leftTime; });
  const renderDetail = (item) => {
    const detail = byId("pipelineFailureDetail"); if (!detail) return false;
    const attempt = item.maximumAttempts ? `${item.attempt} of ${item.maximumAttempts}` : item.attempt ? String(item.attempt) : "Not recorded";
    const retry = item.retryExhausted ? "Exhausted" : item.retryScheduled ? "Scheduled" : "Not scheduled";
    const events = item.events.slice(-4).reverse();
    detail.innerHTML = `<header class="pipeline-failure-detail-head"><div><span>Selected concern</span><strong>${escapeHtml(item.title)}</strong></div><b class="pipeline-attention-badge" data-severity="${escapeHtml(item.severity)}">${escapeHtml(label(item.severity))}</b></header><div class="pipeline-failure-facts"><article><span>Workflow</span><strong>${escapeHtml(item.workflowId)}</strong></article><article><span>Stage</span><strong>${escapeHtml(label(item.stageId))}</strong></article><article><span>Job</span><strong>${escapeHtml(item.jobId)}</strong></article><article><span>Status</span><strong>${escapeHtml(label(item.status))}</strong></article><article><span>Attempt</span><strong>${escapeHtml(attempt)}</strong></article><article><span>Retry state</span><strong>${escapeHtml(retry)}</strong></article><article><span>Worker</span><strong>${escapeHtml(item.assignedWorkerId)}</strong></article><article><span>Recorded</span><strong>${escapeHtml(timestamp(item.recordedAt))}</strong></article><article><span>Evidence source</span><strong>${escapeHtml(label(item.source))}</strong></article></div><div class="pipeline-failure-error"><strong>Attention evidence:</strong> ${escapeHtml(item.message)}</div><div class="pipeline-failure-events"><strong>Recent recorded job events</strong>${events.length ? events.map((event) => `<div class="pipeline-failure-event"><b>${escapeHtml(timestamp(event.recordedAt))}</b><span>${escapeHtml(event.id)} · ${escapeHtml(event.transition)}</span></div>`).join("") : '<div class="pipeline-failure-event"><b>No projected events</b><span>No event evidence was invented.</span></div>'}</div>`;
    return true;
  };
  const renderFailures = () => {
    const contract = latestPayload ? inspect(latestPayload) : Object.freeze({ workflows: [], items: [], summary: { failedWorkflows: 0, failedStages: 0, failedJobs: 0, retriesScheduled: 0, retriesExhausted: 0, terminalErrors: 0 } });
    const directory = byId("pipelineFailuresDirectory"); const detail = byId("pipelineFailureDetail"); const count = byId("pipelineFailuresCount"); if (!directory) return false;
    setSummary(contract.summary); populateWorkflowSelector(contract); const visible = sortItems(contract.items.filter(itemMatches)); if (count) count.textContent = `${visible.length} of ${contract.items.length}`;
    if (!contract.items.length) { selectedAttentionId = ""; directory.innerHTML = placeholder("No failures require attention", "No failed workflow, failed stage, failed job, terminal error, or retry concern is present in the canonical snapshot."); directory.setAttribute("aria-busy", "false"); if (detail) detail.innerHTML = placeholder("All clear", "Owner-attention evidence is empty; no recovery action is required or exposed here."); updateMessage("empty", "No owner-attention items", "The canonical failure and retry evidence is clear.", "✓"); return true; }
    if (!visible.length) { selectedAttentionId = ""; directory.innerHTML = placeholder("No concerns match", "Change the workflow, attention-class filter, or evidence search."); directory.setAttribute("aria-busy", "false"); if (detail) detail.innerHTML = placeholder("No concern selected", "No filtered attention item is available."); updateMessage("ready", "No matching concern", "The component is connected; adjust the local filters.", "⌕"); return true; }
    if (!visible.some((item) => item.attentionId === selectedAttentionId)) selectedAttentionId = visible[0].attentionId;
    directory.innerHTML = visible.map((item) => `<button class="pipeline-failure-row${item.attentionId === selectedAttentionId ? " active" : ""}" type="button" role="option" aria-selected="${item.attentionId === selectedAttentionId ? "true" : "false"}" data-failure-attention-id="${escapeHtml(item.attentionId)}" data-severity="${escapeHtml(item.severity)}"><span class="pipeline-failure-row-head"><strong>${escapeHtml(item.title)}</strong><span>${escapeHtml(label(item.severity))}</span></span><span class="pipeline-failure-row-meta"><span>${escapeHtml(label(item.stageId))}</span><span>${escapeHtml(label(item.kind))}</span></span><p>${escapeHtml(item.message)}</p></button>`).join(""); directory.setAttribute("aria-busy", "false"); renderDetail(visible.find((item) => item.attentionId === selectedAttentionId)); updateMessage("ready", "Owner-attention evidence loaded", `${contract.items.length} canonical concern${contract.items.length === 1 ? "" : "s"} available for inspection.`, "!"); return true;
  };
  const ensureBound = () => {
    if (bound) return true; const panel = byId("pipelineOperationsViewFailures"); const workflow = byId("pipelineFailuresWorkflow"); const scope = byId("pipelineFailuresScope"); const search = byId("pipelineFailuresSearch"); if (!panel || !workflow || !scope || !search) return false;
    panel.addEventListener("click", (event) => { const row = event.target.closest("[data-failure-attention-id]"); if (!row) return; selectedAttentionId = row.dataset.failureAttentionId || ""; renderFailures(); });
    workflow.addEventListener("change", () => { selectedWorkflowId = String(workflow.value || "all"); selectedAttentionId = ""; renderFailures(); });
    scope.addEventListener("change", () => { activeScope = String(scope.value || "all"); selectedAttentionId = ""; renderFailures(); });
    search.addEventListener("input", () => { searchQuery = String(search.value || ""); selectedAttentionId = ""; renderFailures(); });
    bound = true; return true;
  };
  const render = (payload) => { try { inspect(payload); latestPayload = payload; ensureBound(); return renderFailures(); } catch (error) { return renderUnavailable(error?.message); } };
  const renderUnavailable = (message) => {
    latestPayload = null; const directory = byId("pipelineFailuresDirectory"); const detail = byId("pipelineFailureDetail"); const count = byId("pipelineFailuresCount"); const workflow = byId("pipelineFailuresWorkflow");
    ["pipelineFailuresFailedWorkflows","pipelineFailuresFailedStages","pipelineFailuresFailedJobs","pipelineFailuresRetriesScheduled","pipelineFailuresRetriesExhausted","pipelineFailuresTerminalErrors"].forEach((id) => { const node = byId(id); if (node) node.textContent = "—"; });
    if (workflow) { workflow.innerHTML = '<option value="all">Unavailable</option>'; workflow.disabled = true; }
    if (directory) { directory.innerHTML = placeholder("Failure evidence unavailable", message || "The canonical projection could not be loaded."); directory.setAttribute("aria-busy", "false"); }
    if (detail) detail.innerHTML = placeholder("No concern available", "Owner-attention evidence failed closed."); if (count) count.textContent = "Unavailable"; updateMessage("unavailable", "Failures & Attention unavailable", message || "The canonical detail projection could not be loaded.", "!"); return false;
  };
  const activate = () => { ensureBound(); const snapshot = window.LinkCraftorConnectedDomainOverview?.getSnapshot?.(); if (snapshot) return render(snapshot); updateMessage("loading", "Loading attention evidence", "Waiting for the existing Connected Domain detail snapshot.", "◌"); return false; };
  window.LinkCraftorConnectedDomainFailuresAttention = Object.freeze({ activate, render, renderUnavailable, inspect });
})();
// END PART F 15-B4J FAILURES AND ATTENTION COMPONENT
// BEGIN PART F 15-B4K OUTPUT READINESS COMPONENT
(() => {
  "use strict";
  const PIPELINE_ID = "connect_domain";
  const STAGE_ORDER = Object.freeze(["connect_domain","site_sources","url_cleaner","site_pages","live_domain_target_pool","active_target_set"]);
  const FINAL_STAGE_ID = STAGE_ORDER[STAGE_ORDER.length - 1];
  const READINESS_LABELS = Object.freeze({ NOT_EVALUATED: "Not evaluated", PENDING: "Pending", BLOCKED: "Blocked", VERIFIED: "Verified" });
  let latestPayload = null;
  let selectedWorkflowId = "";
  let activeStatus = "all";
  let searchQuery = "";
  let bound = false;

  const byId = (id) => document.getElementById(id);
  const escapeHtml = (value) => String(value ?? "").replaceAll("&", "&amp;").replaceAll("<", "&lt;").replaceAll(">", "&gt;").replaceAll('"', "&quot;").replaceAll("'", "&#039;");
  const label = (value) => String(value || "unknown").split(/[_-]+/).filter(Boolean).map((part) => part.charAt(0).toUpperCase() + part.slice(1)).join(" ");
  const array = (value) => Array.isArray(value) ? value : [];
  const integer = (value) => { const number = Number(value); return Number.isFinite(number) && number >= 0 ? Math.trunc(number) : 0; };
  const timestamp = (value) => { if (!value) return "Unavailable"; const date = new Date(value); return Number.isNaN(date.getTime()) ? String(value) : date.toLocaleString(); };

  const normalizeWorkflow = (workflow, stageOrder) => {
    const workflowId = String(workflow?.workflow_id || "").trim();
    if (!workflowId) throw new Error("Output Readiness received an empty workflow identity.");
    const status = String(workflow?.status || "unknown").toLowerCase();
    const stageCount = integer(workflow?.stage_count);
    const completedStages = array(workflow?.completed_stages).map(String);
    const pendingStages = array(workflow?.pending_stages).map(String);
    const failedStages = array(workflow?.failed_stages).map(String);
    const recordedStages = completedStages.concat(pendingStages, failedStages);
    const currentStage = String(workflow?.current_stage || "");
    if (stageCount !== stageOrder.length) throw new Error("Output Readiness requires six stages for every projected workflow.");
    if (recordedStages.some((stageId) => !stageOrder.includes(stageId))) throw new Error("Output Readiness received a stage outside the canonical contract.");
    if (new Set(recordedStages).size !== recordedStages.length || stageOrder.some((stageId) => !recordedStages.includes(stageId))) throw new Error("Output Readiness requires a complete, non-overlapping stage partition.");
    if (currentStage && !stageOrder.includes(currentStage)) throw new Error("Output Readiness received an invalid current-stage identity.");
    const outputReady = workflow?.output_ready === true;
    if (outputReady && status !== "completed") throw new Error("Output readiness cannot be verified for an unfinished workflow.");
    if (outputReady && !completedStages.includes(FINAL_STAGE_ID)) throw new Error("Verified output lacks completed final-stage evidence.");
    const readinessStatus = status === "failed" || (status === "completed" && !outputReady)
      ? "BLOCKED" : outputReady ? "VERIFIED" : "PENDING";
    const reason = readinessStatus === "VERIFIED"
      ? "Workflow completed and Active Target Set output evidence is projected."
      : readinessStatus === "BLOCKED"
        ? (status === "failed" ? "The workflow is failed; final output readiness is blocked." : "The workflow completed without projected final-output evidence.")
        : "The workflow is unfinished; final output readiness remains pending.";
    return Object.freeze({
      workflowId,
      correlationId: String(workflow?.correlation_id || "Unavailable"),
      workspaceId: String(workflow?.workspace_id || "Unavailable"),
      status,
      currentStage,
      createdAt: workflow?.created_at || null,
      updatedAt: workflow?.updated_at || null,
      stageCount,
      completedStages,
      pendingStages,
      failedStages,
      outputReady,
      readinessStatus,
      reason
    });
  };

  const inspect = (payload) => {
    if (!payload || payload.pipeline_id !== PIPELINE_ID) throw new Error("Output Readiness received an invalid pipeline identity.");
    const stageOrder = array(payload.stage_order).map(String);
    if (JSON.stringify(stageOrder) !== JSON.stringify(STAGE_ORDER)) throw new Error("Output Readiness requires the canonical six-stage order.");
    if (!Array.isArray(payload.workflows)) throw new Error("Output Readiness requires persisted workflow evidence.");
    const counts = payload.counts && typeof payload.counts === "object" ? payload.counts : null;
    const readiness = payload.output_readiness && typeof payload.output_readiness === "object" ? payload.output_readiness : null;
    if (!counts || !readiness) throw new Error("Output Readiness summary evidence is unavailable.");
    const readinessStatus = String(readiness.readiness_status || "").trim().toUpperCase();
    if (!Object.prototype.hasOwnProperty.call(READINESS_LABELS, readinessStatus)) throw new Error("Output Readiness received an unknown readiness status.");
    if (String(readiness.final_stage_id || "") !== FINAL_STAGE_ID) throw new Error("Output Readiness received an invalid final-stage identity.");
    const workflows = payload.workflows.map((workflow) => normalizeWorkflow(workflow, stageOrder));
    const workflowCount = integer(counts.workflow_count);
    const completedCount = integer(readiness.completed_workflow_count);
    const readyCount = integer(readiness.ready_workflow_count);
    const derivedCompleted = workflows.filter((workflow) => workflow.status === "completed").length;
    const derivedReady = workflows.filter((workflow) => workflow.outputReady).length;
    const blockedCount = workflows.filter((workflow) => workflow.readinessStatus === "BLOCKED").length;
    const pendingCount = workflows.filter((workflow) => workflow.readinessStatus === "PENDING").length;
    const derivedStatus = workflows.length === 0
      ? "NOT_EVALUATED"
      : blockedCount > 0
        ? "BLOCKED"
        : derivedCompleted === workflows.length && derivedReady === workflows.length
          ? "VERIFIED" : "PENDING";
    if (workflowCount !== workflows.length || completedCount !== derivedCompleted || readyCount !== derivedReady) throw new Error("Output Readiness summary counts disagree with workflow evidence.");
    if (readinessStatus !== derivedStatus) throw new Error("Output Readiness status disagrees with canonical workflow evidence.");
    if ((readiness.all_completed_outputs_ready === true) !== (readinessStatus === "VERIFIED")) throw new Error("Output Readiness legacy readiness evidence is inconsistent.");
    return Object.freeze({
      stageOrder,
      finalStageId: FINAL_STAGE_ID,
      readinessStatus,
      workflowCount,
      completedCount,
      readyCount,
      pendingCount,
      blockedCount,
      workflows
    });
  };

  const updateMessage = (state, readinessStatus, title, message, symbol) => {
    const panel = byId("pipelineOperationsViewOutputReadiness");
    const stateLabel = byId("pipelineReadinessState");
    const container = byId("pipelineReadinessMessage");
    if (panel) {
      panel.dataset.componentState = state;
      panel.dataset.readinessStatus = String(readinessStatus || "unavailable").toLowerCase();
      panel.setAttribute("aria-busy", state === "loading" ? "true" : "false");
    }
    if (stateLabel) stateLabel.textContent = READINESS_LABELS[readinessStatus] || label(state);
    if (container) {
      container.dataset.state = state;
      const icon = container.querySelector(":scope > span");
      const heading = container.querySelector("strong");
      const paragraph = container.querySelector("p");
      if (icon) icon.textContent = symbol;
      if (heading) heading.textContent = title;
      if (paragraph) paragraph.textContent = message;
    }
  };

  const placeholder = (title, message) => '<div class="pipeline-readiness-placeholder"><strong>' + escapeHtml(title) + '</strong><p>' + escapeHtml(message) + '</p></div>';

  const setSummary = (contract) => {
    const bindings = {
      pipelineReadinessOverall: READINESS_LABELS[contract.readinessStatus],
      pipelineReadinessTotalWorkflows: contract.workflowCount,
      pipelineReadinessCompletedWorkflows: contract.completedCount,
      pipelineReadinessReadyOutputs: contract.readyCount,
      pipelineReadinessPendingWorkflows: contract.pendingCount,
      pipelineReadinessBlockedWorkflows: contract.blockedCount
    };
    Object.entries(bindings).forEach(([id, value]) => { const node = byId(id); if (node) node.textContent = String(value); });
  };

  const workflowMatches = (workflow) => {
    const statusMatches = activeStatus === "all" || workflow.readinessStatus === activeStatus;
    const query = searchQuery.trim().toLowerCase();
    if (!query) return statusMatches;
    return statusMatches && [workflow.workflowId, workflow.correlationId, workflow.workspaceId, workflow.status, workflow.currentStage, workflow.readinessStatus].some((value) => String(value).toLowerCase().includes(query));
  };

  const stageState = (workflow, stageId) => {
    if (workflow.failedStages.includes(stageId)) return "failed";
    if (workflow.completedStages.includes(stageId)) return "completed";
    if (workflow.currentStage === stageId) return "current";
    return "pending";
  };

  const renderDetail = (workflow, contract) => {
    const detail = byId("pipelineReadinessDetail");
    if (!detail) return false;
    const stages = contract.stageOrder.map((stageId, index) => {
      const state = stageState(workflow, stageId);
      return '<li data-state="' + escapeHtml(state) + '"><span>' + String(index + 1).padStart(2, "0") + '</span><strong>' + escapeHtml(label(stageId)) + '</strong><small>' + escapeHtml(label(state)) + '</small></li>';
    }).join("");
    detail.innerHTML =
      '<header class="pipeline-readiness-detail-head"><div><span>Selected workflow</span><strong>' + escapeHtml(workflow.workflowId) + '</strong></div><b class="pipeline-readiness-badge" data-status="' + escapeHtml(workflow.readinessStatus) + '">' + escapeHtml(READINESS_LABELS[workflow.readinessStatus]) + '</b></header>' +
      '<div class="pipeline-readiness-facts">' +
        '<article><span>Lifecycle</span><strong>' + escapeHtml(label(workflow.status)) + '</strong></article>' +
        '<article><span>Current stage</span><strong>' + escapeHtml(workflow.currentStage ? label(workflow.currentStage) : "No active stage") + '</strong></article>' +
        '<article><span>Final stage</span><strong>' + escapeHtml(label(contract.finalStageId)) + '</strong></article>' +
        '<article><span>Stage completion</span><strong>' + workflow.completedStages.length + ' of ' + workflow.stageCount + '</strong></article>' +
        '<article><span>Final output</span><strong>' + (workflow.outputReady ? "Available" : "Not available") + '</strong></article>' +
        '<article><span>Workspace</span><strong>' + escapeHtml(workflow.workspaceId) + '</strong></article>' +
        '<article><span>Correlation</span><strong>' + escapeHtml(workflow.correlationId) + '</strong></article>' +
        '<article><span>Created</span><strong>' + escapeHtml(timestamp(workflow.createdAt)) + '</strong></article>' +
        '<article><span>Last updated</span><strong>' + escapeHtml(timestamp(workflow.updatedAt)) + '</strong></article>' +
      '</div>' +
      '<ol class="pipeline-readiness-stage-strip" aria-label="Selected workflow stage evidence">' + stages + '</ol>' +
      '<div class="pipeline-readiness-verdict" data-status="' + escapeHtml(workflow.readinessStatus) + '"><span>Readiness verdict</span><strong>' + escapeHtml(READINESS_LABELS[workflow.readinessStatus]) + '</strong><p>' + escapeHtml(workflow.reason) + '</p></div>';
    return true;
  };

  const renderReadiness = () => {
    if (!latestPayload) return false;
    const contract = inspect(latestPayload);
    const directory = byId("pipelineReadinessDirectory");
    const detail = byId("pipelineReadinessDetail");
    const count = byId("pipelineReadinessCount");
    const filter = byId("pipelineReadinessStatusFilter");
    if (!directory) return false;
    setSummary(contract);
    if (filter) filter.disabled = false;
    const visible = contract.workflows.filter(workflowMatches);
    if (count) count.textContent = String(visible.length) + " of " + String(contract.workflows.length);
    if (!contract.workflows.length) {
      selectedWorkflowId = "";
      directory.innerHTML = placeholder("No workflows to evaluate", "Connected Domain has no persisted workflow output evidence.");
      directory.setAttribute("aria-busy", "false");
      if (detail) detail.innerHTML = placeholder("Output readiness not evaluated", "A readiness verdict requires at least one persisted workflow.");
      updateMessage("empty", "NOT_EVALUATED", "Output readiness not evaluated", "No workflow has entered the final-output contract.", "◎");
      return true;
    }
    if (!visible.length) {
      selectedWorkflowId = "";
      directory.innerHTML = placeholder("No workflows match", "Change the readiness-state filter or workflow search.");
      directory.setAttribute("aria-busy", "false");
      if (detail) detail.innerHTML = placeholder("No workflow selected", "No filtered workflow is available.");
      updateMessage("ready", contract.readinessStatus, "No matching workflow", "The output-readiness projection is connected; adjust the local filters.", "⌕");
      return true;
    }
    if (!visible.some((workflow) => workflow.workflowId === selectedWorkflowId)) selectedWorkflowId = visible[0].workflowId;
    directory.innerHTML = visible.map((workflow) =>
      '<button class="pipeline-readiness-row' + (workflow.workflowId === selectedWorkflowId ? " active" : "") + '" type="button" role="option" aria-selected="' + (workflow.workflowId === selectedWorkflowId ? "true" : "false") + '" data-readiness-workflow-id="' + escapeHtml(workflow.workflowId) + '" data-status="' + escapeHtml(workflow.readinessStatus) + '">' +
        '<span class="pipeline-readiness-row-head"><strong>' + escapeHtml(workflow.workflowId) + '</strong><span class="pipeline-readiness-badge" data-status="' + escapeHtml(workflow.readinessStatus) + '">' + escapeHtml(READINESS_LABELS[workflow.readinessStatus]) + '</span></span>' +
        '<span class="pipeline-readiness-row-meta"><span>' + escapeHtml(label(workflow.status)) + '</span><span>' + workflow.completedStages.length + ' of ' + workflow.stageCount + ' stages</span></span>' +
        '<p>' + escapeHtml(workflow.reason) + '</p>' +
      '</button>'
    ).join("");
    directory.setAttribute("aria-busy", "false");
    renderDetail(visible.find((workflow) => workflow.workflowId === selectedWorkflowId), contract);
    const title = contract.readinessStatus === "VERIFIED" ? "Output readiness verified" : contract.readinessStatus === "BLOCKED" ? "Output readiness blocked" : "Output readiness pending";
    const message = contract.readinessStatus === "VERIFIED"
      ? "Every persisted workflow is complete with final Active Target Set output evidence."
      : contract.readinessStatus === "BLOCKED"
        ? String(contract.blockedCount) + " workflow" + (contract.blockedCount === 1 ? "" : "s") + " block final-output verification."
        : String(contract.pendingCount) + " workflow" + (contract.pendingCount === 1 ? "" : "s") + " remain unfinished.";
    updateMessage("ready", contract.readinessStatus, title, message, contract.readinessStatus === "VERIFIED" ? "✓" : contract.readinessStatus === "BLOCKED" ? "!" : "◌");
    return true;
  };

  const ensureBound = () => {
    if (bound) return true;
    const panel = byId("pipelineOperationsViewOutputReadiness");
    const filter = byId("pipelineReadinessStatusFilter");
    const search = byId("pipelineReadinessSearch");
    if (!panel || !filter || !search) return false;
    panel.addEventListener("click", (event) => {
      const row = event.target.closest("[data-readiness-workflow-id]");
      if (!row) return;
      selectedWorkflowId = row.dataset.readinessWorkflowId || "";
      renderReadiness();
    });
    filter.addEventListener("change", () => { activeStatus = String(filter.value || "all"); selectedWorkflowId = ""; renderReadiness(); });
    search.addEventListener("input", () => { searchQuery = String(search.value || ""); selectedWorkflowId = ""; renderReadiness(); });
    bound = true;
    return true;
  };

  const render = (payload) => {
    try {
      inspect(payload);
      latestPayload = payload;
      ensureBound();
      return renderReadiness();
    } catch (error) {
      return renderUnavailable(error?.message);
    }
  };

  const renderUnavailable = (message) => {
    latestPayload = null;
    const directory = byId("pipelineReadinessDirectory");
    const detail = byId("pipelineReadinessDetail");
    const count = byId("pipelineReadinessCount");
    const filter = byId("pipelineReadinessStatusFilter");
    ["pipelineReadinessOverall","pipelineReadinessTotalWorkflows","pipelineReadinessCompletedWorkflows","pipelineReadinessReadyOutputs","pipelineReadinessPendingWorkflows","pipelineReadinessBlockedWorkflows"].forEach((id) => { const node = byId(id); if (node) node.textContent = "—"; });
    if (filter) { filter.value = "all"; filter.disabled = true; }
    if (directory) { directory.innerHTML = placeholder("Output evidence unavailable", message || "The canonical projection could not be loaded."); directory.setAttribute("aria-busy", "false"); }
    if (detail) detail.innerHTML = placeholder("No readiness verdict", "Final-output evidence failed closed.");
    if (count) count.textContent = "Unavailable";
    updateMessage("unavailable", "UNAVAILABLE", "Output Readiness unavailable", message || "The canonical detail projection could not be loaded.", "!");
    return false;
  };

  const activate = () => {
    ensureBound();
    const snapshot = window.LinkCraftorConnectedDomainOverview?.getSnapshot?.();
    if (snapshot) return render(snapshot);
    updateMessage("loading", "LOADING", "Loading output readiness", "Waiting for the existing Connected Domain detail snapshot.", "◌");
    return false;
  };

  window.LinkCraftorConnectedDomainOutputReadiness = Object.freeze({ activate, render, renderUnavailable, inspect });
})();
// END PART F 15-B4K OUTPUT READINESS COMPONENT
// BEGIN PART F 15-B4M CROSS-COMPONENT REGRESSION AND ACCESSIBILITY CLOSURE
(() => {
  "use strict";

  const PAIRS = Object.freeze([
    Object.freeze({ view: "overview", tabId: "pipelineOperationsTabOverview", panelId: "pipelineOperationsViewOverview" }),
    Object.freeze({ view: "workflows", tabId: "pipelineOperationsTabWorkflows", panelId: "pipelineOperationsViewWorkflows" }),
    Object.freeze({ view: "stage_progress", tabId: "pipelineOperationsTabStageProgress", panelId: "pipelineOperationsViewStageProgress" }),
    Object.freeze({ view: "jobs_attempts", tabId: "pipelineOperationsTabJobsAttempts", panelId: "pipelineOperationsViewJobsAttempts" }),
    Object.freeze({ view: "dependencies_handoffs", tabId: "pipelineOperationsTabDependenciesHandoffs", panelId: "pipelineOperationsViewDependenciesHandoffs" }),
    Object.freeze({ view: "events_timeline", tabId: "pipelineOperationsTabEventsTimeline", panelId: "pipelineOperationsViewEventsTimeline" }),
    Object.freeze({ view: "failures", tabId: "pipelineOperationsTabFailures", panelId: "pipelineOperationsViewFailures" }),
    Object.freeze({ view: "output_readiness", tabId: "pipelineOperationsTabOutputReadiness", panelId: "pipelineOperationsViewOutputReadiness" })
  ]);
  const TAB_KEYS = new Set(["ArrowRight", "ArrowDown", "ArrowLeft", "ArrowUp", "Home", "End"]);

  const resolveTabIndex = (key, currentIndex, length) => {
    if (!Number.isInteger(length) || length < 1) return -1;
    if (key === "Home") return 0;
    if (key === "End") return length - 1;
    if (key === "ArrowRight" || key === "ArrowDown") return (currentIndex + 1) % length;
    if (key === "ArrowLeft" || key === "ArrowUp") return (currentIndex - 1 + length) % length;
    return currentIndex;
  };

  const sync = () => {
    PAIRS.forEach(({ tabId, panelId }) => {
      const tab = document.getElementById(tabId);
      const panel = document.getElementById(panelId);
      if (!tab || !panel) return;
      const selected = tab.getAttribute("aria-selected") === "true";
      tab.tabIndex = selected ? 0 : -1;
      tab.setAttribute("aria-controls", panelId);
      panel.setAttribute("aria-labelledby", tabId);
      panel.setAttribute("aria-hidden", selected ? "false" : "true");
      panel.tabIndex = 0;
    });
    return true;
  };

  const onTabKeydown = (event) => {
    if (!TAB_KEYS.has(event.key) || event.altKey || event.ctrlKey || event.metaKey) return;
    const current = event.target.closest?.('[role="tab"][data-pipeline-operations-view]');
    const nav = current?.closest?.('[role="tablist"]');
    if (!current || !nav) return;
    const tabs = Array.from(nav.querySelectorAll('[role="tab"][data-pipeline-operations-view]')).filter((tab) => !tab.disabled);
    const currentIndex = tabs.indexOf(current);
    if (currentIndex < 0) return;
    const target = tabs[resolveTabIndex(event.key, currentIndex, tabs.length)];
    if (!target) return;
    event.preventDefault();
    target.click();
    target.focus();
    queueMicrotask(sync);
  };

  const onListboxKeydown = (event) => {
    if (!new Set(["ArrowDown", "ArrowUp", "Home", "End"]).has(event.key) || event.altKey || event.ctrlKey || event.metaKey) return;
    const option = event.target.closest?.('[role="option"]');
    const listbox = option?.closest?.('[role="listbox"]');
    if (!option || !listbox) return;
    const options = Array.from(listbox.querySelectorAll('[role="option"]')).filter((item) => !item.disabled);
    const currentIndex = options.indexOf(option);
    if (currentIndex < 0) return;
    const target = options[resolveTabIndex(event.key, currentIndex, options.length)];
    if (!target) return;
    event.preventDefault();
    target.focus();
    if (target !== option) target.click();
  };

  const initialize = () => {
    const page = document.getElementById("runtimePage");
    const nav = document.getElementById("pipelineOperationsViewNav");
    if (!page || !nav || page.dataset.pipelineAccessibilityBound === "true") return false;
    nav.addEventListener("keydown", onTabKeydown);
    document.addEventListener("keydown", onListboxKeydown);
    new MutationObserver(sync).observe(nav, {
      subtree: true,
      attributes: true,
      attributeFilter: ["aria-selected"]
    });
    sync();
    page.dataset.pipelineAccessibilityBound = "true";
    return true;
  };

  window.LinkCraftorPipelineAccessibility = Object.freeze({ sync, resolveTabIndex });
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initialize, { once: true });
  } else {
    initialize();
  }
})();
// END PART F 15-B4M CROSS-COMPONENT REGRESSION AND ACCESSIBILITY CLOSURE
// BEGIN PART F 15-B5K RUNTIME INFRASTRUCTURE JOBS WIRING
(() => {
  "use strict";

  const ENDPOINT = "/owner/api/runtime/infrastructure";
  const PREFIX = "runtimeInfrastructureJobs";
  const SUMMARY_FIELDS = Object.freeze([
    "total_jobs",
    "queued_jobs",
    "running_jobs",
    "completed_jobs",
    "failed_jobs",
    "cancelled_jobs"
  ]);
  const DETAIL_FIELDS = Object.freeze([
    "job_id",
    "workflow_id",
    "correlation_id",
    "workspace_id",
    "pipeline_id",
    "status",
    "stage",
    "job_type",
    "priority",
    "progress",
    "assigned_worker_id",
    "lease_identity",
    "lease_expiry",
    "attempt_count",
    "attempt_limit",
    "retry_state",
    "next_retry_at",
    "created_at",
    "updated_at",
    "started_at",
    "completed_at",
    "dispatch_result",
    "terminal_error",
    "event_count"
  ]);

  let cachedSnapshot = null;
  let pendingSnapshot = null;
  let allJobs = [];
  let visibleJobs = [];
  let selectedJobId = "";

  const byId = (id) => document.getElementById(id);

  const workspace = () => byId(`${PREFIX}Workspace`);
  const directory = () => byId(`${PREFIX}Directory`);
  const filters = () => byId(`${PREFIX}Filters`);

  const normalizedText = (value) =>
    String(value ?? "").trim().toLowerCase();

  const displayValue = (value) => {
    if (value === null || value === undefined || value === "") {
      return "Unavailable";
    }
    if (Array.isArray(value)) {
      return value.length ? value.map(displayValue).join(", ") : "None";
    }
    if (typeof value === "object") {
      try {
        return JSON.stringify(value);
      } catch (_) {
        return "Recorded evidence";
      }
    }
    return String(value);
  };

  const setState = (state, label) => {
    const root = workspace();
    const badge = byId(`${PREFIX}StateBadge`);
    if (root) {
      root.dataset.runtimeInfrastructureState = state;
    }
    if (badge) {
      badge.textContent = label;
    }
  };

  const setMessage = (title, body) => {
    const node = byId(`${PREFIX}Message`);
    if (!node) {
      return;
    }
    const strong = node.querySelector("strong");
    const span = node.querySelector("span");
    if (strong) {
      strong.textContent = title;
    }
    if (span) {
      span.textContent = body;
    }
  };

  const clearDirectory = (title, body) => {
    const node = directory();
    if (!node) {
      return;
    }
    node.classList.remove("is-populated");
    node.removeAttribute("aria-activedescendant");
    const strong = document.createElement("strong");
    strong.textContent = title;
    const span = document.createElement("span");
    span.textContent = body;
    node.replaceChildren(strong, span);
  };

  const clearDetail = () => {
    DETAIL_FIELDS.forEach((field) => {
      const node = workspace()?.querySelector(
        `[data-runtime-infrastructure-field="${field}"]`
      );
      if (node) {
        node.textContent = "Unavailable";
      }
    });
  };

  const renderSummary = (summary = {}) => {
    SUMMARY_FIELDS.forEach((metric) => {
      const card = workspace()?.querySelector(
        `[data-runtime-infrastructure-metric="${metric}"]`
      );
      if (!card) {
        return;
      }
      const value = card.querySelector("strong");
      const note = card.querySelector("small");
      if (value) {
        value.textContent = displayValue(summary[metric]);
      }
      if (note) {
        note.textContent = "Recorded evidence";
      }
    });
  };

  const selectOptions = (key, fallback, values) => {
    const control = filters()?.querySelector(
      `[data-runtime-infrastructure-filter="${key}"]`
    );
    if (!(control instanceof HTMLSelectElement)) {
      return;
    }
    const selected = control.value;
    const first = document.createElement("option");
    first.value = "";
    first.textContent = fallback;
    const options = [first];
    [...new Set(values.filter(Boolean).map(String))]
      .sort((left, right) => left.localeCompare(right))
      .forEach((value) => {
        const option = document.createElement("option");
        option.value = value;
        option.textContent = value;
        options.push(option);
      });
    control.replaceChildren(...options);
    if ([...control.options].some((option) => option.value === selected)) {
      control.value = selected;
    }
  };

  const enableFilters = () => {
    const fieldset = filters();
    if (!fieldset) {
      return;
    }
    fieldset.disabled = false;
    fieldset.querySelectorAll("input, select").forEach((control) => {
      control.disabled = false;
    });
    selectOptions(
      "pipeline_scope",
      "All pipelines",
      allJobs.map((job) => job.pipeline_id)
    );
    selectOptions(
      "job_status",
      "All statuses",
      allJobs.map((job) => job.status)
    );
    selectOptions(
      "priority",
      "All priorities",
      allJobs.map((job) => job.priority)
    );
  };

  const selectedFilters = () => {
    const value = (key) =>
      filters()?.querySelector(
        `[data-runtime-infrastructure-filter="${key}"]`
      )?.value ?? "";
    return {
      pipeline: normalizedText(value("pipeline_scope")),
      status: normalizedText(value("job_status")),
      priority: normalizedText(value("priority")),
      search: normalizedText(value("identity_search"))
    };
  };

  const filterJobs = () => {
    const active = selectedFilters();
    return allJobs.filter((job) => {
      if (active.pipeline && normalizedText(job.pipeline_id) !== active.pipeline) {
        return false;
      }
      if (active.status && normalizedText(job.status) !== active.status) {
        return false;
      }
      if (active.priority && normalizedText(job.priority) !== active.priority) {
        return false;
      }
      if (active.search) {
        const haystack = [
          job.job_id,
          job.workflow_id,
          job.correlation_id,
          job.workspace_id,
          job.pipeline_id,
          job.job_type,
          job.stage,
          job.assigned_worker_id
        ].map(normalizedText).join(" ");
        if (!haystack.includes(active.search)) {
          return false;
        }
      }
      return true;
    });
  };

  const renderDetail = (job) => {
    DETAIL_FIELDS.forEach((field) => {
      const node = workspace()?.querySelector(
        `[data-runtime-infrastructure-field="${field}"]`
      );
      if (node) {
        node.textContent = displayValue(job?.[field]);
      }
    });
  };

  const selectJob = (jobId, focus = false) => {
    const selected = visibleJobs.find((job) => job.job_id === jobId);
    if (!selected) {
      selectedJobId = "";
      clearDetail();
      return;
    }
    selectedJobId = selected.job_id;
    directory()?.querySelectorAll("[role='option']").forEach((option) => {
      const active = option.dataset.jobId === selectedJobId;
      option.setAttribute("aria-selected", active ? "true" : "false");
      option.tabIndex = active ? 0 : -1;
      if (active) {
        directory()?.setAttribute("aria-activedescendant", option.id);
        if (focus) {
          option.focus();
        }
      }
    });
    renderDetail(selected);
  };

  const jobOption = (job, index) => {
    const button = document.createElement("button");
    button.type = "button";
    button.className = "runtime-infrastructure-job-option";
    button.id = `${PREFIX}Option${index}`;
    button.dataset.jobId = String(job.job_id);
    button.setAttribute("role", "option");
    button.setAttribute("aria-selected", "false");
    button.tabIndex = -1;

    const identity = document.createElement("strong");
    identity.textContent = displayValue(job.job_id);
    const state = document.createElement("span");
    state.textContent = [job.status, job.stage].filter(Boolean).join(" · ") || "Status unavailable";
    const context = document.createElement("small");
    context.textContent = [job.pipeline_id, job.job_type, job.workspace_id]
      .filter(Boolean).join(" · ") || "Context unavailable";
    button.append(identity, state, context);
    button.addEventListener("click", () => selectJob(job.job_id));
    return button;
  };

  const renderDirectory = () => {
    visibleJobs = filterJobs();
    if (!allJobs.length) {
      clearDirectory(
        "No recorded jobs",
        "The canonical job store is available and currently contains no job records."
      );
      clearDetail();
      setState("empty", "EMPTY");
      setMessage("No job evidence", "No execution activity was invented.");
      return;
    }
    if (!visibleJobs.length) {
      clearDirectory(
        "No matching jobs",
        "Adjust the local filters or identity search."
      );
      clearDetail();
      setState("no_match", "NO MATCH");
      setMessage("No matching job evidence", "The cached snapshot remains loaded.");
      return;
    }

    const node = directory();
    if (!node) {
      return;
    }
    node.classList.add("is-populated");
    node.setAttribute("aria-disabled", "false");
    node.replaceChildren(...visibleJobs.map(jobOption));

    if (!visibleJobs.some((job) => job.job_id === selectedJobId)) {
      selectedJobId = visibleJobs[0].job_id;
    }
    selectJob(selectedJobId);
    setState("ready", "LIVE EVIDENCE");
    setMessage(
      "Canonical job evidence loaded",
      `${visibleJobs.length} of ${allJobs.length} recorded jobs visible. Local filters issue no requests.`
    );
  };

  const renderJobs = (payload) => {
    const jobs = payload?.jobs;
    if (!jobs || !Array.isArray(jobs.records) || typeof jobs.summary !== "object") {
      throw new Error("The Jobs projection contract is unavailable.");
    }
    allJobs = jobs.records.filter((job) => job && typeof job === "object");
    renderSummary(jobs.summary);
    enableFilters();
    renderDirectory();
  };

  const unavailable = (message) => {
    allJobs = [];
    visibleJobs = [];
    selectedJobId = "";
    setState("unavailable", "UNAVAILABLE");
    clearDirectory("Job evidence unavailable", message);
    clearDetail();
    setMessage("Jobs unavailable", message);
  };

  const loadSnapshot = () => {
    if (cachedSnapshot) {
      return Promise.resolve(cachedSnapshot);
    }
    if (pendingSnapshot) {
      return pendingSnapshot;
    }
    setState("loading", "LOADING");
    setMessage("Loading job evidence", "Reading the canonical infrastructure snapshot.");
    pendingSnapshot = fetch(ENDPOINT, {
      method: "GET",
      headers: { Accept: "application/json" },
      cache: "no-store",
      credentials: "same-origin"
    }).then(async (response) => {
      let payload = null;
      try {
        payload = await response.json();
      } catch (_) {
        payload = null;
      }
      if (!response.ok) {
        const detail = payload?.detail || {};
        throw new Error(detail.message || `Infrastructure evidence unavailable (${response.status}).`);
      }
      if (!payload || payload.read_only !== true) {
        throw new Error("The infrastructure snapshot did not certify read-only authority.");
      }
      cachedSnapshot = payload;
      return payload;
    }).finally(() => {
      pendingSnapshot = null;
    });
    return pendingSnapshot;
  };

  const loadAndRenderJobs = () =>
    loadSnapshot().then(renderJobs).catch((error) => {
      unavailable(error?.message || "The infrastructure evidence request failed.");
    });

  const bindFilters = () => {
    const fieldset = filters();
    if (!fieldset || fieldset.dataset.b5kBound === "true") {
      return;
    }
    fieldset.addEventListener("input", renderDirectory);
    fieldset.addEventListener("change", renderDirectory);
    fieldset.dataset.b5kBound = "true";
  };

  const bindDirectoryKeyboard = () => {
    const node = directory();
    if (!node || node.dataset.b5kBound === "true") {
      return;
    }
    node.addEventListener("keydown", (event) => {
      const options = [...node.querySelectorAll("[role='option']")];
      if (!options.length || !["ArrowDown", "ArrowUp", "Home", "End"].includes(event.key)) {
        return;
      }
      event.preventDefault();
      const current = Math.max(0, options.findIndex((option) => option.dataset.jobId === selectedJobId));
      let next = current;
      if (event.key === "ArrowDown") {
        next = (current + 1) % options.length;
      } else if (event.key === "ArrowUp") {
        next = (current - 1 + options.length) % options.length;
      } else if (event.key === "Home") {
        next = 0;
      } else if (event.key === "End") {
        next = options.length - 1;
      }
      selectJob(options[next].dataset.jobId, true);
    });
    node.dataset.b5kBound = "true";
  };

  const initialize = () => {
    if (!workspace()) {
      return;
    }
    bindFilters();
    bindDirectoryKeyboard();
    const page = byId("runtimePage");
    page?.addEventListener("runtimeowner:sectionchange", (event) => {
      if (event.detail?.section === "jobs") {
        loadAndRenderJobs();
      }
    });
    loadAndRenderJobs();
  };

  window.RuntimeInfrastructureEvidence = Object.freeze({
    endpoint: ENDPOINT,
    load: loadSnapshot,
    getSnapshot: () => cachedSnapshot
  });
  window.RuntimeInfrastructureJobs = Object.freeze({
    refreshFromCache: loadAndRenderJobs,
    getVisibleJobs: () => [...visibleJobs],
    getSelectedJobId: () => selectedJobId
  });

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initialize, { once: true });
  } else {
    initialize();
  }
})();
// END PART F 15-B5K RUNTIME INFRASTRUCTURE JOBS WIRING
// BEGIN PART F 15-B5L RUNTIME INFRASTRUCTURE QUEUES WIRING
(() => {
  "use strict";

  const PREFIX = "runtimeInfrastructureQueues";
  const SUMMARY_FIELDS = Object.freeze([
    "queued_items",
    "claimable_items",
    "reserved_items",
    "delayed_items",
    "blocked_items",
    "queue_pressure"
  ]);
  const DETAIL_FIELDS = Object.freeze([
    "queue_id",
    "queue_name",
    "pipeline_scope",
    "queued_count",
    "claimable_count",
    "delayed_count",
    "blocked_count",
    "oldest_item_at",
    "critical_count",
    "high_count",
    "normal_count",
    "low_count",
    "reserved_count",
    "active_claim_count",
    "reservation_expiry_evidence",
    "pressure_state",
    "capacity_evidence",
    "throughput_evidence",
    "last_updated_at"
  ]);

  let allQueues = [];
  let visibleQueues = [];
  let selectedQueueId = "";

  const byId = (id) => document.getElementById(id);
  const workspace = () => byId(`${PREFIX}Workspace`);
  const directory = () => byId(`${PREFIX}Directory`);
  const filters = () => byId(`${PREFIX}Filters`);
  const normalizedText = (value) => String(value ?? "").trim().toLowerCase();

  const displayValue = (value) => {
    if (value === null || value === undefined || value === "") {
      return "Unavailable";
    }
    if (Array.isArray(value)) {
      return value.length ? value.map(displayValue).join(", ") : "None";
    }
    if (typeof value === "object") {
      try {
        return JSON.stringify(value);
      } catch (_) {
        return "Recorded evidence";
      }
    }
    return String(value);
  };

  const setState = (state, label) => {
    const root = workspace();
    const badge = byId(`${PREFIX}StateBadge`);
    if (root) {
      root.dataset.runtimeInfrastructureState = state;
    }
    if (badge) {
      badge.textContent = label;
    }
  };

  const setMessage = (title, body) => {
    const node = byId(`${PREFIX}Message`);
    if (!node) {
      return;
    }
    const strong = node.querySelector("strong");
    const span = node.querySelector("span");
    if (strong) {
      strong.textContent = title;
    }
    if (span) {
      span.textContent = body;
    }
  };

  const clearDirectory = (title, body) => {
    const node = directory();
    if (!node) {
      return;
    }
    node.classList.remove("is-populated");
    node.removeAttribute("aria-activedescendant");
    const strong = document.createElement("strong");
    strong.textContent = title;
    const span = document.createElement("span");
    span.textContent = body;
    node.replaceChildren(strong, span);
  };

  const clearDetail = () => {
    DETAIL_FIELDS.forEach((field) => {
      const node = workspace()?.querySelector(
        `[data-runtime-infrastructure-field="${field}"]`
      );
      if (node) {
        node.textContent = "Unavailable";
      }
    });
  };

  const renderSummary = (summary = {}) => {
    SUMMARY_FIELDS.forEach((metric) => {
      const card = workspace()?.querySelector(
        `[data-runtime-infrastructure-metric="${metric}"]`
      );
      if (!card) {
        return;
      }
      const value = card.querySelector("strong");
      const note = card.querySelector("small");
      if (value) {
        value.textContent = displayValue(summary[metric]);
      }
      if (note) {
        note.textContent = summary[metric] === null || summary[metric] === undefined
          ? "Not recorded"
          : "Recorded evidence";
      }
    });
  };

  const selectOptions = (key, fallback, values) => {
    const control = filters()?.querySelector(
      `[data-runtime-infrastructure-filter="${key}"]`
    );
    if (!(control instanceof HTMLSelectElement)) {
      return;
    }
    const selected = control.value;
    const first = document.createElement("option");
    first.value = "";
    first.textContent = fallback;
    const options = [first];
    [...new Set(values.filter(Boolean).map(String))]
      .sort((left, right) => left.localeCompare(right))
      .forEach((value) => {
        const option = document.createElement("option");
        option.value = value;
        option.textContent = value;
        options.push(option);
      });
    control.replaceChildren(...options);
    if ([...control.options].some((option) => option.value === selected)) {
      control.value = selected;
    }
  };

  const enableFilters = () => {
    const fieldset = filters();
    if (!fieldset) {
      return;
    }
    fieldset.disabled = false;
    fieldset.querySelectorAll("input, select").forEach((control) => {
      control.disabled = false;
    });
    selectOptions(
      "queue_scope",
      "All queues",
      allQueues.map((queue) => queue.queue_name || queue.queue_id)
    );
    selectOptions(
      "item_status",
      "All statuses",
      allQueues.map((queue) => queue.item_status)
    );
    selectOptions(
      "priority",
      "All priorities",
      allQueues.flatMap((queue) => queue.priority_classes || [])
    );
  };

  const selectedFilters = () => {
    const value = (key) =>
      filters()?.querySelector(
        `[data-runtime-infrastructure-filter="${key}"]`
      )?.value ?? "";
    return {
      queue: normalizedText(value("queue_scope")),
      status: normalizedText(value("item_status")),
      priority: normalizedText(value("priority")),
      search: normalizedText(value("identity_search"))
    };
  };

  const filterQueues = () => {
    const active = selectedFilters();
    return allQueues.filter((queue) => {
      if (active.queue) {
        const identities = [queue.queue_id, queue.queue_name].map(normalizedText);
        if (!identities.includes(active.queue)) {
          return false;
        }
      }
      if (active.status && normalizedText(queue.item_status) !== active.status) {
        return false;
      }
      if (active.priority) {
        const priorities = (queue.priority_classes || []).map(normalizedText);
        if (!priorities.includes(active.priority)) {
          return false;
        }
      }
      if (active.search) {
        const haystack = [
          queue.queue_id,
          queue.queue_name,
          queue.pipeline_scope,
          ...(queue.queued_job_ids || []),
          ...(queue.workspace_ids || []),
          ...(queue.job_types || [])
        ].map(normalizedText).join(" ");
        if (!haystack.includes(active.search)) {
          return false;
        }
      }
      return true;
    });
  };

  const renderDetail = (queue) => {
    DETAIL_FIELDS.forEach((field) => {
      const node = workspace()?.querySelector(
        `[data-runtime-infrastructure-field="${field}"]`
      );
      if (node) {
        node.textContent = displayValue(queue?.[field]);
      }
    });
  };

  const selectQueue = (queueId, focus = false) => {
    const selected = visibleQueues.find((queue) => queue.queue_id === queueId);
    if (!selected) {
      selectedQueueId = "";
      clearDetail();
      return;
    }
    selectedQueueId = selected.queue_id;
    directory()?.querySelectorAll("[role='option']").forEach((option) => {
      const active = option.dataset.queueId === selectedQueueId;
      option.setAttribute("aria-selected", active ? "true" : "false");
      option.tabIndex = active ? 0 : -1;
      if (active) {
        directory()?.setAttribute("aria-activedescendant", option.id);
        if (focus) {
          option.focus();
        }
      }
    });
    renderDetail(selected);
  };

  const queueOption = (queue, index) => {
    const button = document.createElement("button");
    button.type = "button";
    button.className = "runtime-infrastructure-queue-option";
    button.id = `${PREFIX}Option${index}`;
    button.dataset.queueId = String(queue.queue_id);
    button.setAttribute("role", "option");
    button.setAttribute("aria-selected", "false");
    button.tabIndex = -1;

    const identity = document.createElement("strong");
    identity.textContent = displayValue(queue.queue_name || queue.queue_id);
    const state = document.createElement("span");
    state.textContent = `${displayValue(queue.queued_count)} queued · ${displayValue(queue.claimable_count)} claimable`;
    const context = document.createElement("small");
    context.textContent = queue.pipeline_scope
      ? `Pipeline scope: ${queue.pipeline_scope}`
      : "Pipeline scope unavailable";
    button.append(identity, state, context);
    button.addEventListener("click", () => selectQueue(queue.queue_id));
    return button;
  };

  const renderDirectory = () => {
    visibleQueues = filterQueues();
    if (!allQueues.length) {
      clearDirectory(
        "No recorded queues",
        "The canonical queue reader returned no queue records."
      );
      clearDetail();
      setState("empty", "EMPTY");
      setMessage("No queue evidence", "No queue activity was invented.");
      return;
    }
    if (!visibleQueues.length) {
      clearDirectory(
        "No matching queues",
        "Adjust the local filters or evidence search."
      );
      clearDetail();
      setState("no_match", "NO MATCH");
      setMessage("No matching queue evidence", "The cached snapshot remains loaded.");
      return;
    }

    const node = directory();
    if (!node) {
      return;
    }
    node.classList.add("is-populated");
    node.setAttribute("aria-disabled", "false");
    node.replaceChildren(...visibleQueues.map(queueOption));

    if (!visibleQueues.some((queue) => queue.queue_id === selectedQueueId)) {
      selectedQueueId = visibleQueues[0].queue_id;
    }
    selectQueue(selectedQueueId);
    setState("ready", "LIVE EVIDENCE");
    setMessage(
      "Canonical queue evidence loaded",
      `${visibleQueues.length} of ${allQueues.length} canonical queues visible. Local filters issue no requests.`
    );
  };

  const renderQueues = (payload) => {
    const queues = payload?.queues;
    if (!queues || !Array.isArray(queues.records) || typeof queues.summary !== "object") {
      throw new Error("The Queues projection contract is unavailable.");
    }
    allQueues = queues.records.filter((queue) => queue && typeof queue === "object");
    renderSummary(queues.summary);
    enableFilters();
    renderDirectory();
  };

  const unavailable = (message) => {
    allQueues = [];
    visibleQueues = [];
    selectedQueueId = "";
    setState("unavailable", "UNAVAILABLE");
    clearDirectory("Queue evidence unavailable", message);
    clearDetail();
    setMessage("Queues unavailable", message);
  };

  const loadAndRenderQueues = () => {
    const evidence = window.RuntimeInfrastructureEvidence;
    if (!evidence || typeof evidence.load !== "function") {
      unavailable("The shared infrastructure snapshot authority is unavailable.");
      return Promise.resolve();
    }
    setState("loading", "LOADING");
    setMessage("Loading queue evidence", "Reusing the cached infrastructure snapshot.");
    return evidence.load().then(renderQueues).catch((error) => {
      unavailable(error?.message || "The infrastructure evidence request failed.");
    });
  };

  const bindFilters = () => {
    const fieldset = filters();
    if (!fieldset || fieldset.dataset.b5lBound === "true") {
      return;
    }
    fieldset.addEventListener("input", renderDirectory);
    fieldset.addEventListener("change", renderDirectory);
    fieldset.dataset.b5lBound = "true";
  };

  const bindDirectoryKeyboard = () => {
    const node = directory();
    if (!node || node.dataset.b5lBound === "true") {
      return;
    }
    node.addEventListener("keydown", (event) => {
      const options = [...node.querySelectorAll("[role='option']")];
      if (!options.length || !["ArrowDown", "ArrowUp", "Home", "End"].includes(event.key)) {
        return;
      }
      event.preventDefault();
      const current = Math.max(
        0,
        options.findIndex((option) => option.dataset.queueId === selectedQueueId)
      );
      let next = current;
      if (event.key === "ArrowDown") {
        next = (current + 1) % options.length;
      } else if (event.key === "ArrowUp") {
        next = (current - 1 + options.length) % options.length;
      } else if (event.key === "Home") {
        next = 0;
      } else if (event.key === "End") {
        next = options.length - 1;
      }
      selectQueue(options[next].dataset.queueId, true);
    });
    node.dataset.b5lBound = "true";
  };

  const initialize = () => {
    if (!workspace()) {
      return;
    }
    bindFilters();
    bindDirectoryKeyboard();
    const page = byId("runtimePage");
    page?.addEventListener("runtimeowner:sectionchange", (event) => {
      if (event.detail?.section === "queues") {
        loadAndRenderQueues();
      }
    });
    loadAndRenderQueues();
  };

  window.RuntimeInfrastructureQueues = Object.freeze({
    refreshFromCache: loadAndRenderQueues,
    getVisibleQueues: () => [...visibleQueues],
    getSelectedQueueId: () => selectedQueueId
  });

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initialize, { once: true });
  } else {
    initialize();
  }
})();
// END PART F 15-B5L RUNTIME INFRASTRUCTURE QUEUES WIRING
// BEGIN PART F 15-B5M RUNTIME INFRASTRUCTURE WORKERS AND LEASES WIRING
(() => {
  "use strict";

  const PREFIX = "runtimeInfrastructureWorkersLeases";
  const SUMMARY_FIELDS = Object.freeze([
    "total_workers", "active_workers", "idle_workers",
    "busy_workers", "stale_workers", "active_leases"
  ]);
  const DETAIL_FIELDS = Object.freeze([
    "worker_id", "worker_kind", "runtime_identity", "environment",
    "lifecycle", "health", "availability", "last_heartbeat_at",
    "staleness_reason", "current_job_id", "current_workflow_id",
    "current_stage", "lease_id", "lease_owner", "lease_status",
    "acquired_at", "expires_at", "renewed_at", "concurrency_limit",
    "active_execution_count", "available_capacity"
  ]);

  let allWorkers = [];
  let visibleWorkers = [];
  let selectedWorkerId = "";

  const byId = (id) => document.getElementById(id);
  const workspace = () => byId(`${PREFIX}Workspace`);
  const directory = () => byId(`${PREFIX}Directory`);
  const filters = () => byId(`${PREFIX}Filters`);
  const normalizedText = (value) => String(value ?? "").trim().toLowerCase();

  const displayValue = (value) => {
    if (value === null || value === undefined || value === "") {
      return "Unavailable";
    }
    if (Array.isArray(value)) {
      return value.length ? value.map(displayValue).join(", ") : "None";
    }
    if (typeof value === "object") {
      try {
        return JSON.stringify(value);
      } catch (_) {
        return "Recorded evidence";
      }
    }
    return String(value);
  };

  const setState = (state, label) => {
    const root = workspace();
    const badge = byId(`${PREFIX}StateBadge`);
    if (root) root.dataset.runtimeInfrastructureState = state;
    if (badge) badge.textContent = label;
  };

  const setMessage = (title, body) => {
    const node = byId(`${PREFIX}Message`);
    if (!node) return;
    const strong = node.querySelector("strong");
    const span = node.querySelector("span");
    if (strong) strong.textContent = title;
    if (span) span.textContent = body;
  };

  const clearDirectory = (title, body) => {
    const node = directory();
    if (!node) return;
    node.classList.remove("is-populated");
    node.removeAttribute("aria-activedescendant");
    const strong = document.createElement("strong");
    strong.textContent = title;
    const span = document.createElement("span");
    span.textContent = body;
    node.replaceChildren(strong, span);
  };

  const clearDetail = () => {
    DETAIL_FIELDS.forEach((field) => {
      const node = workspace()?.querySelector(
        `[data-runtime-infrastructure-field="${field}"]`
      );
      if (node) node.textContent = "Unavailable";
    });
  };

  const renderSummary = (summary = {}) => {
    SUMMARY_FIELDS.forEach((metric) => {
      const card = workspace()?.querySelector(
        `[data-runtime-infrastructure-metric="${metric}"]`
      );
      if (!card) return;
      const value = card.querySelector("strong");
      const note = card.querySelector("small");
      const recorded = summary[metric] !== null && summary[metric] !== undefined;
      if (value) value.textContent = displayValue(summary[metric]);
      if (note) note.textContent = recorded ? "Recorded evidence" : "Not recorded";
    });
  };

  const selectOptions = (key, fallback, values) => {
    const control = filters()?.querySelector(
      `[data-runtime-infrastructure-filter="${key}"]`
    );
    if (!(control instanceof HTMLSelectElement)) return;
    const selected = control.value;
    const first = document.createElement("option");
    first.value = "";
    first.textContent = fallback;
    const options = [first];
    [...new Set(values.filter(Boolean).map(String))]
      .sort((left, right) => left.localeCompare(right))
      .forEach((value) => {
        const option = document.createElement("option");
        option.value = value;
        option.textContent = value;
        options.push(option);
      });
    control.replaceChildren(...options);
    if ([...control.options].some((option) => option.value === selected)) {
      control.value = selected;
    }
  };

  const enableFilters = () => {
    const fieldset = filters();
    if (!fieldset) return;
    fieldset.disabled = false;
    fieldset.querySelectorAll("input, select").forEach((control) => {
      control.disabled = false;
    });
    selectOptions("worker_lifecycle", "All lifecycle states", allWorkers.map((worker) => worker.lifecycle));
    selectOptions("worker_health", "All health states", allWorkers.map((worker) => worker.health));
    selectOptions("lease_state", "All lease states", allWorkers.map((worker) => worker.lease_status));
  };

  const selectedFilters = () => {
    const value = (key) => filters()?.querySelector(
      `[data-runtime-infrastructure-filter="${key}"]`
    )?.value ?? "";
    return {
      lifecycle: normalizedText(value("worker_lifecycle")),
      health: normalizedText(value("worker_health")),
      lease: normalizedText(value("lease_state")),
      search: normalizedText(value("identity_search"))
    };
  };

  const filterWorkers = () => {
    const active = selectedFilters();
    return allWorkers.filter((worker) => {
      if (active.lifecycle && normalizedText(worker.lifecycle) !== active.lifecycle) return false;
      if (active.health && normalizedText(worker.health) !== active.health) return false;
      if (active.lease && normalizedText(worker.lease_status) !== active.lease) return false;
      if (active.search) {
        const haystack = [
          worker.worker_id, worker.runtime_identity, worker.lease_id,
          worker.current_job_id, worker.current_workflow_id, worker.current_stage,
          ...(worker.recorded_job_ids || []),
          ...(worker.recorded_workflow_ids || [])
        ].map(normalizedText).join(" ");
        if (!haystack.includes(active.search)) return false;
      }
      return true;
    });
  };

  const renderDetail = (worker) => {
    DETAIL_FIELDS.forEach((field) => {
      const node = workspace()?.querySelector(
        `[data-runtime-infrastructure-field="${field}"]`
      );
      if (node) node.textContent = displayValue(worker?.[field]);
    });
  };

  const selectWorker = (workerId, focus = false) => {
    const selected = visibleWorkers.find((worker) => worker.worker_id === workerId);
    if (!selected) {
      selectedWorkerId = "";
      clearDetail();
      return;
    }
    selectedWorkerId = selected.worker_id;
    directory()?.querySelectorAll("[role='option']").forEach((option) => {
      const active = option.dataset.workerId === selectedWorkerId;
      option.setAttribute("aria-selected", active ? "true" : "false");
      option.tabIndex = active ? 0 : -1;
      if (active) {
        directory()?.setAttribute("aria-activedescendant", option.id);
        if (focus) option.focus();
      }
    });
    renderDetail(selected);
  };

  const workerOption = (worker, index) => {
    const button = document.createElement("button");
    button.type = "button";
    button.className = "runtime-infrastructure-worker-option";
    button.id = `${PREFIX}Option${index}`;
    button.dataset.workerId = String(worker.worker_id);
    button.setAttribute("role", "option");
    button.setAttribute("aria-selected", "false");
    button.tabIndex = -1;
    const identity = document.createElement("strong");
    identity.textContent = displayValue(worker.worker_identity || worker.worker_id);
    const state = document.createElement("span");
    state.textContent = worker.lease_status
      ? `Lease ${displayValue(worker.lease_status)} · ${displayValue(worker.active_execution_count)} active executions`
      : "No recorded lease state";
    const context = document.createElement("small");
    context.textContent = worker.current_job_id
      ? `Current job: ${worker.current_job_id}`
      : "No recorded current work";
    button.append(identity, state, context);
    button.addEventListener("click", () => selectWorker(worker.worker_id));
    return button;
  };

  const renderDirectory = () => {
    visibleWorkers = filterWorkers();
    if (!allWorkers.length) {
      clearDirectory(
        "No recorded workers or leases",
        "Persisted jobs contain no assigned worker identity or lease ownership evidence."
      );
      clearDetail();
      setState("empty", "EMPTY");
      setMessage("No worker evidence", "No worker, heartbeat, health, or lease activity was invented.");
      return;
    }
    if (!visibleWorkers.length) {
      clearDirectory("No matching workers", "Adjust the local filters or identity search.");
      clearDetail();
      setState("no_match", "NO MATCH");
      setMessage("No matching worker evidence", "The cached snapshot remains loaded.");
      return;
    }
    const node = directory();
    if (!node) return;
    node.classList.add("is-populated");
    node.setAttribute("aria-disabled", "false");
    node.replaceChildren(...visibleWorkers.map(workerOption));
    if (!visibleWorkers.some((worker) => worker.worker_id === selectedWorkerId)) {
      selectedWorkerId = visibleWorkers[0].worker_id;
    }
    selectWorker(selectedWorkerId);
    setState("ready", "LIVE EVIDENCE");
    setMessage(
      "Canonical worker and lease evidence loaded",
      `${visibleWorkers.length} of ${allWorkers.length} recorded workers visible. Local filters issue no requests.`
    );
  };

  const renderWorkers = (payload) => {
    const workers = payload?.workers_leases;
    if (!workers || !Array.isArray(workers.records) || typeof workers.summary !== "object") {
      throw new Error("The Workers & Leases projection contract is unavailable.");
    }
    allWorkers = workers.records.filter((worker) => worker && typeof worker === "object");
    renderSummary(workers.summary);
    enableFilters();
    renderDirectory();
  };

  const unavailable = (message) => {
    allWorkers = [];
    visibleWorkers = [];
    selectedWorkerId = "";
    setState("unavailable", "UNAVAILABLE");
    clearDirectory("Worker and lease evidence unavailable", message);
    clearDetail();
    setMessage("Workers & Leases unavailable", message);
  };

  const loadAndRenderWorkers = () => {
    const evidence = window.RuntimeInfrastructureEvidence;
    if (!evidence || typeof evidence.load !== "function") {
      unavailable("The shared infrastructure snapshot authority is unavailable.");
      return Promise.resolve();
    }
    setState("loading", "LOADING");
    setMessage("Loading worker and lease evidence", "Reusing the cached infrastructure snapshot.");
    return evidence.load().then(renderWorkers).catch((error) => {
      unavailable(error?.message || "The infrastructure evidence request failed.");
    });
  };

  const bindFilters = () => {
    const fieldset = filters();
    if (!fieldset || fieldset.dataset.b5mBound === "true") return;
    fieldset.addEventListener("input", renderDirectory);
    fieldset.addEventListener("change", renderDirectory);
    fieldset.dataset.b5mBound = "true";
  };

  const bindDirectoryKeyboard = () => {
    const node = directory();
    if (!node || node.dataset.b5mBound === "true") return;
    node.addEventListener("keydown", (event) => {
      const options = [...node.querySelectorAll("[role='option']")];
      if (!options.length || !["ArrowDown", "ArrowUp", "Home", "End"].includes(event.key)) return;
      event.preventDefault();
      const current = Math.max(0, options.findIndex((option) => option.dataset.workerId === selectedWorkerId));
      let next = current;
      if (event.key === "ArrowDown") next = (current + 1) % options.length;
      else if (event.key === "ArrowUp") next = (current - 1 + options.length) % options.length;
      else if (event.key === "Home") next = 0;
      else if (event.key === "End") next = options.length - 1;
      selectWorker(options[next].dataset.workerId, true);
    });
    node.dataset.b5mBound = "true";
  };

  const initialize = () => {
    if (!workspace()) return;
    bindFilters();
    bindDirectoryKeyboard();
    const page = byId("runtimePage");
    page?.addEventListener("runtimeowner:sectionchange", (event) => {
      if (event.detail?.section === "workers_leases") loadAndRenderWorkers();
    });
    loadAndRenderWorkers();
  };

  window.RuntimeInfrastructureWorkersLeases = Object.freeze({
    refreshFromCache: loadAndRenderWorkers,
    getVisibleWorkers: () => [...visibleWorkers],
    getSelectedWorkerId: () => selectedWorkerId
  });

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initialize, { once: true });
  } else {
    initialize();
  }
})();
// END PART F 15-B5M RUNTIME INFRASTRUCTURE WORKERS AND LEASES WIRING
// BEGIN PART F 15-B5N RUNTIME INFRASTRUCTURE ORCHESTRATION WIRING
(() => {
  "use strict";

  const PREFIX = "runtimeInfrastructureOrchestration";
  const SUMMARY_FIELDS = Object.freeze([
    "total_workflows", "active_workflows", "completed_workflows",
    "failed_workflows", "blocked_workflows", "pending_handoffs"
  ]);
  const DETAIL_FIELDS = Object.freeze([
    "workflow_id", "correlation_id", "workspace_id", "pipeline_id",
    "status", "current_stage", "created_at", "updated_at", "completed_at",
    "stage_count", "completed_stage_count", "pending_stage_count",
    "failed_stage_count", "predecessor_evidence", "successor_evidence",
    "handoff_state", "blocked_reason", "job_count", "active_job_count",
    "failed_job_count", "final_output_state"
  ]);

  let allWorkflows = [];
  let visibleWorkflows = [];
  let selectedWorkflowId = "";

  const byId = (id) => document.getElementById(id);
  const workspace = () => byId(`${PREFIX}Workspace`);
  const directory = () => byId(`${PREFIX}Directory`);
  const filters = () => byId(`${PREFIX}Filters`);
  const normalizedText = (value) => String(value ?? "").trim().toLowerCase();
  const displayValue = (value) => {
    if (value === null || value === undefined || value === "") return "Unavailable";
    if (Array.isArray(value)) return value.length ? value.map(displayValue).join(", ") : "None";
    if (typeof value === "object") {
      try { return JSON.stringify(value); } catch (_) { return "Recorded evidence"; }
    }
    return String(value);
  };

  const setState = (state, label) => {
    const root = workspace();
    const badge = byId(`${PREFIX}StateBadge`);
    if (root) root.dataset.runtimeInfrastructureState = state;
    if (badge) badge.textContent = label;
  };
  const setMessage = (title, body) => {
    const node = byId(`${PREFIX}Message`);
    if (!node) return;
    const strong = node.querySelector("strong");
    const span = node.querySelector("span");
    if (strong) strong.textContent = title;
    if (span) span.textContent = body;
  };
  const clearDirectory = (title, body) => {
    const node = directory();
    if (!node) return;
    node.classList.remove("is-populated");
    node.removeAttribute("aria-activedescendant");
    const strong = document.createElement("strong");
    strong.textContent = title;
    const span = document.createElement("span");
    span.textContent = body;
    node.replaceChildren(strong, span);
  };
  const clearDetail = () => {
    DETAIL_FIELDS.forEach((field) => {
      const node = workspace()?.querySelector(`[data-runtime-infrastructure-field="${field}"]`);
      if (node) node.textContent = "Unavailable";
    });
  };
  const renderSummary = (summary = {}) => {
    SUMMARY_FIELDS.forEach((metric) => {
      const card = workspace()?.querySelector(`[data-runtime-infrastructure-metric="${metric}"]`);
      if (!card) return;
      const value = card.querySelector("strong");
      const note = card.querySelector("small");
      const recorded = summary[metric] !== null && summary[metric] !== undefined;
      if (value) value.textContent = displayValue(summary[metric]);
      if (note) note.textContent = recorded ? "Recorded evidence" : "Not recorded";
    });
  };
  const selectOptions = (key, fallback, values) => {
    const control = filters()?.querySelector(`[data-runtime-infrastructure-filter="${key}"]`);
    if (!(control instanceof HTMLSelectElement)) return;
    const selected = control.value;
    const first = document.createElement("option");
    first.value = "";
    first.textContent = fallback;
    const options = [first];
    [...new Set(values.filter(Boolean).map(String))].sort().forEach((value) => {
      const option = document.createElement("option");
      option.value = value;
      option.textContent = value;
      options.push(option);
    });
    control.replaceChildren(...options);
    if ([...control.options].some((option) => option.value === selected)) control.value = selected;
  };
  const enableFilters = () => {
    const fieldset = filters();
    if (!fieldset) return;
    fieldset.disabled = false;
    fieldset.querySelectorAll("input, select").forEach((control) => { control.disabled = false; });
    selectOptions("pipeline_scope", "All pipelines", allWorkflows.map((item) => item.pipeline_id));
    selectOptions("workflow_lifecycle", "All lifecycle states", allWorkflows.map((item) => item.status));
    selectOptions("current_stage", "All stages", allWorkflows.map((item) => item.current_stage));
  };
  const selectedFilters = () => {
    const value = (key) => filters()?.querySelector(`[data-runtime-infrastructure-filter="${key}"]`)?.value ?? "";
    return {
      pipeline: normalizedText(value("pipeline_scope")),
      lifecycle: normalizedText(value("workflow_lifecycle")),
      stage: normalizedText(value("current_stage")),
      search: normalizedText(value("identity_search"))
    };
  };
  const filterWorkflows = () => {
    const active = selectedFilters();
    return allWorkflows.filter((item) => {
      if (active.pipeline && normalizedText(item.pipeline_id) !== active.pipeline) return false;
      if (active.lifecycle && normalizedText(item.status) !== active.lifecycle) return false;
      if (active.stage && normalizedText(item.current_stage) !== active.stage) return false;
      if (active.search) {
        const haystack = [
          item.workflow_id, item.correlation_id, item.workspace_id,
          item.pipeline_id, item.current_stage, ...(item.job_ids || [])
        ].map(normalizedText).join(" ");
        if (!haystack.includes(active.search)) return false;
      }
      return true;
    });
  };
  const renderDetail = (workflow) => {
    DETAIL_FIELDS.forEach((field) => {
      const node = workspace()?.querySelector(`[data-runtime-infrastructure-field="${field}"]`);
      if (node) node.textContent = displayValue(workflow?.[field]);
    });
  };
  const selectWorkflow = (workflowId, focus = false) => {
    const selected = visibleWorkflows.find((item) => item.workflow_id === workflowId);
    if (!selected) { selectedWorkflowId = ""; clearDetail(); return; }
    selectedWorkflowId = selected.workflow_id;
    directory()?.querySelectorAll("[role='option']").forEach((option) => {
      const active = option.dataset.workflowId === selectedWorkflowId;
      option.setAttribute("aria-selected", active ? "true" : "false");
      option.tabIndex = active ? 0 : -1;
      if (active) {
        directory()?.setAttribute("aria-activedescendant", option.id);
        if (focus) option.focus();
      }
    });
    renderDetail(selected);
  };
  const workflowOption = (workflow, index) => {
    const button = document.createElement("button");
    button.type = "button";
    button.className = "runtime-infrastructure-workflow-option";
    button.id = `${PREFIX}Option${index}`;
    button.dataset.workflowId = String(workflow.workflow_id);
    button.setAttribute("role", "option");
    button.setAttribute("aria-selected", "false");
    button.tabIndex = -1;
    const identity = document.createElement("strong");
    identity.textContent = displayValue(workflow.workflow_id);
    const state = document.createElement("span");
    state.textContent = `${displayValue(workflow.status)} · ${displayValue(workflow.completion)}`;
    const context = document.createElement("small");
    context.textContent = workflow.current_stage
      ? `Current stage: ${workflow.current_stage}`
      : "Current stage unavailable";
    button.append(identity, state, context);
    button.addEventListener("click", () => selectWorkflow(workflow.workflow_id));
    return button;
  };
  const renderDirectory = () => {
    visibleWorkflows = filterWorkflows();
    if (!allWorkflows.length) {
      clearDirectory("No recorded workflows", "Persisted jobs contain no canonical workflow identity.");
      clearDetail();
      setState("empty", "EMPTY");
      setMessage("No orchestration evidence", "No workflow, dependency, or handoff activity was invented.");
      return;
    }
    if (!visibleWorkflows.length) {
      clearDirectory("No matching workflows", "Adjust the local filters or identity search.");
      clearDetail();
      setState("no_match", "NO MATCH");
      setMessage("No matching workflow evidence", "The cached snapshot remains loaded.");
      return;
    }
    const node = directory();
    if (!node) return;
    node.classList.add("is-populated");
    node.setAttribute("aria-disabled", "false");
    node.replaceChildren(...visibleWorkflows.map(workflowOption));
    if (!visibleWorkflows.some((item) => item.workflow_id === selectedWorkflowId)) {
      selectedWorkflowId = visibleWorkflows[0].workflow_id;
    }
    selectWorkflow(selectedWorkflowId);
    setState("ready", "LIVE EVIDENCE");
    setMessage(
      "Canonical orchestration evidence loaded",
      `${visibleWorkflows.length} of ${allWorkflows.length} recorded workflows visible. Local filters issue no requests.`
    );
  };
  const renderWorkflows = (payload) => {
    const orchestration = payload?.orchestration;
    if (!orchestration || !Array.isArray(orchestration.records) || typeof orchestration.summary !== "object") {
      throw new Error("The Orchestration projection contract is unavailable.");
    }
    allWorkflows = orchestration.records.filter((item) => item && typeof item === "object");
    renderSummary(orchestration.summary);
    enableFilters();
    renderDirectory();
  };
  const unavailable = (message) => {
    allWorkflows = [];
    visibleWorkflows = [];
    selectedWorkflowId = "";
    setState("unavailable", "UNAVAILABLE");
    clearDirectory("Orchestration evidence unavailable", message);
    clearDetail();
    setMessage("Orchestration unavailable", message);
  };
  const loadAndRenderOrchestration = () => {
    const evidence = window.RuntimeInfrastructureEvidence;
    if (!evidence || typeof evidence.load !== "function") {
      unavailable("The shared infrastructure snapshot authority is unavailable.");
      return Promise.resolve();
    }
    setState("loading", "LOADING");
    setMessage("Loading orchestration evidence", "Reusing the cached infrastructure snapshot.");
    return evidence.load().then(renderWorkflows).catch((error) => {
      unavailable(error?.message || "The infrastructure evidence request failed.");
    });
  };
  const bindFilters = () => {
    const fieldset = filters();
    if (!fieldset || fieldset.dataset.b5nBound === "true") return;
    fieldset.addEventListener("input", renderDirectory);
    fieldset.addEventListener("change", renderDirectory);
    fieldset.dataset.b5nBound = "true";
  };
  const bindKeyboard = () => {
    const node = directory();
    if (!node || node.dataset.b5nBound === "true") return;
    node.addEventListener("keydown", (event) => {
      const options = [...node.querySelectorAll("[role='option']")];
      if (!options.length || !["ArrowDown", "ArrowUp", "Home", "End"].includes(event.key)) return;
      event.preventDefault();
      const current = Math.max(0, options.findIndex((option) => option.dataset.workflowId === selectedWorkflowId));
      let next = current;
      if (event.key === "ArrowDown") next = (current + 1) % options.length;
      else if (event.key === "ArrowUp") next = (current - 1 + options.length) % options.length;
      else if (event.key === "Home") next = 0;
      else if (event.key === "End") next = options.length - 1;
      selectWorkflow(options[next].dataset.workflowId, true);
    });
    node.dataset.b5nBound = "true";
  };
  const initialize = () => {
    if (!workspace()) return;
    bindFilters();
    bindKeyboard();
    byId("runtimePage")?.addEventListener("runtimeowner:sectionchange", (event) => {
      if (event.detail?.section === "orchestration") loadAndRenderOrchestration();
    });
    loadAndRenderOrchestration();
  };
  window.RuntimeInfrastructureOrchestration = Object.freeze({
    refreshFromCache: loadAndRenderOrchestration,
    getVisibleWorkflows: () => [...visibleWorkflows],
    getSelectedWorkflowId: () => selectedWorkflowId
  });
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initialize, { once: true });
  } else initialize();
})();
// END PART F 15-B5N RUNTIME INFRASTRUCTURE ORCHESTRATION WIRING
// BEGIN PART F 15-B5O RUNTIME INFRASTRUCTURE EXECUTION WIRING
(() => {
  "use strict";

  const PREFIX = "runtimeInfrastructureExecution";
  const SUMMARY_FIELDS = Object.freeze([
    "total_executions", "running_executions", "succeeded_executions",
    "failed_executions", "cancelled_executions", "terminal_executions"
  ]);
  const DETAIL_FIELDS = Object.freeze([
    "execution_id", "job_id", "workflow_id", "correlation_id", "pipeline_id",
    "handler_id", "handler_version", "stage", "execution_action", "worker_id",
    "lease_id", "dispatch_identity", "dispatched_at", "started_at", "finished_at",
    "duration", "status", "result_summary", "terminal_error", "failure_kind", "event_count"
  ]);
  let allExecutions = [];
  let visibleExecutions = [];
  let selectedJobId = "";

  const byId = (id) => document.getElementById(id);
  const workspace = () => byId(`${PREFIX}Workspace`);
  const directory = () => byId(`${PREFIX}Directory`);
  const filters = () => byId(`${PREFIX}Filters`);
  const normalizedText = (value) => String(value ?? "").trim().toLowerCase();
  const displayValue = (value) => {
    if (value === null || value === undefined || value === "") return "Unavailable";
    if (Array.isArray(value)) return value.length ? value.map(displayValue).join(", ") : "None";
    if (typeof value === "object") {
      try { return JSON.stringify(value); } catch (_) { return "Recorded evidence"; }
    }
    return String(value);
  };
  const setState = (state, label) => {
    const root = workspace();
    const badge = byId(`${PREFIX}StateBadge`);
    if (root) root.dataset.runtimeInfrastructureState = state;
    if (badge) badge.textContent = label;
  };
  const setMessage = (title, body) => {
    const node = byId(`${PREFIX}Message`);
    if (!node) return;
    const strong = node.querySelector("strong");
    const span = node.querySelector("span");
    if (strong) strong.textContent = title;
    if (span) span.textContent = body;
  };
  const clearDirectory = (title, body) => {
    const node = directory();
    if (!node) return;
    node.classList.remove("is-populated");
    node.removeAttribute("aria-activedescendant");
    const strong = document.createElement("strong");
    strong.textContent = title;
    const span = document.createElement("span");
    span.textContent = body;
    node.replaceChildren(strong, span);
  };
  const clearDetail = () => {
    DETAIL_FIELDS.forEach((field) => {
      const node = workspace()?.querySelector(`[data-runtime-infrastructure-field="${field}"]`);
      if (node) node.textContent = "Unavailable";
    });
  };
  const renderSummary = (summary = {}) => {
    SUMMARY_FIELDS.forEach((metric) => {
      const card = workspace()?.querySelector(`[data-runtime-infrastructure-metric="${metric}"]`);
      if (!card) return;
      const value = card.querySelector("strong");
      const note = card.querySelector("small");
      const recorded = summary[metric] !== null && summary[metric] !== undefined;
      if (value) value.textContent = displayValue(summary[metric]);
      if (note) note.textContent = recorded ? "Recorded evidence" : "Not recorded";
    });
  };
  const selectOptions = (key, fallback, values) => {
    const control = filters()?.querySelector(`[data-runtime-infrastructure-filter="${key}"]`);
    if (!(control instanceof HTMLSelectElement)) return;
    const selected = control.value;
    const first = document.createElement("option");
    first.value = "";
    first.textContent = fallback;
    const options = [first];
    [...new Set(values.filter(Boolean).map(String))].sort().forEach((value) => {
      const option = document.createElement("option");
      option.value = value;
      option.textContent = value;
      options.push(option);
    });
    control.replaceChildren(...options);
    if ([...control.options].some((option) => option.value === selected)) control.value = selected;
  };
  const enableFilters = () => {
    const fieldset = filters();
    if (!fieldset) return;
    fieldset.disabled = false;
    fieldset.querySelectorAll("input, select").forEach((control) => { control.disabled = false; });
    selectOptions("pipeline_scope", "All pipelines", allExecutions.map((item) => item.pipeline_id));
    selectOptions("execution_status", "All statuses", allExecutions.map((item) => item.status));
    selectOptions("handler_identity", "All handlers", allExecutions.map((item) => item.handler_id));
  };
  const selectedFilters = () => {
    const value = (key) => filters()?.querySelector(`[data-runtime-infrastructure-filter="${key}"]`)?.value ?? "";
    return {
      pipeline: normalizedText(value("pipeline_scope")),
      status: normalizedText(value("execution_status")),
      handler: normalizedText(value("handler_identity")),
      search: normalizedText(value("evidence_search"))
    };
  };
  const filterExecutions = () => {
    const active = selectedFilters();
    return allExecutions.filter((item) => {
      if (active.pipeline && normalizedText(item.pipeline_id) !== active.pipeline) return false;
      if (active.status && normalizedText(item.status) !== active.status) return false;
      if (active.handler && normalizedText(item.handler_id) !== active.handler) return false;
      if (active.search) {
        const haystack = [
          item.execution_id, item.job_id, item.workflow_id, item.correlation_id,
          item.pipeline_id, item.handler_id, item.worker_id, item.stage
        ].map(normalizedText).join(" ");
        if (!haystack.includes(active.search)) return false;
      }
      return true;
    });
  };
  const renderDetail = (execution) => {
    DETAIL_FIELDS.forEach((field) => {
      const node = workspace()?.querySelector(`[data-runtime-infrastructure-field="${field}"]`);
      if (node) node.textContent = displayValue(execution?.[field]);
    });
  };
  const selectExecution = (jobId, focus = false) => {
    const selected = visibleExecutions.find((item) => item.job_id === jobId);
    if (!selected) { selectedJobId = ""; clearDetail(); return; }
    selectedJobId = selected.job_id;
    directory()?.querySelectorAll("[role='option']").forEach((option) => {
      const active = option.dataset.jobId === selectedJobId;
      option.setAttribute("aria-selected", active ? "true" : "false");
      option.tabIndex = active ? 0 : -1;
      if (active) {
        directory()?.setAttribute("aria-activedescendant", option.id);
        if (focus) option.focus();
      }
    });
    renderDetail(selected);
  };
  const executionOption = (execution, index) => {
    const button = document.createElement("button");
    button.type = "button";
    button.className = "runtime-infrastructure-execution-option";
    button.id = `${PREFIX}Option${index}`;
    button.dataset.jobId = String(execution.job_id);
    button.setAttribute("role", "option");
    button.setAttribute("aria-selected", "false");
    button.tabIndex = -1;
    const identity = document.createElement("strong");
    identity.textContent = displayValue(execution.execution_id || execution.job_id);
    const state = document.createElement("span");
    state.textContent = `${displayValue(execution.status)} · ${displayValue(execution.stage)}`;
    const context = document.createElement("small");
    context.textContent = execution.worker_id
      ? `Worker: ${execution.worker_id}`
      : "Worker identity unavailable";
    button.append(identity, state, context);
    button.addEventListener("click", () => selectExecution(execution.job_id));
    return button;
  };
  const renderDirectory = () => {
    visibleExecutions = filterExecutions();
    if (!allExecutions.length) {
      clearDirectory("No recorded executions", "Persisted jobs contain no canonical execution evidence.");
      clearDetail();
      setState("empty", "EMPTY");
      setMessage("No execution evidence", "No handler, worker, result, or terminal activity was invented.");
      return;
    }
    if (!visibleExecutions.length) {
      clearDirectory("No matching executions", "Adjust the local filters or evidence search.");
      clearDetail();
      setState("no_match", "NO MATCH");
      setMessage("No matching execution evidence", "The cached snapshot remains loaded.");
      return;
    }
    const node = directory();
    if (!node) return;
    node.classList.add("is-populated");
    node.setAttribute("aria-disabled", "false");
    node.replaceChildren(...visibleExecutions.map(executionOption));
    if (!visibleExecutions.some((item) => item.job_id === selectedJobId)) {
      selectedJobId = visibleExecutions[0].job_id;
    }
    selectExecution(selectedJobId);
    setState("ready", "LIVE EVIDENCE");
    setMessage(
      "Canonical execution evidence loaded",
      `${visibleExecutions.length} of ${allExecutions.length} recorded executions visible. Local filters issue no requests.`
    );
  };
  const renderExecutions = (payload) => {
    const execution = payload?.execution;
    if (!execution || !Array.isArray(execution.records) || typeof execution.summary !== "object") {
      throw new Error("The Execution projection contract is unavailable.");
    }
    allExecutions = execution.records.filter((item) => item && typeof item === "object");
    renderSummary(execution.summary);
    enableFilters();
    renderDirectory();
  };
  const unavailable = (message) => {
    allExecutions = [];
    visibleExecutions = [];
    selectedJobId = "";
    setState("unavailable", "UNAVAILABLE");
    clearDirectory("Execution evidence unavailable", message);
    clearDetail();
    setMessage("Execution unavailable", message);
  };
  const loadAndRenderExecution = () => {
    const evidence = window.RuntimeInfrastructureEvidence;
    if (!evidence || typeof evidence.load !== "function") {
      unavailable("The shared infrastructure snapshot authority is unavailable.");
      return Promise.resolve();
    }
    setState("loading", "LOADING");
    setMessage("Loading execution evidence", "Reusing the cached infrastructure snapshot.");
    return evidence.load().then(renderExecutions).catch((error) => {
      unavailable(error?.message || "The infrastructure evidence request failed.");
    });
  };
  const bindFilters = () => {
    const fieldset = filters();
    if (!fieldset || fieldset.dataset.b5oBound === "true") return;
    fieldset.addEventListener("input", renderDirectory);
    fieldset.addEventListener("change", renderDirectory);
    fieldset.dataset.b5oBound = "true";
  };
  const bindKeyboard = () => {
    const node = directory();
    if (!node || node.dataset.b5oBound === "true") return;
    node.addEventListener("keydown", (event) => {
      const options = [...node.querySelectorAll("[role='option']")];
      if (!options.length || !["ArrowDown", "ArrowUp", "Home", "End"].includes(event.key)) return;
      event.preventDefault();
      const current = Math.max(0, options.findIndex((option) => option.dataset.jobId === selectedJobId));
      let next = current;
      if (event.key === "ArrowDown") next = (current + 1) % options.length;
      else if (event.key === "ArrowUp") next = (current - 1 + options.length) % options.length;
      else if (event.key === "Home") next = 0;
      else if (event.key === "End") next = options.length - 1;
      selectExecution(options[next].dataset.jobId, true);
    });
    node.dataset.b5oBound = "true";
  };
  const initialize = () => {
    if (!workspace()) return;
    bindFilters();
    bindKeyboard();
    byId("runtimePage")?.addEventListener("runtimeowner:sectionchange", (event) => {
      if (event.detail?.section === "execution") loadAndRenderExecution();
    });
    loadAndRenderExecution();
  };
  window.RuntimeInfrastructureExecution = Object.freeze({
    refreshFromCache: loadAndRenderExecution,
    getVisibleExecutions: () => [...visibleExecutions],
    getSelectedJobId: () => selectedJobId
  });
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initialize, { once: true });
  } else initialize();
})();
// END PART F 15-B5O RUNTIME INFRASTRUCTURE EXECUTION WIRING
// BEGIN PART F 15-B6B THROUGH 15-B6I OWNER ACTIONS AND RECOVERY
(() => {
  "use strict";

  const SNAPSHOT_ENDPOINT = "/owner/api/runtime/infrastructure";
  const PREVIEW_ENDPOINT = "/owner/api/runtime/actions/preview";
  const EXECUTE_ENDPOINT = "/owner/api/runtime/actions/execute";
  const ACTIONS = Object.freeze({
    jobs_queues: Object.freeze([
      ["job_claim", "Claim eligible job"],
      ["job_retry", "Retry failed job"],
      ["job_requeue", "Requeue job"],
      ["job_cancel", "Cancel job"]
    ]),
    workflows_stages: Object.freeze([
      ["workflow_retry", "Retry workflow"],
      ["workflow_cancel", "Cancel workflow"],
      ["stage_recover", "Recover failed stage"]
    ]),
    workers_leases: Object.freeze([
      ["lease_release", "Release expired lease"],
      ["worker_drain", "Drain worker"]
    ]),
    executions: Object.freeze([
      ["execution_cancel", "Cancel execution"],
      ["execution_terminate", "Terminate execution"]
    ])
  });

  const byId = (id) => document.getElementById(id);
  const family = byId("runtimeOwnerActionsFamily");
  const actionType = byId("runtimeOwnerActionsType");
  const target = byId("runtimeOwnerActionsTarget");
  const refresh = byId("runtimeOwnerActionsRefresh");
  const previewButton = byId("runtimeOwnerActionsPreviewButton");
  const executeButton = byId("runtimeOwnerActionsExecuteButton");
  if (!family || !actionType || !target || !previewButton || !executeButton) return;

  const state = { snapshot: null, records: [], preview: null };
  const text = (id, value) => {
    const node = byId(id);
    if (node) node.textContent = value == null || value === "" ? "Unavailable" : String(value);
  };
  const value = (id) => {
    const node = byId(id);
    return node ? node.value.trim() : "";
  };
  const makeKey = () => {
    if (globalThis.crypto && typeof globalThis.crypto.randomUUID === "function") {
      return globalThis.crypto.randomUUID();
    }
    return `owner-action-${Date.now()}-${Math.random().toString(16).slice(2)}`;
  };
  const setResult = (message) => text("runtimeOwnerActionsResult", message);

  const recordsForFamily = (snapshot, selectedFamily) => {
    const component = {
      jobs_queues: "jobs",
      workflows_stages: "orchestration",
      workers_leases: "workers_leases",
      executions: "execution"
    }[selectedFamily];
    const namespace = snapshot && snapshot[component];
    return namespace && Array.isArray(namespace.records) ? namespace.records : [];
  };

  const recordIdentity = (record) => {
    const fields = [
      "job_id", "job_identity", "workflow_id", "workflow_identity",
      "worker_identity", "worker_id", "lease_identity", "execution_identity",
      "queue_identity", "queue_name"
    ];
    for (const field of fields) {
      if (record && record[field] != null && record[field] !== "") return String(record[field]);
    }
    return "";
  };

  const recordState = (record) => {
    const fields = ["status", "state", "lifecycle", "lease_status", "execution_status"];
    for (const field of fields) {
      if (record && record[field] != null && record[field] !== "") return String(record[field]);
    }
    return "unavailable";
  };

  const populateActions = () => {
    actionType.replaceChildren();
    for (const [code, label] of ACTIONS[family.value] || []) {
      const option = document.createElement("option");
      option.value = code;
      option.textContent = label;
      actionType.append(option);
    }
  };

  const populateTargets = () => {
    state.records = recordsForFamily(state.snapshot, family.value);
    target.replaceChildren();
    if (!state.records.length) {
      const option = document.createElement("option");
      option.value = "";
      option.textContent = "No recorded targets available";
      target.append(option);
      return;
    }
    for (const record of state.records) {
      const identity = recordIdentity(record);
      if (!identity) continue;
      const option = document.createElement("option");
      option.value = identity;
      option.textContent = `${identity} — ${recordState(record)}`;
      target.append(option);
    }
  };

  const resetPreview = () => {
    state.preview = null;
    executeButton.disabled = true;
    text("runtimeOwnerActionsCurrentState", "Select a target");
    text("runtimeOwnerActionsEligibility", "Not evaluated");
    text("runtimeOwnerActionsRisk", "Unavailable");
    text("runtimeOwnerActionsExpectedResult", "Unavailable");
    const impact = byId("runtimeOwnerActionsImpact");
    if (impact) impact.innerHTML = "<li>Generate a preview to inspect the selected action.</li>";
    const expectedState = byId("runtimeOwnerActionsExpectedState");
    if (expectedState) expectedState.value = "Unavailable";
    const confirmation = byId("runtimeOwnerActionsConfirmation");
    if (confirmation) confirmation.value = "";
    text("runtimeOwnerActionsConfirmationHelp", "A fresh preview will provide the exact confirmation phrase.");
  };

  const loadSnapshot = async () => {
    setResult("Refreshing canonical Runtime Infrastructure evidence…");
    const response = await fetch(SNAPSHOT_ENDPOINT, {
      method: "GET",
      credentials: "same-origin",
      headers: { Accept: "application/json" }
    });
    if (!response.ok) throw new Error(`Infrastructure evidence unavailable (${response.status}).`);
    state.snapshot = await response.json();
    populateTargets();
    resetPreview();
    setResult("Canonical evidence refreshed. No owner action was executed.");
  };

  const requestJson = async (url, payload, extraHeaders = {}) => {
    const response = await fetch(url, {
      method: "POST",
      credentials: "same-origin",
      headers: { "Content-Type": "application/json", Accept: "application/json", ...extraHeaders },
      body: JSON.stringify(payload)
    });
    let body = {};
    try { body = await response.json(); } catch (_) { body = {}; }
    if (!response.ok) {
      const detail = body.detail || body.message || `Request blocked (${response.status}).`;
      throw new Error(typeof detail === "string" ? detail : JSON.stringify(detail));
    }
    return body;
  };

  const preview = async () => {
    resetPreview();
    if (!target.value) throw new Error("Select a recorded target before previewing an action.");
    const selected = state.records.find((record) => recordIdentity(record) === target.value) || {};
    const payload = {
      action_type: actionType.value,
      target_type: family.value,
      target_id: target.value,
      expected_state: recordState(selected)
    };
    setResult("Generating a read-only eligibility and impact preview…");
    const result = await requestJson(PREVIEW_ENDPOINT, payload);
    state.preview = result;
    text("runtimeOwnerActionsCurrentState", result.current_state);
    text("runtimeOwnerActionsEligibility", result.eligible ? "Eligible" : `Blocked — ${result.blocked_reason || "ineligible"}`);
    text("runtimeOwnerActionsRisk", result.risk_level);
    text("runtimeOwnerActionsExpectedResult", result.expected_result);
    const expectedState = byId("runtimeOwnerActionsExpectedState");
    if (expectedState) expectedState.value = result.current_state || "Unavailable";
    const impact = byId("runtimeOwnerActionsImpact");
    if (impact) {
      impact.replaceChildren();
      for (const item of result.impact || ["No recorded impact evidence was returned."]) {
        const li = document.createElement("li");
        li.textContent = item;
        impact.append(li);
      }
    }
    const idempotency = byId("runtimeOwnerActionsIdempotency");
    if (idempotency) idempotency.value = makeKey();
    text("runtimeOwnerActionsConfirmationHelp", `Type exactly: ${result.confirmation_phrase || "Unavailable"}`);
    executeButton.disabled = !result.eligible;
    setResult(result.eligible
      ? "Preview complete. Review the impact and confirmation requirements."
      : `Action blocked by fresh eligibility: ${result.blocked_reason || "not eligible"}.`);
  };

  const execute = async () => {
    if (!state.preview || !state.preview.eligible) throw new Error("Generate a fresh eligible preview first.");
    const payload = {
      action_type: actionType.value,
      target_type: family.value,
      target_id: target.value,
      expected_state: value("runtimeOwnerActionsExpectedState"),
      reason: value("runtimeOwnerActionsReason"),
      confirmation: value("runtimeOwnerActionsConfirmation"),
      confirmation_token: state.preview.confirmation_token,
      idempotency_key: value("runtimeOwnerActionsIdempotency")
    };
    executeButton.disabled = true;
    setResult("Submitting the protected action request…");
    try {
      const result = await requestJson(EXECUTE_ENDPOINT, payload, {
        "X-LinkCraftor-Idempotency-Key": payload.idempotency_key
      });
      setResult(`Request ${result.request_id || "recorded"}: ${result.status || "accepted"}.`);
      await loadSnapshot();
    } finally {
      executeButton.disabled = !state.preview || !state.preview.eligible;
    }
  };

  family.addEventListener("change", () => {
    populateActions();
    populateTargets();
    resetPreview();
  });
  actionType.addEventListener("change", resetPreview);
  target.addEventListener("change", resetPreview);
  refresh.addEventListener("click", () => loadSnapshot().catch((error) => setResult(error.message)));
  previewButton.addEventListener("click", () => preview().catch((error) => setResult(error.message)));
  executeButton.addEventListener("click", () => execute().catch((error) => setResult(error.message)));

  populateActions();
  const idempotency = byId("runtimeOwnerActionsIdempotency");
  if (idempotency) idempotency.value = makeKey();
  loadSnapshot().catch((error) => setResult(error.message));
})();
// END PART F 15-B6B THROUGH 15-B6I OWNER ACTIONS AND RECOVERY
