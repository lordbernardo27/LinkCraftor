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
