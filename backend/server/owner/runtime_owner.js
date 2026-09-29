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
