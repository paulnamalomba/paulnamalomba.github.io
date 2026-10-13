(() => {
  const mobileNavigation = window.matchMedia("(max-width: 680px)");
  const focusableSelector =
    'a[href], button:not([disabled]), input:not([disabled]), [tabindex="0"]';

  document
    .querySelectorAll("[data-menu-button], .hamburger")
    .forEach((button, index) => {
      const navigation =
        document.getElementById(button.getAttribute("aria-controls")) ||
        button
          .closest(".nav-shell, nav")
          ?.querySelector("[data-nav], .nav-links");
      if (!navigation) return;

      document.documentElement.classList.add("has-navigation");
      navigation.id ||= `site-navigation-${index + 1}`;
      button.type = "button";
      button.setAttribute("aria-controls", navigation.id);
      button.setAttribute("aria-expanded", "false");
      const inertRegions = new Map();
      let open = false;

      const setOpen = (next, { restoreFocus = false } = {}) => {
        open = next && mobileNavigation.matches;
        button.setAttribute("aria-expanded", String(open));
        button.classList.toggle("active", open);
        navigation.classList.toggle("open", open);
        document.body.classList.toggle("menu-open", open);

        if (open) {
          for (const region of document.body.children) {
            if (
              region.contains(button) ||
              region.contains(navigation) ||
              region.matches("script, style, link")
            )
              continue;
            inertRegions.set(region, region.hasAttribute("inert"));
            region.setAttribute("inert", "");
          }
          navigation.querySelector(focusableSelector)?.focus();
        } else {
          for (const [region, wasInert] of inertRegions) {
            region.toggleAttribute("inert", wasInert);
          }
          inertRegions.clear();
          if (restoreFocus) button.focus();
        }
      };

      button.addEventListener("click", () => setOpen(!open));
      navigation.querySelectorAll("a[href]").forEach((link) => {
        link.addEventListener("click", () => {
          if (!open) return;
          setOpen(false);
          const destination = new URL(link.href, location.href);
          if (
            destination.origin === location.origin &&
            destination.pathname === location.pathname &&
            destination.hash
          ) {
            const target = document.getElementById(
              decodeURIComponent(destination.hash.slice(1)),
            );
            if (target) {
              target.setAttribute("tabindex", "-1");
              target.focus({ preventScroll: true });
            }
          }
        });
      });

      document.addEventListener("keydown", (event) => {
        if (!open) return;
        if (event.key === "Escape") {
          event.preventDefault();
          setOpen(false, { restoreFocus: true });
        } else if (event.key === "Tab") {
          const controls = [
            button,
            ...navigation.querySelectorAll(focusableSelector),
          ];
          const current = controls.indexOf(document.activeElement);
          if (event.shiftKey && current <= 0) {
            event.preventDefault();
            controls.at(-1)?.focus();
          } else if (
            !event.shiftKey &&
            (current === controls.length - 1 || current === -1)
          ) {
            event.preventDefault();
            button.focus();
          }
        }
      });

      document.addEventListener("focusin", (event) => {
        if (
          open &&
          event.target !== button &&
          !navigation.contains(event.target)
        ) {
          navigation.querySelector(focusableSelector)?.focus();
        }
      });
      mobileNavigation.addEventListener("change", () => {
        const focusWasInMenu = navigation.contains(document.activeElement);
        const focusWasOnToggle = document.activeElement === button;
        setOpen(false);
        if (mobileNavigation.matches && focusWasInMenu) button.focus();
        if (!mobileNavigation.matches && focusWasOnToggle)
          navigation.querySelector(focusableSelector)?.focus();
      });
    });

  const dropdowns = [];
  const hoverAvailable = window.matchMedia(
    "(hover: hover) and (pointer: fine)",
  );
  document
    .querySelectorAll(
      ".nav-dropdown, .dropdown-menu, .dropdown-nested, .breadcrumb-dropdown",
    )
    .forEach((container, index) => {
      const panel = [...container.children].find((child) =>
        child.matches(
          ".dropdown-content, .dropdown-nested-content, .breadcrumb-dropdown-content",
        ),
      );
      let trigger =
        [...container.children].find((child) => child.matches("button")) ||
        [...container.children].find((child) =>
          child.matches("a, .breadcrumb-dropdown-btn"),
        );
      if (!panel || !trigger) return;
      document.documentElement.classList.add("has-dropdowns");

      if (trigger.tagName === "A" && trigger.getAttribute("href") !== "#") {
        const toggle = document.createElement("button");
        toggle.className = "submenu-toggle";
        toggle.setAttribute(
          "aria-label",
          `Toggle ${trigger.textContent.trim()} links`,
        );
        toggle.innerHTML =
          '<svg viewBox="0 0 24 24" width="18" height="18" aria-hidden="true"><path d="m6 9 6 6 6-6" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>';
        panel.before(toggle);
        trigger = toggle;
      } else if (trigger.tagName !== "BUTTON") {
        const toggle = document.createElement("button");
        toggle.className = trigger.className;
        toggle.innerHTML = trigger.innerHTML;
        trigger.replaceWith(toggle);
        trigger = toggle;
      }
      trigger.classList.add("dropdown-button");
      trigger.type = "button";
      panel.id ||= `dropdown-panel-${index + 1}`;
      trigger.setAttribute("aria-controls", panel.id);
      trigger.setAttribute("aria-expanded", "false");
      panel.hidden = true;

      const setOpen = (open) => {
        container.classList.toggle("open", open);
        trigger.setAttribute("aria-expanded", String(open));
        panel.hidden = !open;
        if (open && getComputedStyle(panel).position !== "static") {
          panel.style.removeProperty("left");
          panel.style.removeProperty("right");
          if (panel.getBoundingClientRect().right > window.innerWidth - 16) {
            panel.style.left = "auto";
            panel.style.right = "0";
          }
        }
        if (!open) {
          for (const child of dropdowns) {
            if (
              child.container !== container &&
              container.contains(child.container)
            )
              child.close();
          }
        }
      };
      const close = () => setOpen(false);
      dropdowns.push({ container, close });
      const toggle = () => {
        const open = trigger.getAttribute("aria-expanded") !== "true";
        if (open) {
          for (const other of dropdowns) {
            if (!other.container.contains(container)) other.close();
          }
        }
        setOpen(open);
      };

      trigger.addEventListener("click", toggle);
      trigger.addEventListener("keydown", (event) => {
        if (event.key === "ArrowDown" || event.key === "ArrowUp") {
          event.preventDefault();
          setOpen(true);
          const links = [...panel.querySelectorAll(focusableSelector)].filter(
            (link) => !link.closest("[hidden]"),
          );
          (event.key === "ArrowDown" ? links[0] : links.at(-1))?.focus();
        }
      });
      container.addEventListener("keydown", (event) => {
        if (event.key === "Escape" && container.classList.contains("open")) {
          event.preventDefault();
          event.stopPropagation();
          close();
          trigger.focus();
        }
      });
      container.addEventListener("focusout", (event) => {
        if (!container.contains(event.relatedTarget)) close();
      });
      container.addEventListener("pointerenter", (event) => {
        if (hoverAvailable.matches && event.pointerType === "mouse")
          setOpen(true);
      });
      container.addEventListener("pointerleave", () => {
        if (
          hoverAvailable.matches &&
          !container.contains(document.activeElement)
        )
          close();
      });
    });
  document.addEventListener("click", (event) => {
    for (const dropdown of dropdowns) {
      if (!dropdown.container.contains(event.target)) dropdown.close();
    }
  });

  document
    .querySelectorAll(".expand-btn, .qa-question")
    .forEach((button, index) => {
      const container =
        button.closest(".hub-card, .qa-item") || button.parentElement;
      const panel = button.nextElementSibling?.matches(".qa-answer")
        ? button.nextElementSibling
        : container.querySelector(".expand-wrapper, .qa-answer");
      if (!panel) return;
      document.documentElement.classList.add("has-disclosures");
      button.removeAttribute("onclick");
      button.type = "button";
      panel.id ||= `disclosure-panel-${index + 1}`;
      button.setAttribute("aria-controls", panel.id);
      const collapsedLabel = button.textContent.trim();
      const setExpanded = (expanded) => {
        button.setAttribute("aria-expanded", String(expanded));
        panel.hidden = !expanded;
        container.classList.toggle(
          button.matches(".expand-btn") ? "expanded" : "open",
          expanded,
        );
        if (button.matches(".qa-question")) {
          button.classList.toggle("open", expanded);
          panel.classList.toggle("visible", expanded);
        }
        if (button.matches(".expand-btn"))
          button.textContent = expanded ? "Show less" : collapsedLabel;
      };
      setExpanded(
        container.classList.contains("expanded") ||
          button.classList.contains("open") ||
          panel.classList.contains("visible"),
      );
      button.addEventListener("click", () =>
        setExpanded(button.getAttribute("aria-expanded") !== "true"),
      );
    });
})();
