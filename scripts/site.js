document.querySelectorAll("[data-year]").forEach((node) => {
  node.textContent = String(new Date().getFullYear());
});

// Keep native touch scrolling, with explicit controls for mouse and keyboard.
document.querySelectorAll(".project-slider").forEach((slider) => {
  const gallery = slider.querySelector(".project-slides");
  const slides = [...gallery.querySelectorAll(".project-slide")];
  const controls = slider.querySelector(".gallery-controls");
  if (!controls || slides.length < 2) return;
  const previous = controls.querySelector("[data-gallery-previous]");
  const next = controls.querySelector("[data-gallery-next]");
  const status = controls.querySelector("[data-gallery-status]");
  const reducedMotion = matchMedia("(prefers-reduced-motion: reduce)");
  let index = 0;
  let frame;

  const update = () => {
    index = Math.round(gallery.scrollLeft / gallery.clientWidth);
    index = Math.max(0, Math.min(slides.length - 1, index));
    previous.disabled = index === 0;
    next.disabled = index === slides.length - 1;
    status.textContent = `${index + 1} / ${slides.length}`;
  };
  const go = (delta) => {
    const destination = Math.max(0, Math.min(slides.length - 1, index + delta));
    gallery.scrollTo({
      left: destination * gallery.clientWidth,
      behavior: reducedMotion.matches ? "instant" : "smooth",
    });
  };
  previous.addEventListener("click", () => go(-1));
  next.addEventListener("click", () => go(1));
  gallery.addEventListener("keydown", (event) => {
    if (event.key !== "ArrowLeft" && event.key !== "ArrowRight") return;
    event.preventDefault();
    go(event.key === "ArrowLeft" ? -1 : 1);
  });
  gallery.addEventListener(
    "scroll",
    () => {
      cancelAnimationFrame(frame);
      frame = requestAnimationFrame(update);
    },
    { passive: true },
  );
  new ResizeObserver(() => {
    gallery.scrollTo({
      left: index * gallery.clientWidth,
      behavior: "instant",
    });
    update();
  }).observe(gallery);
  controls.hidden = false;
  update();
});
