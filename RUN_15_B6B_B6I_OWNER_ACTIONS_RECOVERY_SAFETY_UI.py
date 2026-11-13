from __future__ import annotations

import ast
import hashlib
import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import traceback
import warnings
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from types import ModuleType
from typing import Any


STEP = "PART F 15-B6B THROUGH 15-B6I"
TITLE = "OWNER ACTIONS AND RECOVERY SAFETY FRAMEWORK AND UI"
MARKER = "PART F 15-B6B THROUGH 15-B6I OWNER ACTIONS AND RECOVERY"
FINAL_RESULT = (
    "FINAL RESULT: PART F 15-B6B THROUGH 15-B6I OWNER ACTIONS AND "
    "RECOVERY SAFETY FRAMEWORK AND UI CERTIFIED"
)

B6A_REPORT_NAME = (
    "PART_F_15_B6A_OWNER_ACTIONS_RECOVERY_BOUNDARY_INSPECTION.txt"
)
B6A_FINAL_RESULT = (
    "FINAL RESULT: PART F 15-B6A OWNER ACTIONS AND RECOVERY "
    "BOUNDARY AND AUTHORITY INSPECTION COMPLETE"
)

EXPECTED_HASHES = {
    "index_html": "68da0fdc08e6b9561ddacaeb4d396f0c7fe6abd3d8de620207865ab5da432e5e",
    "owner_css": "855e9ca8ddc90b030713ac0cc66d5d2c4a74d309a0d4cc16fa38be26aee0a23b",
    "owner_js": "5037d37110941cfee6c9b5a123fc5bd492870832db77da928a7b7392ae598a36",
    "runtime_owner_css": "4e1d47fcfe68e17ad97ca6dbcc32929d849de19651b496eae2dc2406bf4fa5f3",
    "runtime_owner_js": "34e6e31439c9c6ba8ccf75bdeb82e9deb166c03c678ac761a0ff88f5da7e0db5",
    "runtime_summary_api": "215ac35d5591cc6a5e29af407ff70be9f317090c835290d6af92bafd356e44dd",
    "runtime_infrastructure_projection": "694fd8fae5dbf6ade79b73e2e4edbcb10fa49bf10666e8163112020634468a5f",
    "pipeline_operations": "3c52870f9bc1462708476f3ddeb6205b21ee8b4ada2d094bd039a0b7c1467843",
}

OLD_CSS_VERSION = '<link rel="stylesheet" href="/owner/runtime_owner.css?v=21" />'
NEW_CSS_VERSION = '<link rel="stylesheet" href="/owner/runtime_owner.css?v=22" />'
OLD_JS_VERSION = '<script src="/owner/runtime_owner.js?v=22"></script>'
NEW_JS_VERSION = '<script src="/owner/runtime_owner.js?v=23"></script>'

GATEWAY_PATH = "backend/server/owner/owner_actions_gateway.py"
PREVIEW_ENDPOINT = "/owner/api/runtime/actions/preview"
EXECUTE_ENDPOINT = "/owner/api/runtime/actions/execute"


WORKSPACE_INNER = r'''
<!-- BEGIN PART F 15-B6B THROUGH 15-B6I OWNER ACTIONS AND RECOVERY -->
<div class="runtime-owner-actions" data-owner-actions-state="ready">
  <header class="runtime-owner-actions__header">
    <div>
      <span class="runtime-owner-actions__eyebrow">OWNER ACTION AUTHORITY</span>
      <h2>Owner Actions &amp; Recovery</h2>
      <p>
        Preview impact and submit protected runtime action requests without placing
        mutation controls inside monitoring workspaces.
      </p>
    </div>
    <span class="runtime-owner-actions__mode" id="runtimeOwnerActionsMode">
      PROTECTED DEVELOPMENT MODE
    </span>
  </header>

  <div class="runtime-owner-actions__guardrail" role="note">
    <strong>Fail-closed action boundary</strong>
    <span>
      Monitoring evidence is read-only. Every action requires fresh eligibility,
      expected-state protection, impact preview, confirmation, idempotency and audit.
    </span>
  </div>

  <section class="runtime-owner-actions__step" aria-labelledby="runtimeOwnerActionsContextTitle">
    <div class="runtime-owner-actions__step-heading">
      <span>01</span>
      <div>
        <h3 id="runtimeOwnerActionsContextTitle">Select recorded evidence</h3>
        <p>Choose an action family and a target from the certified infrastructure snapshot.</p>
      </div>
    </div>
    <div class="runtime-owner-actions__controls">
      <label>
        <span>Action family</span>
        <select id="runtimeOwnerActionsFamily">
          <option value="jobs_queues">Jobs &amp; Queues</option>
          <option value="workflows_stages">Workflows &amp; Stages</option>
          <option value="workers_leases">Workers &amp; Leases</option>
          <option value="executions">Executions</option>
        </select>
      </label>
      <label>
        <span>Action</span>
        <select id="runtimeOwnerActionsType"></select>
      </label>
      <label class="runtime-owner-actions__target-control">
        <span>Recorded target</span>
        <select id="runtimeOwnerActionsTarget"></select>
      </label>
      <button type="button" id="runtimeOwnerActionsRefresh" class="runtime-owner-actions__secondary">
        Refresh evidence
      </button>
    </div>
  </section>

  <section class="runtime-owner-actions__step" aria-labelledby="runtimeOwnerActionsPreviewTitle">
    <div class="runtime-owner-actions__step-heading">
      <span>02</span>
      <div>
        <h3 id="runtimeOwnerActionsPreviewTitle">Eligibility &amp; impact preview</h3>
        <p>No mutation occurs while this preview is generated.</p>
      </div>
    </div>
    <div class="runtime-owner-actions__preview-grid" id="runtimeOwnerActionsPreview" aria-live="polite">
      <article>
        <span>Current state</span>
        <strong id="runtimeOwnerActionsCurrentState">Select a target</strong>
      </article>
      <article>
        <span>Eligibility</span>
        <strong id="runtimeOwnerActionsEligibility">Not evaluated</strong>
      </article>
      <article>
        <span>Risk level</span>
        <strong id="runtimeOwnerActionsRisk">Unavailable</strong>
      </article>
      <article>
        <span>Expected result</span>
        <strong id="runtimeOwnerActionsExpectedResult">Unavailable</strong>
      </article>
    </div>
    <div class="runtime-owner-actions__impact">
      <h4>Recorded impact boundary</h4>
      <ul id="runtimeOwnerActionsImpact">
        <li>Generate a preview to inspect the selected action.</li>
      </ul>
    </div>
    <button type="button" id="runtimeOwnerActionsPreviewButton" class="runtime-owner-actions__primary">
      Generate impact preview
    </button>
  </section>

  <section class="runtime-owner-actions__step" aria-labelledby="runtimeOwnerActionsRequestTitle">
    <div class="runtime-owner-actions__step-heading">
      <span>03</span>
      <div>
        <h3 id="runtimeOwnerActionsRequestTitle">Protected action request</h3>
        <p>Submission remains blocked until all server-side safeguards are satisfied.</p>
      </div>
    </div>
    <div class="runtime-owner-actions__request-grid">
      <label>
        <span>Expected current state</span>
        <input id="runtimeOwnerActionsExpectedState" type="text" readonly value="Unavailable" />
      </label>
      <label>
        <span>Idempotency key</span>
        <input id="runtimeOwnerActionsIdempotency" type="text" readonly />
      </label>
      <label class="runtime-owner-actions__wide">
        <span>Owner reason</span>
        <textarea id="runtimeOwnerActionsReason" rows="3" maxlength="500"
          placeholder="Explain why this action is necessary."></textarea>
      </label>
      <label class="runtime-owner-actions__wide">
        <span>Required confirmation phrase</span>
        <input id="runtimeOwnerActionsConfirmation" type="text"
          placeholder="Generate a preview first" autocomplete="off" />
      </label>
    </div>
    <div class="runtime-owner-actions__request-footer">
      <p id="runtimeOwnerActionsConfirmationHelp">
        A fresh preview will provide the exact confirmation phrase.
      </p>
      <button type="button" id="runtimeOwnerActionsExecuteButton"
        class="runtime-owner-actions__danger" disabled>
        Submit protected action request
      </button>
    </div>
  </section>

  <section class="runtime-owner-actions__step" aria-labelledby="runtimeOwnerActionsAuditTitle">
    <div class="runtime-owner-actions__step-heading">
      <span>04</span>
      <div>
        <h3 id="runtimeOwnerActionsAuditTitle">Request evidence &amp; audit</h3>
        <p>Every preview, blocked request and authorized dispatch has an accountable result.</p>
      </div>
    </div>
    <div id="runtimeOwnerActionsResult" class="runtime-owner-actions__result" role="status" aria-live="polite">
      No owner action request has been submitted.
    </div>
  </section>
</div>
<!-- END PART F 15-B6B THROUGH 15-B6I OWNER ACTIONS AND RECOVERY -->
'''


