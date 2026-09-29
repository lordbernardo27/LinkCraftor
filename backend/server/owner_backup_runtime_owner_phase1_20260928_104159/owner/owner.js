(function(){
  const titles = {
    dashboard:["Owner Dashboard","Founder-level command center for LinkCraftor."],
    users:["Users & Plans","Manage users, workspaces, subscriptions, and plan visibility."],
    billing:["Billing & Revenue","Monitor subscriptions, API revenue, document revenue, and failed payments."],
    documents:["Documents & Linking","Track documents, linking activity, anchors, and batch processing."],
    external:["External Intelligence / Resolver","Manage external authority URLs, resolver tools, sitemap imports, rollback, and source intelligence."],
    engine:["Engine & Modules","Monitor LinkCraftor engines, modules, toggles, and performance."],
    api:["Access & API Keys","Manage API keys, SDK access, developer usage, and limits."],
    ai:["AI Insights","View semantic trends, AI recommendations, and intelligence snapshots."],
    logs:["Logs & Diagnostics","Inspect errors, runtime logs, queue logs, and system events."],
    settings:["Settings","Manage owner preferences, branding, notifications, and feature flags."],
    decision:["Decision Intelligence","Inspect decision logs, learning signals, confidence, and explainability."],
    ledger:["Global Ledger","Unified revenue, usage, API, workspace, subscription, and event ledger."],
    queues:["Orchestration & Queues","Monitor jobs, workers, queues, batch tasks, and retries."],
    cloud:["Infrastructure & Cloud","Track AWS, storage, database, server health, and cloud cost."],
    security:["Security & Access","Monitor logins, permissions, tokens, encryption, and threats."],
    tms:["TMS Intelligence","Support ticket health, SLA risk, escalations, and support AI monitoring."],
    sos:["SOS Intelligence","Lead pipeline, outreach, demos, conversions, and sales operations."],
    product:["Product Analytics","Feature adoption, retention, churn, user journeys, and bottlenecks."],
    dataset:["Dataset Ecosystem","Dataset growth, quality, learning signals, and future data intelligence."],
    integrations:["Integrations Hub","WordPress, Webflow, Shopify, APIs, SDKs, and plugin ecosystem."],
    crosssite:["Cross-Site Intelligence","Domains, sitemaps, cross-site links, and authority flow."],
    founder:["Founder Intelligence","Company health, risks, opportunities, and strategic recommendations."],
    compliance:["Policy & Compliance","Privacy, audit trails, governance, and compliance monitoring."],
    multiproduct:["Multi-Product Control Tower","Unified control for LinkCraftor, Wisspert, Scenagram, and future products."],
    growth:["Autonomous Growth Engine","Growth, pricing, revenue, market, and expansion recommendations."],
    audit:["Audit Log Viewer","System-wide audit trails, ownership actions, security actions, and operational history."],

      backup:["Backup & Restore Control","Backups, restore points, disaster recovery, and recovery validation."],

      alerts:["Notification & Alert Center","System alerts, incidents, warnings, notifications, and operational events."],

      environment:["Environment Control Panel","Local, staging, production, deployments, versions, and infrastructure environments."],

      staff:["Staff & Role Management","Staff accounts, permissions, role assignments, and access governance."],

      sla:["SLA & Escalation Monitor","SLA compliance, escalation routing, breach detection, and service monitoring."],

      incident:["Incident & Status Management","Incidents, outages, status pages, service disruptions, and recovery tracking."],

      selfhealing:["Self-Healing Operations Center","Repair execution, rebuild execution, reloads, validation, and autonomous recovery."],

      governance:["Governance & Event Intelligence Center","Governance events, event contracts, routing, decision logs, and event audits."],

      jobs:["Async Job & Queue Monitor","Async jobs, queue depth, running jobs, failed jobs, slow jobs, and retry controls."],

      workers:["Worker & Cluster Monitor","Worker health, workload, speed, errors, clusters, listeners, and processing routes."],

      billinggate:["Billing Gate & Usage Enforcement Center","AU limits, document limits, API usage, ceiling events, paused jobs, and resume logic."],

      sovereignty:["Founder Sovereignty Center","Founder authority, sovereignty events, override history, trust status, and founder controls."],

      recovery:["Recovery Vault Center","Recovery assets, recovery tokens, recovery certificates, key rotation, and vault monitoring."],

      lockdown:["Emergency Lockdown Center","Global lockdown, selective lockdown, session kill switch, access freeze, and emergency overrides."],

      threatintel:["Sovereignty Threat Intelligence Center","Suspicious logins, privilege escalation, credential abuse, threat correlation, and founder alerts."],

      architect:["Autonomous Product Architect","Owner-only strategic AI for products, modules, APIs, and roadmaps."]
  };

  const pageTitle = document.getElementById("pageTitle");
  const pageSubtitle = document.getElementById("pageSubtitle");
  const dashboard = document.getElementById("dashboard");
  const generic = document.getElementById("genericPage");
  const genericTitle = document.getElementById("genericTitle");
  const genericDesc = document.getElementById("genericDesc");

  function showPage(key){
    document.querySelectorAll(".nav-item").forEach(b=>b.classList.toggle("active", b.dataset.page === key));
    const meta = titles[key] || titles.dashboard;
    pageTitle.textContent = meta[0];
    pageSubtitle.textContent = meta[1];

    const pageMap = {
      dashboard: "dashboard",
      users: "usersPage",
      billing: "billingPage",
      documents: "documentsPage",
      external: "externalPage",
      engine: "enginePage",
      api: "apiPage",
      ai: "aiPage",
      logs: "logsPage",
      settings: "settingsPage",
      decision: "decisionPage",
      ledger: "ledgerPage",
      queues: "queuesPage",
      cloud: "cloudPage",
      security: "securityPage",
      tms: "tmsPage",
      sos: "sosPage",
      product: "productPage",
      dataset: "datasetPage",
      integrations: "integrationsPage",
      crosssite: "crosssitePage",
      founder: "founderPage",
      compliance: "compliancePage",
      multiproduct: "multiproductPage",
      growth: "growthPage",
      audit: "auditPage",
        backup: "genericPage",
        alerts: "genericPage",
        environment: "genericPage",
        staff: "genericPage",
        sla: "genericPage",
        incident: "genericPage",
        selfhealing: "genericPage",
        governance: "genericPage",
        jobs: "genericPage",
        workers: "genericPage",
        billinggate: "genericPage",
        sovereignty: "genericPage",
        recovery: "genericPage",
        lockdown: "genericPage",
        threatintel: "genericPage",

        architect: "architectPage"
    };

    document.querySelectorAll(".page").forEach(p=>p.classList.remove("active"));

    const targetId = pageMap[key];
    const target = targetId ? document.getElementById(targetId) : null;

    if(target){
      target.classList.add("active");
    }else{
      generic.classList.add("active");
      genericTitle.textContent = meta[0];
      genericDesc.textContent = meta[1] + " Full component design will be added in the next UI phases.";
    }

    try{ localStorage.setItem("LC_OWNER_LAST_PAGE", key); }catch(e){}
  }


  document.querySelectorAll(".nav-item").forEach(btn=>{
    btn.addEventListener("click", ()=>showPage(btn.dataset.page));
  });


  const notifyBtn = document.getElementById("btnNotify");
  const notifyDrawer = document.getElementById("notifyDrawer");
  const quickBtn = document.getElementById("btnQuick");
  const quickMenu = document.getElementById("quickMenu");

  notifyBtn?.addEventListener("click", ()=>{
    notifyDrawer?.classList.toggle("open");
    quickMenu?.classList.remove("open");
  });

  quickBtn?.addEventListener("click", ()=>{
    quickMenu?.classList.toggle("open");
    notifyDrawer?.classList.remove("open");
  });

  document.querySelectorAll("[data-close]").forEach(btn=>{
    btn.addEventListener("click", ()=>{
      document.getElementById(btn.dataset.close)?.classList.remove("open");
    });
  });

  document.querySelectorAll("[data-jump]").forEach(btn=>{
    btn.addEventListener("click", ()=>{
      showPage(btn.dataset.jump);
      quickMenu?.classList.remove("open");
    });
  });

  document.addEventListener("keydown", (e)=>{
    if((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "k"){
      e.preventDefault();
      document.getElementById("ownerSearch")?.focus();
    }
  });



  async function loadAuditDashboard(){
    try{
      const [summaryRes, filtersRes, eventsRes, timelineRes] = await Promise.all([
        fetch("/owner/api/audit/summary"),
        fetch("/owner/api/audit/filters"),
        fetch("/owner/api/audit/events?limit=20"),
        fetch("/owner/api/audit/timeline?limit=20")
      ]);

      const summary = await summaryRes.json();
      const filters = await filtersRes.json();
      const eventsData = await eventsRes.json();
      const timelineData = await timelineRes.json();

      document.getElementById("auditTotal").textContent = summary.total_events ?? 0;
      document.getElementById("auditSources").textContent = Object.keys(summary.sources || {}).length;
      document.getElementById("auditMajor").textContent = summary.severity?.major ?? 0;
      document.getElementById("auditMinor").textContent = summary.severity?.minor ?? 0;
      document.getElementById("auditInfo").textContent = summary.severity?.info ?? 0;

      const sourceSelect = document.getElementById("auditSourceFilter");
      const severitySelect = document.getElementById("auditSeverityFilter");
      const typeSelect = document.getElementById("auditTypeFilter");

      if(sourceSelect && sourceSelect.options.length <= 1){
        (filters.sources || []).forEach(v=>{
          const o = document.createElement("option");
          o.value = v; o.textContent = v;
          sourceSelect.appendChild(o);
        });
      }

      if(severitySelect && severitySelect.options.length <= 1){
        (filters.severities || []).forEach(v=>{
          const o = document.createElement("option");
          o.value = v; o.textContent = v;
          severitySelect.appendChild(o);
        });
      }

      if(typeSelect && typeSelect.options.length <= 1){
        (filters.event_types || []).forEach(v=>{
          const o = document.createElement("option");
          o.value = v; o.textContent = v;
          typeSelect.appendChild(o);
        });
      }

      renderAuditEvents(eventsData.events || []);
      renderAuditTimeline(timelineData.timeline || []);
    }catch(err){
      console.error("[Owner Audit] failed to load", err);
    }
  }

  function renderAuditEvents(events){
    const box = document.getElementById("auditEventList");
    if(!box) return;
    if(!events.length){
      box.innerHTML = "<div><span>No audit events found.</span><strong>Empty</strong></div>";
      return;
    }
    box.innerHTML = events.map(e=>`
      <div>
        <span>${e.title || e.event_type}</span>
        <strong>${e.severity || "info"}</strong>
        <small>${e.source || "unknown"} ? ${e.timestamp || ""}</small>
      </div>
    `).join("");
  }

  function renderAuditTimeline(items){
    const box = document.getElementById("auditTimelineList");
    if(!box) return;
    if(!items.length){
      box.innerHTML = "<div><span>No timeline events found.</span><strong>Empty</strong></div>";
      return;
    }
    box.innerHTML = items.map(e=>`
      <div>
        <span>${e.timestamp || ""}</span>
        <strong>${e.event_type || "event"}</strong>
        <small>${e.source || "unknown"} ? ${e.severity || "info"}</small>
      </div>
    `).join("");
  }

  async function applyAuditFilters(){
    const q = encodeURIComponent(document.getElementById("auditSearch")?.value || "");
    const source = encodeURIComponent(document.getElementById("auditSourceFilter")?.value || "");
    const severity = encodeURIComponent(document.getElementById("auditSeverityFilter")?.value || "");
    const eventType = encodeURIComponent(document.getElementById("auditTypeFilter")?.value || "");

    const url = `/owner/api/audit/events?limit=50&query=${q}&source=${source}&severity=${severity}&event_type=${eventType}`;
    const res = await fetch(url);
    const data = await res.json();
    renderAuditEvents(data.events || []);
  }

  document.getElementById("auditApplyFilters")?.addEventListener("click", applyAuditFilters);

  document.getElementById("auditExportBtn")?.addEventListener("click", async ()=>{
    const q = encodeURIComponent(document.getElementById("auditSearch")?.value || "");
    const res = await fetch(`/owner/api/audit/export?limit=1000&query=${q}`);
    const data = await res.json();
    console.log("[Owner Audit Export]", data);
    alert("Audit export prepared in browser console.");
  });


  showPage(localStorage.getItem("LC_OWNER_LAST_PAGE") || "dashboard");
})();
