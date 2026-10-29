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

    if (!runtimePage || !subnav || !contentPanel) {
      return false;
    }

    const normalized = normalizeSection(section);

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

    const panels = contentPanel.querySelectorAll(
      "[data-runtime-owner-section-panel]"
    );

    panels.forEach((panel) => {
      const isActive =
        panel.dataset.runtimeOwnerSectionPanel === normalized;

      panel.classList.toggle("active", isActive);
      panel.hidden = !isActive;
    });

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

    runtimeButton.addEventListener("click", openRuntimeTree);
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

        setDisclosure(groupToggle, panel, !expanded);
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