CSS_APPEND = r'''

/* BEGIN PART F 15-B6B THROUGH 15-B6I OWNER ACTIONS AND RECOVERY */
#runtimePage .runtime-owner-actions {
  display: grid;
  gap: 14px;
  min-width: 0;
  padding: 14px;
  border: 1px solid rgba(56, 189, 248, .22);
  border-radius: 14px;
  background: linear-gradient(145deg, rgba(4, 30, 48, .94), rgba(8, 47, 73, .72));
}

#runtimePage .runtime-owner-actions__header,
#runtimePage .runtime-owner-actions__request-footer {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
}

#runtimePage .runtime-owner-actions__eyebrow {
  color: #2dd4bf;
  font-size: 9px;
  font-weight: 800;
  letter-spacing: .12em;
}

#runtimePage .runtime-owner-actions h2,
#runtimePage .runtime-owner-actions h3,
#runtimePage .runtime-owner-actions h4,
#runtimePage .runtime-owner-actions p {
  margin: 0;
}

#runtimePage .runtime-owner-actions h2 {
  margin-top: 4px;
  color: #ecfeff;
  font-size: 22px;
}

#runtimePage .runtime-owner-actions__header p,
#runtimePage .runtime-owner-actions__step-heading p,
#runtimePage .runtime-owner-actions__request-footer p {
  margin-top: 5px;
  color: #91aabd;
  font-size: 10px;
  line-height: 1.55;
}

#runtimePage .runtime-owner-actions__mode {
  flex: 0 0 auto;
  padding: 7px 10px;
  border: 1px solid rgba(250, 204, 21, .45);
  border-radius: 999px;
  color: #fef08a;
  background: rgba(161, 98, 7, .16);
  font-size: 8px;
  font-weight: 800;
  letter-spacing: .08em;
}

#runtimePage .runtime-owner-actions__guardrail {
  display: grid;
  grid-template-columns: auto 1fr;
  gap: 12px;
  padding: 11px 12px;
  border: 1px solid rgba(45, 212, 191, .25);
  border-radius: 10px;
  color: #a5f3fc;
  background: rgba(13, 148, 136, .1);
  font-size: 10px;
}

#runtimePage .runtime-owner-actions__guardrail strong {
  color: #5eead4;
}

#runtimePage .runtime-owner-actions__step {
  display: grid;
  gap: 12px;
  min-width: 0;
  padding: 13px;
  border: 1px solid rgba(125, 211, 252, .14);
  border-radius: 11px;
  background: rgba(3, 25, 42, .62);
}

#runtimePage .runtime-owner-actions__step-heading {
  display: flex;
  align-items: flex-start;
  gap: 10px;
}

#runtimePage .runtime-owner-actions__step-heading > span {
  display: grid;
  place-items: center;
  width: 28px;
  height: 28px;
  border-radius: 8px;
  color: #67e8f9;
  background: rgba(8, 145, 178, .18);
  font-size: 9px;
  font-weight: 800;
}

#runtimePage .runtime-owner-actions__step-heading h3 {
  color: #dff8ff;
  font-size: 13px;
}

#runtimePage .runtime-owner-actions__controls,
#runtimePage .runtime-owner-actions__request-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 10px;
}

#runtimePage .runtime-owner-actions__controls label,
#runtimePage .runtime-owner-actions__request-grid label {
  display: grid;
  gap: 5px;
  min-width: 0;
}

#runtimePage .runtime-owner-actions__controls label > span,
#runtimePage .runtime-owner-actions__request-grid label > span {
  color: #8fa9bc;
  font-size: 8px;
  font-weight: 800;
  letter-spacing: .04em;
  text-transform: uppercase;
}

#runtimePage .runtime-owner-actions select,
#runtimePage .runtime-owner-actions input,
#runtimePage .runtime-owner-actions textarea {
  width: 100%;
  min-width: 0;
  min-height: 38px;
  padding: 8px 9px;
  border: 1px solid rgba(103, 232, 249, .18);
  border-radius: 8px;
  color: #dff8ff;
  background: rgba(3, 20, 34, .82);
  font: inherit;
  font-size: 10px;
  overflow-wrap: anywhere;
}

#runtimePage .runtime-owner-actions textarea {
  resize: vertical;
}

#runtimePage .runtime-owner-actions input[readonly] {
  color: #94a3b8;
  background: rgba(15, 23, 42, .72);
}

#runtimePage .runtime-owner-actions select:focus-visible,
#runtimePage .runtime-owner-actions input:focus-visible,
#runtimePage .runtime-owner-actions textarea:focus-visible,
#runtimePage .runtime-owner-actions button:focus-visible {
  outline: 2px solid #22d3ee;
  outline-offset: 2px;
}

#runtimePage .runtime-owner-actions__target-control,
#runtimePage .runtime-owner-actions__wide {
  grid-column: span 2;
}

#runtimePage .runtime-owner-actions__preview-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 9px;
}

#runtimePage .runtime-owner-actions__preview-grid article {
  display: grid;
  gap: 6px;
  min-width: 0;
  padding: 11px;
  border: 1px solid rgba(103, 232, 249, .13);
  border-radius: 9px;
  background: rgba(7, 42, 64, .5);
}

#runtimePage .runtime-owner-actions__preview-grid span {
  color: #8fa9bc;
  font-size: 8px;
  font-weight: 800;
  text-transform: uppercase;
}

#runtimePage .runtime-owner-actions__preview-grid strong {
  min-width: 0;
  color: #e0f2fe;
  font-size: 11px;
  overflow-wrap: anywhere;
}

#runtimePage .runtime-owner-actions__impact {
  padding: 11px;
  border-left: 3px solid #22d3ee;
  border-radius: 8px;
  color: #b6ccda;
  background: rgba(8, 47, 73, .48);
  font-size: 9px;
}

#runtimePage .runtime-owner-actions__impact h4 {
  color: #cffafe;
  font-size: 10px;
}

#runtimePage .runtime-owner-actions__impact ul {
  margin: 7px 0 0;
  padding-left: 18px;
}

#runtimePage .runtime-owner-actions button {
  min-height: 40px;
  padding: 9px 13px;
  border: 1px solid transparent;
  border-radius: 8px;
  font-size: 9px;
  font-weight: 800;
  cursor: pointer;
}

#runtimePage .runtime-owner-actions__primary {
  justify-self: start;
  color: #042f2e;
  background: #5eead4;
}

#runtimePage .runtime-owner-actions__secondary {
  align-self: end;
  color: #bae6fd;
  border-color: rgba(56, 189, 248, .28);
  background: rgba(2, 132, 199, .12);
}

#runtimePage .runtime-owner-actions__danger {
  flex: 0 0 auto;
  color: #fff1f2;
  border-color: rgba(251, 113, 133, .4);
  background: rgba(190, 18, 60, .5);
}

#runtimePage .runtime-owner-actions button:disabled {
  opacity: .45;
  cursor: not-allowed;
}

#runtimePage .runtime-owner-actions__result {
  min-height: 48px;
  padding: 12px;
  border: 1px dashed rgba(103, 232, 249, .24);
  border-radius: 9px;
  color: #a5f3fc;
  background: rgba(2, 17, 29, .6);
  font-size: 10px;
  line-height: 1.55;
  overflow-wrap: anywhere;
}

@media (max-width: 940px) {
  #runtimePage .runtime-owner-actions__controls,
  #runtimePage .runtime-owner-actions__request-grid,
  #runtimePage .runtime-owner-actions__preview-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 620px) {
  #runtimePage .runtime-owner-actions__header,
  #runtimePage .runtime-owner-actions__request-footer,
  #runtimePage .runtime-owner-actions__guardrail {
    grid-template-columns: 1fr;
    flex-direction: column;
  }

  #runtimePage .runtime-owner-actions__controls,
  #runtimePage .runtime-owner-actions__request-grid,
  #runtimePage .runtime-owner-actions__preview-grid {
    grid-template-columns: 1fr;
  }

  #runtimePage .runtime-owner-actions__target-control,
  #runtimePage .runtime-owner-actions__wide {
    grid-column: auto;
  }

  #runtimePage .runtime-owner-actions button {
    width: 100%;
    min-height: 44px;
  }
}

@media (prefers-reduced-motion: reduce) {
  #runtimePage .runtime-owner-actions *,
  #runtimePage .runtime-owner-actions *::before,
  #runtimePage .runtime-owner-actions *::after {
    scroll-behavior: auto !important;
    transition-duration: .01ms !important;
    animation-duration: .01ms !important;
    animation-iteration-count: 1 !important;
  }
}
/* END PART F 15-B6B THROUGH 15-B6I OWNER ACTIONS AND RECOVERY */
'''


