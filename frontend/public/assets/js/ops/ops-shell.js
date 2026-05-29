(function initOpsShell() {
  const app = document.getElementById("ops-app");
  const content = document.getElementById("ops-content");
  const navItems = document.querySelectorAll(".ops-nav-item");

  const staffPermissionRegistry = {
    support: [
      "view_tickets",
      "reply_to_ticket",
      "add_internal_note",
      "update_status"
    ],
    senior_agent: [
      "view_tickets",
      "reply_to_ticket",
      "add_internal_note",
      "assign_ticket",
      "update_priority",
      "update_severity",
      "update_status",
      "resolve_ticket",
      "close_ticket"
    ],
    billing: [
      "view_tickets",
      "reply_to_ticket",
      "add_internal_note",
      "update_status",
      "resolve_ticket",
      "view_billing_context"
    ],
    engineering: [
      "view_tickets",
      "add_internal_note",
      "update_severity",
      "update_status",
      "view_engineering_context"
    ],
    manager: ["all"],
    admin: ["all"],
    owner: ["all"]
  };

  function staffHasPermission(role, permission) {
    const permissions = staffPermissionRegistry[role] || [];
    return permissions.includes("all") || permissions.includes(permission);
  }

  function applyUiPermissionGuards(role) {
    const guardedActions = {
      reply: "reply_to_ticket",
      internal_note: "add_internal_note",
      assignment: "assign_ticket",
      priority: "update_priority",
      severity: "update_severity",
      status: "update_status",
      resolve: "resolve_ticket",
      close: "close_ticket"
    };

    document.querySelectorAll("[data-staff-action]").forEach(function (button) {
      const action = button.dataset.staffAction;
      const requiredPermission = guardedActions[action];

      if (requiredPermission && !staffHasPermission(role, requiredPermission)) {
        button.disabled = true;
        button.title = "Your staff role does not have permission for this action.";
        button.classList.add("ops-disabled-action");
      }
    });
  }

  const routePermissions = {
    dashboard: ["owner", "admin", "manager", "support", "billing", "engineering"],
    tickets: ["owner", "admin", "manager", "support", "billing", "engineering"],
    assigned: ["owner", "admin", "manager", "support", "billing", "engineering"],
    unassigned: ["owner", "admin", "manager", "support", "billing", "engineering"],
    urgent: ["owner", "admin", "manager", "support", "billing", "engineering"],
    engineering: ["owner", "admin", "manager", "engineering", "support"],
    waiting_customer: ["owner", "admin", "manager", "support", "billing"],
    resolved: ["owner", "admin", "manager", "support", "billing", "engineering"],
    closed: ["owner", "admin", "manager", "support", "billing", "engineering"],
    ticket_thread: ["owner", "admin", "manager", "support", "billing", "engineering"],
    customers: ["owner", "admin", "manager", "support", "billing"],
    workspaces: ["owner", "admin", "manager", "support", "engineering"],
    escalations: ["owner", "admin", "manager", "engineering"],
    reports: ["owner", "admin", "manager"],
    settings: ["owner", "admin"]
  };

  const demoTickets = [
    {
      id: "TKT-1001",
      title: "Unable to process internal linking batch",
      priority: "High",
      workspace: "betterhealthcheck.com",
      status: "Open",
      assignee: "me",
      queue: "engineering",
      category: "Technical",
      severity: "Major",
      createdAt: "2026-05-28T09:14:00"
    },
    {
      id: "TKT-1002",
      title: "Billing invoice mismatch detected",
      priority: "Medium",
      workspace: "fitlivingdaily.com",
      status: "Waiting on Customer",
      assignee: "billing",
      queue: "waiting_customer",
      category: "Billing",
      severity: "Normal",
      createdAt: "2026-05-28T08:42:00"
    },
    {
      id: "TKT-1003",
      title: "Upload pipeline timeout during processing",
      priority: "Urgent",
      workspace: "ovulationguide.com",
      status: "Escalated",
      assignee: "me",
      queue: "engineering",
      category: "Technical",
      severity: "Critical",
      createdAt: "2026-05-28T07:55:00"
    },
    {
      id: "TKT-1004",
      title: "Customer cannot access workspace dashboard",
      priority: "High",
      workspace: "medicalinsightslab.com",
      status: "Open",
      assignee: null,
      queue: "support",
      category: "Access",
      severity: "Major",
      createdAt: "2026-05-27T16:20:00"
    },
    {
      id: "TKT-1005",
      title: "Resolved sitemap import inconsistency",
      priority: "Low",
      workspace: "nutritionresearchhub.com",
      status: "Resolved",
      assignee: "support",
      queue: "resolved",
      category: "Import",
      severity: "Normal",
      createdAt: "2026-05-27T11:10:00"
    },
    {
      id: "TKT-1006",
      title: "Completed billing correction confirmation",
      priority: "Low",
      workspace: "seoauthoritylabs.com",
      status: "Closed",
      assignee: "billing",
      queue: "closed",
      category: "Billing",
      severity: "Normal",
      createdAt: "2026-05-26T15:45:00"
    }
  ];

  const demoThreadMessages = [
    {
      sender: "Customer",
      role: "customer",
      time: "09:14 AM",
      body: "Our internal linking batch keeps failing after upload processing."
    },
    {
      sender: "Support Agent",
      role: "staff",
      time: "09:26 AM",
      body: "We are investigating the runtime pipeline timeout issue now."
    },
    {
      sender: "Engineering",
      role: "staff",
      time: "09:41 AM",
      body: "We detected a queue orchestration delay during worker execution."
    }
  ];

  function renderShellError(title, message) {
    if (!content) return;

    content.innerHTML = `
      <div class="ops-card ops-error-card">
        <span class="ops-status ops-status-error">Shell Error</span>
        <h3>${title}</h3>
        <p>${message}</p>
      </div>
    `;
  }

  function renderShellLoading(message) {
    if (!content) return;

    content.innerHTML = `
      <div class="ops-card ops-loading-card">
        <span class="ops-loader"></span>
        <h3>Loading staff console</h3>
        <p>${message}</p>
      </div>
    `;
  }

  function getPriorityWeight(priority) {
    const weights = {
      Urgent: 4,
      High: 3,
      Medium: 2,
      Low: 1
    };

    return weights[priority] || 0;
  }

  function getQueueFiltersHtml() {
    return `
      <div class="ops-filter-bar">
        <input
          id="ops-ticket-search"
          type="search"
          placeholder="Search tickets, workspace, category..."
        />

        <select id="ops-filter-status">
          <option value="">All Statuses</option>
          <option>Open</option>
          <option>Pending</option>
          <option>Escalated</option>
          <option>Waiting on Customer</option>
          <option>Resolved</option>
          <option>Closed</option>
        </select>

        <select id="ops-filter-priority">
          <option value="">All Priorities</option>
          <option>Urgent</option>
          <option>High</option>
          <option>Medium</option>
          <option>Low</option>
        </select>

        <select id="ops-filter-severity">
          <option value="">All Severities</option>
          <option>Critical</option>
          <option>Major</option>
          <option>Normal</option>
        </select>

        <select id="ops-filter-category">
          <option value="">All Categories</option>
          <option>Technical</option>
          <option>Billing</option>
          <option>Access</option>
          <option>Import</option>
        </select>

        <select id="ops-filter-assignee">
          <option value="">All Assignees</option>
          <option value="me">Assigned to Me</option>
          <option value="support">Support</option>
          <option value="billing">Billing</option>
          <option value="unassigned">Unassigned</option>
        </select>

        <select id="ops-filter-workspace">
          <option value="">All Workspaces</option>
          <option>betterhealthcheck.com</option>
          <option>fitlivingdaily.com</option>
          <option>ovulationguide.com</option>
          <option>medicalinsightslab.com</option>
          <option>nutritionresearchhub.com</option>
          <option>seoauthoritylabs.com</option>
        </select>

        <select id="ops-sort-mode">
          <option value="newest">Sort: Newest</option>
          <option value="oldest">Sort: Oldest</option>
          <option value="urgency">Sort: Urgency</option>
        </select>
      </div>
    `;
  }

  function applyQueueFilters(tickets) {
    const search = document.getElementById("ops-ticket-search")?.value.toLowerCase().trim() || "";
    const status = document.getElementById("ops-filter-status")?.value || "";
    const priority = document.getElementById("ops-filter-priority")?.value || "";
    const severity = document.getElementById("ops-filter-severity")?.value || "";
    const category = document.getElementById("ops-filter-category")?.value || "";
    const assignee = document.getElementById("ops-filter-assignee")?.value || "";
    const workspace = document.getElementById("ops-filter-workspace")?.value || "";
    const sortMode = document.getElementById("ops-sort-mode")?.value || "newest";

    let filtered = tickets.filter(function (ticket) {
      const searchTarget = [
        ticket.id,
        ticket.title,
        ticket.workspace,
        ticket.status,
        ticket.priority,
        ticket.severity,
        ticket.category,
        ticket.assignee || "Unassigned"
      ].join(" ").toLowerCase();

      const matchesSearch = !search || searchTarget.includes(search);
      const matchesStatus = !status || ticket.status === status;
      const matchesPriority = !priority || ticket.priority === priority;
      const matchesSeverity = !severity || ticket.severity === severity;
      const matchesCategory = !category || ticket.category === category;
      const matchesWorkspace = !workspace || ticket.workspace === workspace;

      let matchesAssignee = true;
      if (assignee === "unassigned") {
        matchesAssignee = !ticket.assignee;
      } else if (assignee) {
        matchesAssignee = ticket.assignee === assignee;
      }

      return (
        matchesSearch &&
        matchesStatus &&
        matchesPriority &&
        matchesSeverity &&
        matchesCategory &&
        matchesAssignee &&
        matchesWorkspace
      );
    });

    filtered = filtered.sort(function (a, b) {
      if (sortMode === "oldest") {
        return new Date(a.createdAt) - new Date(b.createdAt);
      }

      if (sortMode === "urgency") {
        return getPriorityWeight(b.priority) - getPriorityWeight(a.priority);
      }

      return new Date(b.createdAt) - new Date(a.createdAt);
    });

    return filtered;
  }

  function bindQueueFilters(baseTickets) {
    const controls = document.querySelectorAll(
      "#ops-ticket-search, #ops-filter-status, #ops-filter-priority, #ops-filter-severity, #ops-filter-category, #ops-filter-assignee, #ops-filter-workspace, #ops-sort-mode"
    );

    const list = document.getElementById("ops-ticket-list");
    const total = document.getElementById("ops-stat-total");
    const urgent = document.getElementById("ops-stat-urgent");
    const open = document.getElementById("ops-stat-open");

    function refreshQueue() {
      const filtered = applyQueueFilters(baseTickets);

      if (list) {
        list.innerHTML = renderTicketCards(filtered);
      }

      if (total) total.textContent = filtered.length;
      if (urgent) total.textContent = filtered.length;
      if (urgent) urgent.textContent = filtered.filter(ticket => ticket.priority === "Urgent").length;
      if (open) open.textContent = filtered.filter(ticket => ticket.status === "Open").length;

      bindThreadOpeners();
    }

    controls.forEach(function (control) {
      control.addEventListener("input", refreshQueue);
      control.addEventListener("change", refreshQueue);
    });
  }

  function renderTicketCards(tickets) {
    if (!tickets.length) {
      return `
        <div class="ops-empty-state">
          <h3>No tickets found</h3>
          <p>This queue does not have tickets yet.</p>
        </div>
      `;
    }

    return tickets.map(ticket => `
      <article
        class="ops-ticket-card"
        data-open-thread="true"
        data-ticket-id="${ticket.id}"
      >
        <div class="ops-ticket-top">
          <span class="ops-ticket-id">${ticket.id}</span>
          <span class="ops-ticket-priority">${ticket.priority}</span>
        </div>

        <h3>${ticket.title}</h3>

        <div class="ops-ticket-meta">
          <span>${ticket.workspace}</span>
          <span>${ticket.status}</span>
          <span>Assigned: ${ticket.assignee || "Unassigned"}</span>
        </div>
      </article>
    `).join("");
  }

  function renderQueuePage(queueTitle, queueSubtitle, tickets) {
    return `
      <section class="ops-queue-page" data-queue-base='${JSON.stringify(tickets)}'>
        <div class="ops-page-header">
          <div>
            <span class="ops-status">Queue Active</span>
            <h2>${queueTitle}</h2>
            <p>${queueSubtitle}</p>
          </div>
        </div>

        ${getQueueFiltersHtml()}

        <div class="ops-queue-stats">
          <div class="ops-stat-card">
            <strong id="ops-stat-total">${tickets.length}</strong>
            <span>Total Tickets</span>
          </div>

          <div class="ops-stat-card">
            <strong id="ops-stat-urgent">${tickets.filter(ticket => ticket.priority === "Urgent").length}</strong>
            <span>Urgent</span>
          </div>

          <div class="ops-stat-card">
            <strong id="ops-stat-open">${tickets.filter(ticket => ticket.status === "Open").length}</strong>
            <span>Open</span>
          </div>
        </div>

        <div class="ops-ticket-list" id="ops-ticket-list">
          ${renderTicketCards(tickets)}
        </div>
      </section>
    `;
  }

  function renderTicketThreadWorkspace(ticketId) {
    const ticket =
      demoTickets.find(ticket => ticket.id === ticketId) || demoTickets[0];

    return `
      <section class="ops-thread-page">
        <div class="ops-thread-header">
          <div>
            <span class="ops-status">Ticket Thread</span>
            <h2>${ticket.title}</h2>

            <div class="ops-ticket-meta">
              <span>${ticket.id}</span>
              <span>${ticket.workspace}</span>
              <span>${ticket.status}</span>
            </div>
          </div>
        </div>

        <div class="ops-thread-layout">
          <main class="ops-thread-main">
            <div class="ops-thread-conversation">
              ${demoThreadMessages.map(message => `
                <article class="ops-thread-message ${message.role}">
                  <div class="ops-thread-message-top">
                    <strong>${message.sender}</strong>
                    <span>${message.time}</span>
                  </div>

                  <p>${message.body}</p>
                </article>
              `).join("")}
            </div>

            <div class="ops-reply-composer">
              <h3>Reply to Customer</h3>
              <textarea placeholder="Write a staff reply..."></textarea>
              <button type="button" data-staff-action="reply" data-ticket-id="${ticket.id}">Send Reply</button>
            </div>

            <div class="ops-internal-notes">
              <h3>Internal Notes</h3>
              <textarea placeholder="Add an internal note for staff only..."></textarea>
              <button type="button" data-staff-action="internal_note" data-ticket-id="${ticket.id}">Save Internal Note</button>
            </div>
          </main>

          <aside class="ops-thread-side">
            <div class="ops-side-card">
              <h3>Customer Metadata</h3>
              <p><strong>Name:</strong> Demo Customer</p>
              <p><strong>Email:</strong> customer@example.com</p>
              <p><strong>Plan:</strong> Pro</p>
              <p><strong>Risk:</strong> Medium</p>
            </div>

            <div class="ops-side-card">
              <h3>Workspace Metadata</h3>
              <p><strong>Workspace:</strong> ${ticket.workspace}</p>
              <p><strong>Domain:</strong> ${ticket.workspace}</p>
              <p><strong>Recent Jobs:</strong> 12</p>
              <p><strong>Engine Status:</strong> Needs Review</p>
            </div>

            <div class="ops-side-card">
              <h3>Lifecycle Timeline</h3>
              <ol class="ops-timeline">
                <li>Ticket created</li>
                <li>Assigned to staff</li>
                <li>Engineering review started</li>
                <li>Awaiting next action</li>
              </ol>
            </div>

            <div class="ops-side-card">
              <h3>Assignment</h3>
              <select data-staff-action-field="assignment">
                <option>Assign to Support</option>
                <option>Assign to Billing</option>
                <option>Assign to Engineering</option>
                <option>Assign to Manager</option>
              </select>

              <button type="button" class="ops-side-action-btn" data-staff-action="assignment" data-ticket-id="${ticket.id}">
                Update Assignment
              </button>
            </div>

            <div class="ops-side-card">
              <h3>Priority & Severity</h3>

              <label>Priority</label>
              <select data-staff-action-field="priority">
                <option>${ticket.priority}</option>
                <option>Low</option>
                <option>Medium</option>
                <option>High</option>
                <option>Urgent</option>
              </select>

              <button type="button" class="ops-side-action-btn" data-staff-action="priority" data-ticket-id="${ticket.id}">
                Update Priority
              </button>

              <label>Severity</label>
              <select data-staff-action-field="severity">
                <option>Normal</option>
                <option>Major</option>
                <option>Critical</option>
              </select>

              <button type="button" class="ops-side-action-btn" data-staff-action="severity" data-ticket-id="${ticket.id}">
                Update Severity
              </button>
            </div>

            <div class="ops-side-card">
              <h3>Status Controls</h3>

              <label>Ticket Status</label>
              <select>
                <option>${ticket.status}</option>
                <option>Open</option>
                <option>Pending</option>
                <option>Escalated</option>
                <option>Waiting on Customer</option>
                <option>Resolved</option>
                <option>Closed</option>
              </select>

              <button type="button" class="ops-side-action-btn" data-staff-action="status" data-ticket-id="${ticket.id}">
                Update Status
              </button>
            </div>

            <div class="ops-side-card">
              <h3>Resolution Controls</h3>

              <textarea
                class="ops-resolution-textarea"
                placeholder="Add ticket resolution notes..."
              ></textarea>

              <div class="ops-resolution-actions">
                <button type="button" class="ops-side-action-btn" data-staff-action="resolve" data-ticket-id="${ticket.id}">
                  Resolve Ticket
                </button>

                <button
                  type="button"
                  class="ops-side-action-btn ops-danger-btn"
                  data-staff-action="close"
                  data-ticket-id="${ticket.id}"
                >
                  Close Ticket
                </button>
              </div>
            </div>
          </aside>
        </div>
      </section>
    `;
  }

  function renderAllTicketsQueue() {
    return renderQueuePage(
      "All Tickets",
      "Central support operations queue.",
      demoTickets
    );
  }

  function renderAssignedToMeQueue() {
    return renderQueuePage(
      "Assigned to Me",
      "Tickets currently assigned to the signed-in staff member.",
      demoTickets.filter(ticket => ticket.assignee === "me")
    );
  }

  function renderUnassignedQueue() {
    return renderQueuePage(
      "Unassigned Tickets",
      "Tickets waiting for staff assignment.",
      demoTickets.filter(ticket => !ticket.assignee)
    );
  }

  function renderUrgentQueue() {
    return renderQueuePage(
      "Urgent Tickets",
      "High-impact tickets requiring immediate staff attention.",
      demoTickets.filter(ticket => ticket.priority === "Urgent")
    );
  }

  function renderEngineeringQueue() {
    return renderQueuePage(
      "Pending Engineering",
      "Technical escalation and engineering investigation queue.",
      demoTickets.filter(ticket => ticket.queue === "engineering")
    );
  }

  function renderWaitingCustomerQueue() {
    return renderQueuePage(
      "Waiting on Customer",
      "Tickets paused until customer response or confirmation.",
      demoTickets.filter(ticket => ticket.queue === "waiting_customer")
    );
  }

  function renderResolvedQueue() {
    return renderQueuePage(
      "Resolved Tickets",
      "Successfully resolved support requests awaiting closure.",
      demoTickets.filter(ticket => ticket.queue === "resolved")
    );
  }

  function renderClosedQueue() {
    return renderQueuePage(
      "Closed Tickets",
      "Archived and finalized support operations records.",
      demoTickets.filter(ticket => ticket.queue === "closed")
    );
  }

  if (!app || !content) {
    console.error("LinkCraftor ops shell failed to initialize: missing shell containers");
    return;
  }

  renderShellLoading("Preparing workspace shell...");

  const staffSession = window.localStorage.getItem("linkcraftor_ops_staff_session");
  const staffRole = window.localStorage.getItem("linkcraftor_ops_staff_role") || "support";

  if (!staffSession) {
    app.dataset.shell = "auth-required";

    content.innerHTML = `
      <div class="ops-card ops-auth-card">
        <span class="ops-status ops-status-warning">Staff Access Required</span>
        <h3>Authentication required</h3>
        <p>This staff operations workspace requires a valid LinkCraftor staff session.</p>

        <button class="ops-dev-login-btn" type="button" id="ops-dev-login-btn">
          Start Dev Staff Session
        </button>
      </div>
    `;

    const devLoginBtn = document.getElementById("ops-dev-login-btn");

    if (devLoginBtn) {
      devLoginBtn.addEventListener("click", function () {
        window.localStorage.setItem("linkcraftor_ops_staff_session", "dev_staff_session");
        window.localStorage.setItem("linkcraftor_ops_staff_role", "support");
        window.location.reload();
      });
    }

    console.warn("LinkCraftor ops shell waiting for staff authentication");
    return;
  }

  function canAccessRoute(route) {
    const allowedRoles = routePermissions[route] || [];
    return allowedRoles.includes(staffRole);
  }

  function bindThreadOpeners() {
    const threadCards = document.querySelectorAll("[data-open-thread='true']");

    threadCards.forEach(function (card) {
      card.addEventListener("click", function () {
        const ticketId = card.dataset.ticketId || "TKT-1001";

        window.location.hash = "ticket_thread";

        setActiveNav("");

        content.innerHTML = renderTicketThreadWorkspace(ticketId);
        bindStaffActions();
        applyUiPermissionGuards(staffRole);
      });
    });
  }

  function bindStaffActions() {
    const actionButtons = document.querySelectorAll("[data-staff-action]");

    actionButtons.forEach(function (button) {
      button.addEventListener("click", function () {
        const actionName = button.dataset.staffAction || "unknown";
        const ticketId = button.dataset.ticketId || "unknown";

        handleStaffAction(actionName, ticketId);
      });
    });
  }

  function renderRoute(route) {
    try {
      if (!canAccessRoute(route)) {
        content.innerHTML = `
          <div class="ops-card ops-auth-card">
            <span class="ops-status ops-status-warning">Access Restricted</span>
            <h3>Role permission required</h3>
            <p>Your current role <strong>${staffRole}</strong> cannot access the <strong>${route}</strong> section.</p>
          </div>
        `;
        return;
      }

      if (route === "tickets") {
        content.innerHTML = renderAllTicketsQueue();
        bindQueueFilters(demoTickets);
        bindThreadOpeners();
        return;
      }

      if (route === "assigned") {
        content.innerHTML = renderAssignedToMeQueue();
        bindQueueFilters(demoTickets.filter(ticket => ticket.assignee === "me"));
        bindThreadOpeners();
        return;
      }

      if (route === "unassigned") {
        content.innerHTML = renderUnassignedQueue();
        bindQueueFilters(demoTickets.filter(ticket => !ticket.assignee));
        bindThreadOpeners();
        return;
      }

      if (route === "urgent") {
        content.innerHTML = renderUrgentQueue();
        bindQueueFilters(demoTickets.filter(ticket => ticket.priority === "Urgent"));
        bindThreadOpeners();
        return;
      }

      if (route === "engineering") {
        content.innerHTML = renderEngineeringQueue();
        bindQueueFilters(demoTickets.filter(ticket => ticket.queue === "engineering"));
        bindThreadOpeners();
        return;
      }

      if (route === "waiting_customer") {
        content.innerHTML = renderWaitingCustomerQueue();
        bindQueueFilters(demoTickets.filter(ticket => ticket.queue === "waiting_customer"));
        bindThreadOpeners();
        return;
      }

      if (route === "resolved") {
        content.innerHTML = renderResolvedQueue();
        bindQueueFilters(demoTickets.filter(ticket => ticket.queue === "resolved"));
        bindThreadOpeners();
        return;
      }

      if (route === "closed") {
        content.innerHTML = renderClosedQueue();
        bindQueueFilters(demoTickets.filter(ticket => ticket.queue === "closed"));
        bindThreadOpeners();
        return;
      }

      if (route === "ticket_thread") {
        content.innerHTML = renderTicketThreadWorkspace("TKT-1001");
        bindStaffActions();
        applyUiPermissionGuards(staffRole);
        return;
      }

      content.innerHTML = `
        <div class="ops-card">
          <span class="ops-status">Shell Active</span>
          <h3>${route.charAt(0).toUpperCase() + route.slice(1)}</h3>
          <p>Role-aware route loaded for <strong>${staffRole}</strong>.</p>
        </div>
      `;
    } catch (error) {
      console.error("Failed to render ops route", error);

      renderShellError(
        "Route failed to load",
        "The selected staff console section could not be rendered."
      );
    }
  }

  function setActiveNav(route) {
    navItems.forEach(function (item) {
      item.classList.toggle("active", item.dataset.route === route);
    });
  }

  navItems.forEach(function (item) {
    item.addEventListener("click", function (event) {
      event.preventDefault();

      const route = item.dataset.route || "dashboard";

      window.location.hash = route;

      setActiveNav(route);
      renderRoute(route);
    });
  });

  const initialRoute =
    (window.location.hash || "#dashboard").replace("#", "") || "dashboard";

  setActiveNav(initialRoute);
  renderRoute(initialRoute);

  app.dataset.shell = "ready";
  app.dataset.staffRole = staffRole;

  console.log("LinkCraftor ops shell initialized");
})();
