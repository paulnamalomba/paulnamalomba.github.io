const header = document.querySelector("[data-header]");

const syncHeader = () =>
  header?.classList.toggle("scrolled", window.scrollY > 12);
syncHeader();
window.addEventListener("scroll", syncHeader, { passive: true });

document.querySelectorAll("[data-year]").forEach((node) => {
  node.textContent = String(new Date().getFullYear());
});