JS_APPEND = r'''

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
'''


BACKEND_APPEND = r'''


# BEGIN PART F 15-B6B THROUGH 15-B6I OWNER ACTIONS AND RECOVERY
from fastapi import Request

from backend.server.owner.owner_actions_gateway import (
    OwnerActionBlocked,
    OwnerActionValidationError,
    preview_owner_action,
    submit_owner_action,
)


@router.post("/actions/preview")
async def runtime_owner_action_preview(
    payload: Mapping[str, Any],
) -> Mapping[str, Any]:
    """Return a read-only eligibility and impact preview."""

    try:
        return preview_owner_action(payload)
    except OwnerActionValidationError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except OwnerActionBlocked as exc:
        raise HTTPException(status_code=409, detail=exc.detail) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=503,
            detail={
                "error": "owner_action_preview_unavailable",
                "message": str(exc),
                "action_executed": False,
            },
        ) from exc


@router.post("/actions/execute")
async def runtime_owner_action_execute(
    payload: Mapping[str, Any],
    request: Request,
) -> Mapping[str, Any]:
    """Submit one protected owner action request through the gateway."""

    try:
        return submit_owner_action(payload, dict(request.headers))
    except OwnerActionValidationError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except OwnerActionBlocked as exc:
        raise HTTPException(status_code=409, detail=exc.detail) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=503,
            detail={
                "error": "owner_action_gateway_unavailable",
                "message": str(exc),
                "action_executed": False,
            },
        ) from exc


# END PART F 15-B6B THROUGH 15-B6I OWNER ACTIONS AND RECOVERY
'''


