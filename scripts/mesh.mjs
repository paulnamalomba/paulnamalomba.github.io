// An illustrative parametric surface, rather than a physical simulation.
// The same renderer produces the static SVG fallback and the interactive study.
export function renderMesh(imprints = []) {
  const columns = 72;
  const rows = 12;
  const points = [];
  for (let i = 0; i <= columns; i += 1) {
    const u = (i / columns) * Math.PI * 2;
    points[i] = [];
    for (let j = 0; j <= rows; j += 1) {
      const v = (j / rows - 0.5) * 0.86;
      const radius = 1.4 + v * Math.cos(u / 2);
      const x = radius * Math.cos(u);
      const y = radius * Math.sin(u);
      const z = v * Math.sin(u / 2) * 1.46 + Math.sin(u * 2) * 0.09;
      const baseX = 310 + (x * 0.94 + y * 0.34) * 147;
      const baseY = 275 + (y * 0.56 - x * 0.17 - z * 0.96) * 147;
      // A local Gaussian dent keeps nearby mesh lines connected and leaves the rest intact.
      let dent = 0;
      for (const imprint of imprints) {
        const dx = baseX - imprint.x;
        const dy = baseY - imprint.y;
        dent +=
          imprint.strength * Math.exp(-(dx * dx + dy * dy) / (2 * 74 * 74));
      }
      points[i][j] = {
        x: baseX + dent * 0.14,
        y: baseY + dent * 0.7,
        depth: y * 0.8 + z * 0.6 - dent / 100,
      };
    }
  }
  const faces = [];
  for (let i = 0; i < columns; i += 1) {
    for (let j = 0; j < rows; j += 1) {
      const corners = [
        points[i][j],
        points[i + 1][j],
        points[i + 1][j + 1],
        points[i][j + 1],
      ];
      const light =
        43 + 17 * Math.sin((i / columns) * Math.PI * 2 - 0.5) + (j / rows) * 9;
      const coords = corners
        .map((p) => `${p.x.toFixed(2)},${p.y.toFixed(2)}`)
        .join(" ");
      faces.push({
        depth: corners.reduce((sum, p) => sum + p.depth, 0) / 4,
        markup: `<polygon points="${coords}" fill="hsl(226 76% ${light.toFixed(1)}%)" stroke="#d7e3ff" stroke-opacity=".7" stroke-width=".55" stroke-linejoin="round"/>`,
      });
    }
  }
  return faces
    .sort((a, b) => a.depth - b.depth)
    .map((face) => face.markup)
    .join("");
}

if (typeof document !== "undefined") {
  const study = document.querySelector("[data-mesh-study]");
  if (study) {
    const svg = study.querySelector(".mesh-interactive");
    const surface = study.querySelector("[data-mesh-surface]");
    const imprints = [];
    const pointers = new Map();
    let scale = 1;
    let panX = 0;
    let panY = 0;
    let lastPoint = null;
    let pinchDistance = 0;
    let frame = 0;
    const draw = () => {
      frame = 0;
      surface.innerHTML = renderMesh(imprints);
      surface.setAttribute(
        "transform",
        `translate(${panX} ${panY}) translate(310 275) scale(${scale}) translate(-310 -275)`,
      );
    };
    const schedule = () => {
      if (!frame) frame = requestAnimationFrame(draw);
    };
    const coords = (event) => {
      const point = svg.createSVGPoint();
      point.x = event.clientX;
      point.y = event.clientY;
      const local = point.matrixTransform(svg.getScreenCTM().inverse());
      return {
        x: 310 + (local.x - panX - 310) / scale,
        y: 275 + (local.y - panY - 275) / scale,
      };
    };
    const imprint = (point, strength = 18) => {
      imprints.push({ ...point, strength });
      if (imprints.length > 36) imprints.shift();
      schedule();
    };
    const zoom = (factor, x, y) => {
      const next = Math.max(0.65, Math.min(2.8, scale * factor));
      const ratio = next / scale;
      panX = x - 310 - (x - 310 - panX) * ratio;
      panY = y - 275 - (y - 275 - panY) * ratio;
      scale = next;
      schedule();
    };
    draw();
    study.classList.add("is-interactive");
    svg.addEventListener("pointerdown", (event) => {
      if (event.target.tagName.toLowerCase() !== "polygon") return;
      svg.setPointerCapture(event.pointerId);
      pointers.set(event.pointerId, { x: event.clientX, y: event.clientY });
      if (pointers.size === 1) {
        const point = coords(event);
        imprint(point);
        lastPoint = point;
      } else {
        const [a, b] = [...pointers.values()];
        pinchDistance = Math.hypot(a.x - b.x, a.y - b.y);
      }
    });
    svg.addEventListener("pointermove", (event) => {
      if (!pointers.has(event.pointerId)) return;
      pointers.set(event.pointerId, { x: event.clientX, y: event.clientY });
      if (pointers.size === 2) {
        const [a, b] = [...pointers.values()];
        const distance = Math.hypot(a.x - b.x, a.y - b.y);
        const rect = svg.getBoundingClientRect();
        const center = {
          x: (((a.x + b.x) / 2 - rect.left) * 620) / rect.width,
          y: (((a.y + b.y) / 2 - rect.top) * 550) / rect.height,
        };
        if (pinchDistance) zoom(distance / pinchDistance, center.x, center.y);
        pinchDistance = distance;
      } else if (pointers.size === 1) {
        const point = coords(event);
        if (
          !lastPoint ||
          Math.hypot(point.x - lastPoint.x, point.y - lastPoint.y) > 16
        ) {
          imprint(point, 8);
          lastPoint = point;
        }
      }
    });
    const release = (event) => {
      pointers.delete(event.pointerId);
      lastPoint = null;
      pinchDistance = 0;
    };
    svg.addEventListener("pointerup", release);
    svg.addEventListener("pointercancel", release);
    svg.addEventListener(
      "wheel",
      (event) => {
        event.preventDefault();
        const rect = svg.getBoundingClientRect();
        zoom(
          Math.exp(-event.deltaY * 0.001),
          ((event.clientX - rect.left) * 620) / rect.width,
          ((event.clientY - rect.top) * 550) / rect.height,
        );
      },
      { passive: false },
    );
    svg.addEventListener("keydown", (event) => {
      if (event.key === "+" || event.key === "=") zoom(1.15, 310, 275);
      else if (event.key === "-" || event.key === "_") zoom(1 / 1.15, 310, 275);
      else if (event.key === "Enter" || event.key === " ") {
        event.preventDefault();
        imprint({ x: 310, y: 275 });
      } else return;
      event.preventDefault();
    });
  }
}
