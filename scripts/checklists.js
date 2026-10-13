(() => {
  const progress = document.querySelector("[data-checklist-storage]");
  if (!progress) return;
  const storageKey = progress.dataset.checklistStorage;
  const items = [...document.querySelectorAll(".checklist-item[data-key]")];
  let saved = {};
  try {
    const value = JSON.parse(localStorage.getItem(storageKey) || "{}");
    if (value && typeof value === "object" && !Array.isArray(value))
      saved = value;
  } catch {
    // The checklist remains usable when saved data or storage is unavailable.
  }

  function updateProgress() {
    const checked = items.filter(
      (item) => item.querySelector("input").checked,
    ).length;
    const percent = items.length
      ? Math.round((checked / items.length) * 100)
      : 0;
    document.getElementById("progressCount").textContent =
      `${checked} / ${items.length}`;
    const bar = document.getElementById("progressBar");
    bar.style.width = `${percent}%`;
    bar.setAttribute("aria-valuenow", percent);
    bar.classList.toggle("complete", percent === 100);
  }

  items.forEach((item) => {
    const checkbox = item.querySelector('input[type="checkbox"]');
    checkbox.checked = saved[item.dataset.key] === true;
    item.classList.toggle("checked", checkbox.checked);
    checkbox.addEventListener("change", () => {
      item.classList.toggle("checked", checkbox.checked);
      saved[item.dataset.key] = checkbox.checked;
      try {
        localStorage.setItem(storageKey, JSON.stringify(saved));
      } catch {
        // Keep the current session interactive even without persistence.
      }
      updateProgress();
    });
  });
  document.getElementById("resetBtn")?.addEventListener("click", () => {
    if (!confirm("Reset all checklist progress on this page?")) return;
    saved = {};
    items.forEach((item) => {
      item.querySelector("input").checked = false;
      item.classList.remove("checked");
    });
    try {
      localStorage.removeItem(storageKey);
    } catch {
      // Reset still applies to the current page when persistence is unavailable.
    }
    updateProgress();
  });
  updateProgress();
})();