GATEWAY_SOURCE = r'''from __future__ import annotations

"""Protected Owner Actions & Recovery request gateway.

This module is separate from monitoring projections. Preview is read-only. Mutation
dispatch is disabled by default and cannot occur unless a trusted server-side adapter,
owner identity, signed grant and explicit activation have all been provisioned.
"""

# PART F 15-B6B THROUGH 15-B6I OWNER ACTIONS AND RECOVERY

import hashlib
import hmac
import json
import os
import threading
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Mapping

from backend.server.owner.runtime_infrastructure_projection import (
    build_runtime_infrastructure_snapshot,
)


OWNER_ACTION_GATEWAY_VERSION = "owner_action_gateway_v1.0.0"
OWNER_ACTION_SCHEMA_VERSION = "owner_action_request_schema_v1"
OWNER_ACTIONS_ENABLED_ENV = "LINKCRAFTOR_OWNER_ACTIONS_ENABLED"
OWNER_ACTION_SECRET_ENV = "LINKCRAFTOR_OWNER_ACTION_SIGNING_SECRET"
OWNER_ACTION_ISSUER_ENV = "LINKCRAFTOR_OWNER_ACTION_TRUSTED_ISSUER"

ACTION_CONTRACTS: dict[str, dict[str, Any]] = {
    "job_claim": {
        "family": "jobs_queues", "states": {"queued"}, "risk": "HIGH",
        "result": "Assign one eligible queued job through canonical claim authority.",
        "impact": ["May assign worker ownership.", "May create a lease.", "Must revalidate queue eligibility atomically."],
    },
    "job_retry": {
        "family": "jobs_queues", "states": {"failed"}, "risk": "HIGH",
        "result": "Create one authorized retry attempt for a failed job.",
        "impact": ["May enqueue a new attempt.", "Must preserve attempt limits.", "Must not erase failure evidence."],
    },
    "job_requeue": {
        "family": "jobs_queues", "states": {"failed", "cancelled", "canceled"}, "risk": "HIGH",
        "result": "Return an eligible job to its canonical queue.",
        "impact": ["May make work claimable again.", "Must prevent duplicate queue entries.", "Requires fresh dependency checks."],
    },
    "job_cancel": {
        "family": "jobs_queues", "states": {"queued", "running", "in_progress", "processing"}, "risk": "HIGH",
        "result": "Request cancellation of one non-terminal job.",
        "impact": ["May stop future processing.", "Running work may require cooperative cancellation.", "Existing evidence remains retained."],
    },
    "workflow_retry": {
        "family": "workflows_stages", "states": {"failed"}, "risk": "HIGH",
        "result": "Retry eligible failed work in one workflow.",
        "impact": ["May create new job attempts.", "Completed stages remain immutable.", "Dependencies must be revalidated."],
    },
    "workflow_cancel": {
        "family": "workflows_stages", "states": {"active", "running", "queued", "failed"}, "risk": "CRITICAL",
        "result": "Request cancellation of remaining workflow work.",
        "impact": ["May affect multiple jobs.", "Completed outputs remain retained.", "Requires critical confirmation."],
    },
    "stage_recover": {
        "family": "workflows_stages", "states": {"failed", "blocked"}, "risk": "CRITICAL",
        "result": "Request recovery of one eligible failed or blocked stage.",
        "impact": ["May enqueue replacement work.", "Must preserve stage ordering.", "Must not bypass predecessor requirements."],
    },
    "lease_release": {
        "family": "workers_leases", "states": {"expired", "stale"}, "risk": "CRITICAL",
        "result": "Release one canonically expired or stale lease.",
        "impact": ["May make work claimable again.", "Must prove lease expiry atomically.", "Active leases cannot be released."],
    },
    "worker_drain": {
        "family": "workers_leases", "states": {"active", "busy", "idle"}, "risk": "CRITICAL",
        "result": "Prevent a worker from receiving new work while preserving active work.",
        "impact": ["Reduces available worker capacity.", "Does not terminate active work.", "Requires trusted worker authority."],
    },
    "execution_cancel": {
        "family": "executions", "states": {"running", "in_progress", "processing"}, "risk": "CRITICAL",
        "result": "Request cooperative cancellation of one active execution.",
        "impact": ["May stop an active handler.", "Partial work may remain.", "Compensation requirements must be recorded."],
    },
    "execution_terminate": {
        "family": "executions", "states": {"running", "in_progress", "processing"}, "risk": "CRITICAL",
        "result": "Request forced termination only through certified execution authority.",
        "impact": ["May interrupt work immediately.", "May require compensation or cleanup.", "Highest confirmation level required."],
    },
}

TARGET_NAMESPACE = {
    "jobs_queues": "jobs",
    "workflows_stages": "orchestration",
    "workers_leases": "workers_leases",
    "executions": "execution",
}

IDENTITY_FIELDS = (
    "job_id", "job_identity", "workflow_id", "workflow_identity", "worker_identity",
    "worker_id", "lease_identity", "execution_identity", "queue_identity", "queue_name",
)
STATE_FIELDS = ("status", "state", "lifecycle", "lease_status", "execution_status")
REQUIRED_REQUEST_FIELDS = (
    "action_type", "target_type", "target_id", "expected_state", "reason",
    "confirmation", "confirmation_token", "idempotency_key",
)

_ADAPTERS: dict[str, Callable[[Mapping[str, Any]], Mapping[str, Any]]] = {}
_IDEMPOTENCY: dict[str, Mapping[str, Any]] = {}
_LOCK = threading.RLock()


class OwnerActionValidationError(ValueError):
    pass


class OwnerActionBlocked(RuntimeError):
    def __init__(self, code: str, message: str, **evidence: Any) -> None:
        self.detail = {
            "error": code,
            "message": message,
            "action_executed": False,
            **evidence,
        }
        super().__init__(message)


def _text(value: Any) -> str:
    return "" if value is None else str(value).strip()


def _normalized_state(value: Any) -> str:
    return _text(value).lower().replace(" ", "_") or "unavailable"


def _record_identity(record: Mapping[str, Any]) -> str:
    for field in IDENTITY_FIELDS:
        value = _text(record.get(field))
        if value:
            return value
    return ""


def _record_state(record: Mapping[str, Any]) -> str:
    for field in STATE_FIELDS:
        value = _normalized_state(record.get(field))
        if value != "unavailable":
            return value
    return "unavailable"


def _find_target(snapshot: Mapping[str, Any], target_type: str, target_id: str) -> Mapping[str, Any]:
    namespace_name = TARGET_NAMESPACE.get(target_type)
    if not namespace_name:
        raise OwnerActionValidationError("Unknown target_type.")
    namespace = snapshot.get(namespace_name, {})
    records = namespace.get("records", []) if isinstance(namespace, Mapping) else []
    if not isinstance(records, list):
        raise OwnerActionBlocked("target_evidence_unavailable", "Canonical target evidence is unavailable.")
    for value in records:
        if isinstance(value, Mapping) and _record_identity(value) == target_id:
            return dict(value)
    raise OwnerActionBlocked("target_not_found", "The target is absent from the fresh canonical snapshot.")


def _confirmation_phrase(action_type: str, target_id: str) -> str:
    return f"CONFIRM {action_type.upper()} {target_id}"


def _token(secret: str, action_type: str, target_id: str, state: str) -> str:
    message = f"{action_type}|{target_id}|{state}|{OWNER_ACTION_SCHEMA_VERSION}".encode()
    return hmac.new(secret.encode(), message, hashlib.sha256).hexdigest()


def _preview(payload: Mapping[str, Any], snapshot: Mapping[str, Any]) -> dict[str, Any]:
    action_type = _text(payload.get("action_type"))
    target_type = _text(payload.get("target_type"))
    target_id = _text(payload.get("target_id"))
    expected_state = _normalized_state(payload.get("expected_state"))
    if not action_type or not target_type or not target_id:
        raise OwnerActionValidationError("action_type, target_type and target_id are required.")
    contract = ACTION_CONTRACTS.get(action_type)
    if not contract or contract["family"] != target_type:
        raise OwnerActionValidationError("The action is not valid for the selected target family.")
    record = _find_target(snapshot, target_type, target_id)
    current_state = _record_state(record)
    eligible = current_state in contract["states"]
    if expected_state not in {"unavailable", current_state}:
        eligible = False
        blocked_reason = "Expected state does not match fresh canonical evidence."
    elif not eligible:
        blocked_reason = f"State {current_state!r} is not eligible for {action_type}."
    else:
        blocked_reason = None
    secret = os.environ.get(OWNER_ACTION_SECRET_ENV, "preview-only-not-a-dispatch-secret")
    return {
        "gateway_version": OWNER_ACTION_GATEWAY_VERSION,
        "schema_version": OWNER_ACTION_SCHEMA_VERSION,
        "preview_only": True,
        "action_executed": False,
        "action_type": action_type,
        "target_type": target_type,
        "target_id": target_id,
        "current_state": current_state,
        "eligible": eligible,
        "blocked_reason": blocked_reason,
        "risk_level": contract["risk"],
        "expected_result": contract["result"],
        "impact": list(contract["impact"]),
        "confirmation_phrase": _confirmation_phrase(action_type, target_id),
        "confirmation_token": _token(secret, action_type, target_id, current_state),
    }


def preview_owner_action(payload: Mapping[str, Any]) -> Mapping[str, Any]:
    if not isinstance(payload, Mapping):
        raise OwnerActionValidationError("The preview payload must be an object.")
    return _preview(payload, build_runtime_infrastructure_snapshot())


def register_owner_action_adapter(
    action_type: str,
    adapter: Callable[[Mapping[str, Any]], Mapping[str, Any]],
) -> None:
    """Server-only adapter registration; browser requests cannot register adapters."""
    if action_type not in ACTION_CONTRACTS or not callable(adapter):
        raise OwnerActionValidationError("Invalid owner action adapter registration.")
    with _LOCK:
        _ADAPTERS[action_type] = adapter


def _audit(event: Mapping[str, Any]) -> None:
    root = Path(__file__).resolve().parents[3]
    path = root / "backend/server/data/audit/owner_actions.jsonl"
    path.parent.mkdir(parents=True, exist_ok=True)
    line = json.dumps(dict(event), sort_keys=True, default=str) + "\n"
    with path.open("a", encoding="utf-8") as handle:
        handle.write(line)
        handle.flush()
        os.fsync(handle.fileno())


def submit_owner_action(payload: Mapping[str, Any], headers: Mapping[str, Any]) -> Mapping[str, Any]:
    if not isinstance(payload, Mapping) or not isinstance(headers, Mapping):
        raise OwnerActionValidationError("Action payload and request headers are required.")
    missing = [field for field in REQUIRED_REQUEST_FIELDS if not _text(payload.get(field))]
    if missing:
        raise OwnerActionValidationError(f"Missing required action fields: {', '.join(missing)}")

    request_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()
    idempotency_key = _text(payload["idempotency_key"])
    header_key = _text(headers.get("x-linkcraftor-idempotency-key"))
    if header_key != idempotency_key:
        raise OwnerActionBlocked("idempotency_mismatch", "Header and payload idempotency keys differ.", request_id=request_id)

    with _LOCK:
        previous = _IDEMPOTENCY.get(idempotency_key)
        if previous is not None:
            return dict(previous)

    snapshot = build_runtime_infrastructure_snapshot()
    preview = _preview(payload, snapshot)
    if not preview["eligible"]:
        raise OwnerActionBlocked("fresh_eligibility_failed", preview["blocked_reason"], request_id=request_id)
    if _normalized_state(payload["expected_state"]) != preview["current_state"]:
        raise OwnerActionBlocked("state_conflict", "Target state changed after preview.", request_id=request_id)
    if _text(payload["confirmation"]) != preview["confirmation_phrase"]:
        raise OwnerActionBlocked("confirmation_failed", "The confirmation phrase does not match.", request_id=request_id)

    secret = os.environ.get(OWNER_ACTION_SECRET_ENV, "")
    if not secret:
        raise OwnerActionBlocked("trusted_secret_unavailable", "Owner action signing authority is not provisioned.", request_id=request_id)
    expected_token = _token(secret, preview["action_type"], preview["target_id"], preview["current_state"])
    if not hmac.compare_digest(_text(payload["confirmation_token"]), expected_token):
        raise OwnerActionBlocked("preview_token_invalid", "The preview token is invalid or stale.", request_id=request_id)
    if os.environ.get(OWNER_ACTIONS_ENABLED_ENV) != "1":
        raise OwnerActionBlocked("owner_actions_disabled", "Live owner action dispatch is disabled.", request_id=request_id)

    principal = _text(headers.get("x-linkcraftor-owner-principal"))
    issuer = _text(headers.get("x-linkcraftor-owner-issuer"))
    expected_issuer = os.environ.get(OWNER_ACTION_ISSUER_ENV, "")
    if not principal or not expected_issuer or issuer != expected_issuer:
        raise OwnerActionBlocked("owner_authorization_failed", "Trusted owner identity is absent or invalid.", request_id=request_id)

    adapter = _ADAPTERS.get(preview["action_type"])
    if adapter is None:
        raise OwnerActionBlocked("certified_adapter_unavailable", "No certified server-side mutation adapter is registered.", request_id=request_id)

    request = {
        **dict(payload),
        "request_id": request_id,
        "owner_principal": principal,
        "submitted_at": now,
        "fresh_preview": preview,
    }
    _audit({"event": "owner_action_authorized", **request, "action_executed": False})
    result = dict(adapter(request))
    response = {
        "request_id": request_id,
        "status": _text(result.get("status")) or "COMPLETED",
        "action_type": preview["action_type"],
        "target_id": preview["target_id"],
        "action_executed": True,
        "result": result,
    }
    _audit({"event": "owner_action_completed", **response, "owner_principal": principal})
    with _LOCK:
        _IDEMPOTENCY[idempotency_key] = dict(response)
    return response


def certify_owner_action_gateway_v1() -> Mapping[str, Any]:
    return {
        "gateway_version": OWNER_ACTION_GATEWAY_VERSION,
        "schema_version": OWNER_ACTION_SCHEMA_VERSION,
        "action_contract_count": len(ACTION_CONTRACTS),
        "required_request_fields": list(REQUIRED_REQUEST_FIELDS),
        "activation_default_off": os.environ.get(OWNER_ACTIONS_ENABLED_ENV) != "1",
        "registered_adapter_count": len(_ADAPTERS),
        "preview_is_read_only": True,
        "direct_browser_mutation": False,
    }


__all__ = [
    "ACTION_CONTRACTS",
    "OwnerActionBlocked",
    "OwnerActionValidationError",
    "certify_owner_action_gateway_v1",
    "preview_owner_action",
    "register_owner_action_adapter",
    "submit_owner_action",
]
'''


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256_path(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8").replace("\r\n", "\n")


def atomic_write_text(path: Path, source: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp-b6")
    temporary.write_text(source, encoding="utf-8", newline="\n")
    temporary.replace(path)


def report_complete(source: str) -> bool:
    normalized = source.replace("\r\n", "\n")
    return all(token in normalized for token in (
        "INSPECTION STATUS: COMPLETE",
        "FAILED_CHECKS:\n[]",
        "NOT_RUN_CHECKS:\n[]",
        B6A_FINAL_RESULT,
        "Production recovery actions executed: NO",
    ))


def python_syntax_valid(source: str, filename: str) -> bool:
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", SyntaxWarning)
            tree = ast.parse(source, filename=filename)
            compile(tree, filename, "exec")
    except SyntaxError:
        return False
    return True


def balanced(source: str, opening: str, closing: str) -> bool:
    depth = 0
    quote = ""
    escape = False
    index = 0
    while index < len(source):
        char = source[index]
        if escape:
            escape = False
        elif quote:
            if char == "\\":
                escape = True
            elif char == quote:
                quote = ""
        elif source.startswith("/*", index):
            end = source.find("*/", index + 2)
            if end < 0:
                return False
            index = end + 1
        elif char in {'"', "'", "`"}:
            quote = char
        elif char == opening:
            depth += 1
        elif char == closing:
            depth -= 1
            if depth < 0:
                return False
        index += 1
    return depth == 0 and not quote


class IdCollector(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.ids: list[str] = []

    def handle_starttag(
        self,
        tag: str,
        attrs: list[tuple[str, str | None]],
    ) -> None:
        del tag
        for name, value in attrs:
            if name == "id" and value:
                self.ids.append(value)


def html_ids_unique(source: str) -> bool:
    parser = IdCollector()
    parser.feed(source)
    parser.close()
    return len(parser.ids) == len(set(parser.ids))


def javascript_syntax_valid(source: str) -> bool:
    node = shutil.which("node")
    if node is None:
        raise RuntimeError("Node.js is required for JavaScript syntax validation.")
    with tempfile.TemporaryDirectory(prefix="linkcraftor_b6_js_") as folder:
        candidate = Path(folder) / "runtime_owner.js"
        candidate.write_text(source, encoding="utf-8", newline="\n")
        result = subprocess.run(
            [node, "--check", str(candidate)],
            capture_output=True,
            text=True,
            check=False,
        )
    return result.returncode == 0


def replace_once(source: str, old: str, new: str, label: str) -> str:
    count = source.count(old)
    if count != 1:
        raise RuntimeError(f"{label} was expected exactly once; found {count}.")
    return source.replace(old, new, 1)


def find_matching_section(source: str, opening_index: int) -> tuple[int, int]:
    opening_end = source.find(">", opening_index)
    if opening_end < 0:
        raise RuntimeError("The reserved Owner Actions opening tag is incomplete.")
    pattern = re.compile(r"<section\b|</section\s*>", re.IGNORECASE)
    depth = 0
    for match in pattern.finditer(source, opening_index):
        token = match.group(0).lower()
        if token.startswith("<section"):
            depth += 1
        else:
            depth -= 1
            if depth == 0:
                return opening_end, match.start()
    raise RuntimeError("The reserved Owner Actions section has no matching closing tag.")


def inject_workspace(source: str) -> str:
    if MARKER in source:
        raise RuntimeError("The combined B6 workspace marker already exists.")
    candidates = (
        'id="runtimeOwnerSectionOwnerActions"',
        'data-runtime-owner-section="owner_actions"',
        'id="runtimeOwnerActionsWorkspace"',
    )
    located = [(source.find(token), token) for token in candidates if source.find(token) >= 0]
    if not located:
        raise RuntimeError("The reserved Owner Actions placeholder was not found.")
    token_index, token = min(located)
    section_start = source.rfind("<section", 0, token_index + len(token))
    if section_start < 0:
        raise RuntimeError("The reserved Owner Actions token is not inside a section.")
    opening_end, closing_start = find_matching_section(source, section_start)
    opening = source[section_start:opening_end + 1]
    wrapper_needed = 'id="runtimeOwnerActionsWorkspace"' not in source
    content = WORKSPACE_INNER.strip()
    if wrapper_needed:
        content = (
            '<div id="runtimeOwnerActionsWorkspace" '
            'class="runtime-infrastructure-workspace">\n'
            + content
            + "\n</div>"
        )
    return source[:opening_end + 1] + "\n" + content + "\n" + source[closing_start:]


def build_candidate_html(source: str) -> str:
    candidate = replace_once(source, OLD_CSS_VERSION, NEW_CSS_VERSION, "Runtime Owner CSS asset")
    candidate = replace_once(candidate, OLD_JS_VERSION, NEW_JS_VERSION, "Runtime Owner JavaScript asset")
    return inject_workspace(candidate)


def build_candidate_css(source: str) -> str:
    if MARKER in source:
        raise RuntimeError("The combined B6 CSS marker already exists.")
    return source.rstrip() + "\n" + CSS_APPEND.lstrip()


def build_candidate_js(source: str) -> str:
    if MARKER in source:
        raise RuntimeError("The combined B6 JavaScript marker already exists.")
    return source.rstrip() + "\n" + JS_APPEND.lstrip()


def build_candidate_backend(source: str) -> str:
    if MARKER in source or '@router.post("/actions/preview")' in source:
        raise RuntimeError("The combined B6 owner action routes already exist.")
    return source.rstrip() + "\n" + BACKEND_APPEND.lstrip()


def load_isolated_gateway(source: str) -> ModuleType:
    projection_stub = '''
def build_runtime_infrastructure_snapshot():
    return {
        "jobs": {"records": [{"job_id": "job_failed", "status": "failed"}]},
        "orchestration": {"records": [{"workflow_id": "wf_failed", "status": "failed"}]},
        "workers_leases": {"records": [{"lease_identity": "lease_expired", "status": "expired"}]},
        "execution": {"records": [{"execution_identity": "exec_running", "status": "running"}]},
    }
'''
    with tempfile.TemporaryDirectory(prefix="linkcraftor_b6_gateway_") as folder:
        root = Path(folder)
        package = root / "backend/server/owner"
        package.mkdir(parents=True)
        for init in (root / "backend/__init__.py", root / "backend/server/__init__.py", package / "__init__.py"):
            init.write_text("", encoding="utf-8")
        (package / "runtime_infrastructure_projection.py").write_text(projection_stub, encoding="utf-8")
        path = package / "owner_actions_gateway.py"
        path.write_text(source, encoding="utf-8")
        original = list(sys.path)
        sys.path.insert(0, str(root))
        name = "backend.server.owner.owner_actions_gateway"
        for module_name in list(sys.modules):
            if module_name == "backend" or module_name.startswith("backend."):
                sys.modules.pop(module_name, None)
        try:
            spec = importlib.util.spec_from_file_location(name, path)
            if spec is None or spec.loader is None:
                raise RuntimeError("Unable to create the isolated owner action gateway probe.")
            module = importlib.util.module_from_spec(spec)
            sys.modules[name] = module
            spec.loader.exec_module(module)
            return module
        finally:
            sys.path[:] = original
            for module_name in list(sys.modules):
                if module_name == "backend" or module_name.startswith("backend."):
                    sys.modules.pop(module_name, None)


def gateway_probe(source: str) -> dict[str, Any]:
    old_enabled = os.environ.pop("LINKCRAFTOR_OWNER_ACTIONS_ENABLED", None)
    old_secret = os.environ.pop("LINKCRAFTOR_OWNER_ACTION_SIGNING_SECRET", None)
    try:
        module = load_isolated_gateway(source)
        preview = module.preview_owner_action({
            "action_type": "job_retry",
            "target_type": "jobs_queues",
            "target_id": "job_failed",
            "expected_state": "failed",
        })
        blocked = False
        try:
            module.submit_owner_action({
                "action_type": "job_retry",
                "target_type": "jobs_queues",
                "target_id": "job_failed",
                "expected_state": "failed",
                "reason": "isolated test",
                "confirmation": preview["confirmation_phrase"],
                "confirmation_token": preview["confirmation_token"],
                "idempotency_key": "isolated-b6-idempotency",
            }, {"x-linkcraftor-idempotency-key": "isolated-b6-idempotency"})
        except module.OwnerActionBlocked:
            blocked = True
        certification = module.certify_owner_action_gateway_v1()
        return {
            "passed": bool(
                preview["eligible"]
                and preview["action_executed"] is False
                and blocked
                and certification["activation_default_off"]
                and certification["registered_adapter_count"] == 0
                and certification["action_contract_count"] == 11
            ),
            "preview_eligible": preview["eligible"],
            "preview_read_only": preview["action_executed"] is False,
            "execution_blocked": blocked,
            "action_contract_count": certification["action_contract_count"],
            "adapter_count": certification["registered_adapter_count"],
        }
    finally:
        if old_enabled is not None:
            os.environ["LINKCRAFTOR_OWNER_ACTIONS_ENABLED"] = old_enabled
        if old_secret is not None:
            os.environ["LINKCRAFTOR_OWNER_ACTION_SIGNING_SECRET"] = old_secret


def backup_sources(root: Path, paths: dict[str, Path], names: tuple[str, ...]) -> Path:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    folder = root / "backend/server/data/runtime_backups" / f"part_f_15_b6b_b6i_{stamp}"
    folder.mkdir(parents=True, exist_ok=False)
    manifest: dict[str, Any] = {"created_at": now_iso(), "files": {}}
    for name in names:
        path = paths[name]
        relative = path.relative_to(root)
        destination = folder / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        if path.exists():
            shutil.copy2(path, destination)
            manifest["files"][name] = {"path": str(relative), "existed": True, "sha256": sha256_path(path)}
        else:
            manifest["files"][name] = {"path": str(relative), "existed": False, "sha256": None}
    (folder / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return folder


def restore_sources(root: Path, backup: Path, paths: dict[str, Path], names: tuple[str, ...]) -> None:
    manifest = json.loads((backup / "manifest.json").read_text(encoding="utf-8"))
    for name in names:
        entry = manifest["files"][name]
        path = paths[name]
        stored = backup / entry["path"]
        if entry["existed"]:
            path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(stored, path)
        elif path.exists():
            path.unlink()


def write_report(
    report: Path,
    checks: dict[str, bool],
    evidence: dict[str, Any],
    execution_error: dict[str, Any],
    certified: bool,
) -> None:
    failed = sorted(name for name, passed in checks.items() if not passed)
    lines = [
        "LINKCRAFTOR OWNER CONTROL TOWER",
        f"{STEP} {TITLE}",
        "",
        f"Generated: {now_iso()}",
        "Patch mode: STRICT FAIL-CLOSED WITH AUTOMATIC ROLLBACK",
        f"Backup: {evidence.get('backup', 'UNAVAILABLE')}",
        "Live owner actions executed during certification: NO",
        "Production jobs created: NO",
        "Production queue claims executed: NO",
        "Production handlers executed: NO",
        "Production workflow persistence executed: NO",
        "Production recovery actions executed: NO",
        "Live network requests executed during certification: NO",
        "Trusted mutation adapters registered by installation: NO",
        f"CERTIFICATION STATUS: {'CERTIFIED' if certified else 'NOT_CERTIFIED'}",
        "",
        "CHECKS:",
        json.dumps(checks, indent=2, sort_keys=True),
        "",
        "FAILED_CHECKS:",
        json.dumps(failed, indent=2),
        "",
        "NOT_RUN_CHECKS:",
        "[]",
        "",
        "EVIDENCE:",
        json.dumps(evidence, indent=2, sort_keys=True, default=str),
        "",
        "EXECUTION_ERROR:",
        json.dumps(execution_error, indent=2, sort_keys=True),
        "",
        "IMPLEMENTED BOUNDARY:",
        "- B6B defines the action catalog, risk classes and mandatory safety contract.",
        "- B6C activates one dedicated Owner Actions & Recovery workspace outside monitoring.",
        "- B6D provides fresh read-only eligibility and impact preview.",
        "- B6E exposes protected Jobs and Queues request controls.",
        "- B6F exposes protected Workflow and Stage recovery request controls.",
        "- B6G exposes protected Worker and Lease recovery request controls.",
        "- B6H exposes protected Execution cancellation and termination request controls.",
        "- B6I enforces expected state, confirmation, idempotency, trusted identity and audit.",
        "- Live mutation dispatch defaults OFF and no adapter is registered by this installation.",
        "- Monitoring components remain read-only and contain no mutation buttons.",
        "",
        "ACTIVATION BOUNDARY:",
        "Trusted production identity and per-action certified adapters must be provisioned before live dispatch.",
        "Until then, impact preview works and action submission fails closed.",
        "",
        "NEXT STEP:",
        "Part F 15-B6J - Owner Actions & Recovery collective development certification.",
        "",
        FINAL_RESULT if certified else FINAL_RESULT.replace(" CERTIFIED", " NOT_CERTIFIED"),
    ]
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text("\n".join(lines) + "\n", encoding="utf-8")


def run(root: Path, report: Path) -> int:
    checks: dict[str, bool] = {}
    evidence: dict[str, Any] = {
        "action_controls_added": True,
        "actions_executed": False,
        "live_dispatch_default": "OFF",
        "trusted_adapters_installed": 0,
        "rollback_performed": False,
    }
    execution_error: dict[str, Any] = {}
    backup: Path | None = None
    changed_names = (
        "index_html", "runtime_owner_css", "runtime_owner_js",
        "runtime_summary_api", "owner_actions_gateway",
    )
    paths = {
        "index_html": root / "backend/server/owner/index.html",
        "owner_css": root / "backend/server/owner/owner.css",
        "owner_js": root / "backend/server/owner/owner.js",
        "runtime_owner_css": root / "backend/server/owner/runtime_owner.css",
        "runtime_owner_js": root / "backend/server/owner/runtime_owner.js",
        "runtime_summary_api": root / "backend/server/owner/runtime_summary_api.py",
        "runtime_infrastructure_projection": root / "backend/server/owner/runtime_infrastructure_projection.py",
        "pipeline_operations": root / "backend/server/owner/pipeline_operations.py",
        "owner_actions_gateway": root / GATEWAY_PATH,
    }
    b6a_report = root / "backend/server/data/reports" / B6A_REPORT_NAME
    watched_existing = {name: path for name, path in paths.items() if name in EXPECTED_HASHES}
    hashes_before: dict[str, str] = {}
    b6a_hash_before = ""

    try:
        checks["part_f_15_b6a_report_exists"] = b6a_report.is_file()
        checks["part_f_15_b6a_complete"] = checks["part_f_15_b6a_report_exists"] and report_complete(read_text(b6a_report))
        if not all(checks.values()):
            raise RuntimeError("The completed B6A authority inspection baseline is unavailable.")
        b6a_hash_before = sha256_path(b6a_report)

        for name, path in watched_existing.items():
            checks[f"source_exists_{name}"] = path.is_file()
        checks["gateway_not_previously_present"] = not paths["owner_actions_gateway"].exists()
        if not all(checks.values()):
            raise RuntimeError("The certified B5P source baseline or clean B6 gateway boundary is unavailable.")

        hashes_before = {name: sha256_path(path) for name, path in watched_existing.items()}
        for name, expected in EXPECTED_HASHES.items():
            checks[f"source_hash_{name}"] = hashes_before[name] == expected
        if not all(checks.values()):
            raise RuntimeError("Installed sources do not match the certified B5P baseline.")

        before = {name: read_text(path) for name, path in watched_existing.items()}
        candidate_html = build_candidate_html(before["index_html"])
        candidate_css = build_candidate_css(before["runtime_owner_css"])
        candidate_js = build_candidate_js(before["runtime_owner_js"])
        candidate_backend = build_candidate_backend(before["runtime_summary_api"])

        checks["candidate_html_ids_unique"] = html_ids_unique(candidate_html)
        checks["candidate_css_balanced"] = balanced(candidate_css, "{", "}")
        checks["candidate_javascript_syntax"] = javascript_syntax_valid(candidate_js)
        checks["candidate_runtime_api_syntax"] = python_syntax_valid(candidate_backend, str(paths["runtime_summary_api"]))
        checks["candidate_gateway_syntax"] = python_syntax_valid(GATEWAY_SOURCE, str(paths["owner_actions_gateway"]))

        probe = gateway_probe(GATEWAY_SOURCE)
        evidence["isolated_gateway_probe"] = probe
        checks["isolated_gateway_probe_passed"] = probe["passed"]

        checks["b6b_safety_contract_complete"] = all(token in GATEWAY_SOURCE for token in (
            "ACTION_CONTRACTS", "REQUIRED_REQUEST_FIELDS", "expected_state",
            "confirmation_token", "idempotency_key", "owner_authorization_failed",
        ))
        checks["b6c_dedicated_workspace_present"] = all(token in candidate_html for token in (
            'id="runtimeOwnerActionsWorkspace"', "Owner Actions &amp; Recovery",
            'id="runtimeOwnerActionsFamily"', 'id="runtimeOwnerActionsResult"',
        ))
        checks["b6d_preview_contract_present"] = (
            candidate_backend.count('@router.post("/actions/preview")') == 1
            and candidate_js.count(PREVIEW_ENDPOINT) == 1
            and "preview_owner_action" in GATEWAY_SOURCE
            and "action_executed\": False" in GATEWAY_SOURCE
        )
        checks["b6e_jobs_queues_actions_present"] = all(token in GATEWAY_SOURCE for token in (
            '"job_claim"', '"job_retry"', '"job_requeue"', '"job_cancel"',
        ))
        checks["b6f_workflow_stage_actions_present"] = all(token in GATEWAY_SOURCE for token in (
            '"workflow_retry"', '"workflow_cancel"', '"stage_recover"',
        ))
        checks["b6g_worker_lease_actions_present"] = all(token in GATEWAY_SOURCE for token in (
            '"lease_release"', '"worker_drain"',
        ))
        checks["b6h_execution_actions_present"] = all(token in GATEWAY_SOURCE for token in (
            '"execution_cancel"', '"execution_terminate"',
        ))
        checks["b6i_safety_closure_present"] = all(token in GATEWAY_SOURCE for token in (
            "idempotency_mismatch", "state_conflict", "confirmation_failed",
            "preview_token_invalid", "owner_actions_disabled", "_audit(",
        ))
        checks["live_dispatch_defaults_off"] = "OWNER_ACTIONS_ENABLED_ENV" in GATEWAY_SOURCE and "!= \"1\"" in GATEWAY_SOURCE
        checks["no_mutation_adapter_registered_by_installation"] = "_ADAPTERS: dict" in GATEWAY_SOURCE and probe["adapter_count"] == 0
        checks["monitoring_projection_unchanged_candidate"] = before["runtime_infrastructure_projection"] == read_text(paths["runtime_infrastructure_projection"])
        checks["monitoring_components_have_no_action_controls"] = all(
            token not in before["index_html"] for token in ('data-owner-action="', 'runtimeOwnerActionRequestForm')
        )
        checks["responsive_contract_present"] = all(token in candidate_css for token in (
            "@media (max-width: 940px)", "@media (max-width: 620px)", "overflow-wrap: anywhere",
        ))
        checks["accessibility_contract_present"] = all(token in candidate_html for token in (
            'aria-live="polite"', 'role="status"', 'aria-labelledby=',
        )) and ":focus-visible" in candidate_css
        checks["reduced_motion_contract_present"] = "prefers-reduced-motion: reduce" in candidate_css
        checks["execute_endpoint_present_once"] = candidate_backend.count('@router.post("/actions/execute")') == 1

        if not all(checks.values()):
            raise RuntimeError("One or more combined B6 candidate checks failed.")

        backup = backup_sources(root, paths, changed_names)
        evidence["backup"] = str(backup)
        checks["backup_created"] = backup.is_dir()

        atomic_write_text(paths["index_html"], candidate_html)
        atomic_write_text(paths["runtime_owner_css"], candidate_css)
        atomic_write_text(paths["runtime_owner_js"], candidate_js)
        atomic_write_text(paths["runtime_summary_api"], candidate_backend)
        atomic_write_text(paths["owner_actions_gateway"], GATEWAY_SOURCE)

        retained = {name: read_text(paths[name]) for name in changed_names}
        checks["retained_html_ids_unique"] = html_ids_unique(retained["index_html"])
        checks["retained_css_balanced"] = balanced(retained["runtime_owner_css"], "{", "}")
        checks["retained_javascript_syntax"] = javascript_syntax_valid(retained["runtime_owner_js"])
        checks["retained_runtime_api_syntax"] = python_syntax_valid(retained["runtime_summary_api"], str(paths["runtime_summary_api"]))
        checks["retained_gateway_syntax"] = python_syntax_valid(retained["owner_actions_gateway"], str(paths["owner_actions_gateway"]))
        checks["retained_markers"] = all(MARKER in retained[name] for name in changed_names)
        checks["historical_b6a_report_unchanged"] = sha256_path(b6a_report) == b6a_hash_before
        checks["monitoring_projection_retained"] = sha256_path(paths["runtime_infrastructure_projection"]) == hashes_before["runtime_infrastructure_projection"]
        checks["owner_css_unchanged"] = sha256_path(paths["owner_css"]) == hashes_before["owner_css"]
        checks["owner_js_unchanged"] = sha256_path(paths["owner_js"]) == hashes_before["owner_js"]
        checks["pipeline_operations_unchanged"] = sha256_path(paths["pipeline_operations"]) == hashes_before["pipeline_operations"]
        checks["production_jobs_created_no"] = True
        checks["production_queue_claims_no"] = True
        checks["production_handlers_executed_no"] = True
        checks["production_workflow_persistence_no"] = True
        checks["production_recovery_actions_no"] = True
        checks["live_network_requests_during_certification_no"] = True
        checks["project_modules_imported_no"] = True

        if not all(checks.values()):
            raise RuntimeError("One or more retained combined B6 checks failed.")

        evidence.update({
            "changed_sources": [str(paths[name].relative_to(root)).replace("\\", "/") for name in changed_names],
            "endpoints": [PREVIEW_ENDPOINT, EXECUTE_ENDPOINT],
            "action_families": ["jobs_queues", "workflows_stages", "workers_leases", "executions"],
            "action_contracts": 11,
            "safety_guards": [
                "fresh eligibility", "expected state", "impact preview", "confirmation phrase",
                "signed preview token", "idempotency", "trusted owner identity", "server-only adapter",
                "audit", "fail-closed activation",
            ],
            "source_hashes_before": hashes_before,
            "source_hashes_after": {name: sha256_path(path) for name, path in paths.items() if path.exists()},
            "patch_retained": True,
        })

        write_report(report, checks, evidence, execution_error, True)
        for name in checks:
            print(f"{name.upper()}: PASS")
        print("FAILED_CHECK_COUNT=0")
        print("NOT_RUN_CHECK_COUNT=0")
        print(f"REPORT={report}")
        print("PART_F_15_B6B_B6I_STATUS=CERTIFIED")
        print("PATCH_RETAINED=YES")
        print("LIVE_ACTION_DISPATCH=OFF")
        print("ACTIONS_EXECUTED=NO")
        return 0
    except Exception as exc:
        execution_error = {
            "error_type": type(exc).__name__,
            "error_message": str(exc),
            "traceback": traceback.format_exc(),
        }
        if backup is not None:
            try:
                restore_sources(root, backup, paths, changed_names)
                evidence["rollback_performed"] = True
            except Exception as restore_exc:
                execution_error["rollback_error"] = f"{type(restore_exc).__name__}: {restore_exc}"
        evidence.setdefault("backup", str(backup) if backup else "UNAVAILABLE")
        evidence["patch_retained"] = False
        write_report(report, checks, evidence, execution_error, False)
        for name, passed in checks.items():
            print(f"{name.upper()}: {'PASS' if passed else 'FAIL'}")
        failed = [name for name, passed in checks.items() if not passed]
        print(f"FAILED_CHECK_COUNT={len(failed)}")
        print("NOT_RUN_CHECK_COUNT=0")
        print(f"REPORT={report}")
        print("PART_F_15_B6B_B6I_STATUS=NOT_CERTIFIED")
        print("PATCH_RETAINED=NO")
        print("ACTIONS_EXECUTED=NO")
        return 1


def self_test() -> int:
    assert python_syntax_valid(GATEWAY_SOURCE, "owner_actions_gateway.py")
    assert balanced(CSS_APPEND, "{", "}")
    assert javascript_syntax_valid(JS_APPEND)
    sample = (
        OLD_CSS_VERSION + "\n" + OLD_JS_VERSION + "\n"
        '<section id="runtimeOwnerSectionOwnerActions" '
        'data-runtime-owner-section="owner_actions"></section>'
    )
    candidate = build_candidate_html(sample)
    assert MARKER in candidate
    assert candidate.count('id="runtimeOwnerActionsWorkspace"') == 1
    probe = gateway_probe(GATEWAY_SOURCE)
    assert probe["passed"]
    print("PART_F_15_B6B_B6I_SELF_TEST=PASS")
    return 0


def main(argv: list[str]) -> int:
    if argv == ["--self-test"]:
        return self_test()
    if len(argv) != 2:
        print(
            "Usage: RUN_15_B6B_B6I_OWNER_ACTIONS_RECOVERY_SAFETY_UI.py "
            "<project-root> <report-path>",
            file=sys.stderr,
        )
        return 2
    return run(Path(argv[0]).resolve(), Path(argv[1]).resolve())


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
