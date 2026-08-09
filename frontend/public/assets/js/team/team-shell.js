(function initLinkCraftorTeamShell() {
  const app = document.getElementById("team-app");

  if (!app) {
    console.error(
      "LinkCraftor Team Dashboard failed to initialize: #team-app missing."
    );

    return;
  }

  const collapseButton =
    document.getElementById("team-collapse-btn");

  const navItems =
    document.querySelectorAll("[data-team-route]");

  const groupToggles =
    document.querySelectorAll("[data-team-toggle]");


  function setActiveRoute(route) {
    navItems.forEach(function (item) {
      item.classList.toggle(
        "active",
        item.dataset.teamRoute === route
      );
    });
  }


  navItems.forEach(function (item) {
    item.addEventListener("click", function () {
      const route =
        item.dataset.teamRoute || "dashboard";

      setActiveRoute(route);

      console.log(
        "LinkCraftor Team route selected:",
        route
      );
    });
  });


  groupToggles.forEach(function (button) {
    button.addEventListener("click", function () {
      const target =
        button.dataset.teamToggle;

      const submenu =
        document.querySelector(
          `[data-team-submenu="${target}"]`
        );

      if (!submenu) {
        return;
      }

      submenu.classList.toggle("open");
    });
  });


  if (collapseButton) {
    collapseButton.addEventListener(
      "click",
      function () {
        app.classList.toggle("sidebar-collapsed");

        collapseButton.firstChild.textContent =
          app.classList.contains("sidebar-collapsed")
            ? "›"
            : "‹";
      }
    );
  }


  console.log(
    "LinkCraftor Team Dashboard shell initialized."
  );
})();
