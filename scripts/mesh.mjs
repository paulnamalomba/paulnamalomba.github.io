// An illustrative parametric surface, rather than a physical simulation.
// The same renderer produces the static SVG fallback and the interactive study.
export function renderMesh(deformation = 0.6) {
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
      const z =
        v * Math.sin(u / 2) * (0.5 + deformation * 1.6) +
        Math.sin(u * 2) * deformation * 0.15;
      points[i][j] = {
        x: 310 + (x * 0.94 + y * 0.34) * 147,
        y: 275 + (y * 0.56 - x * 0.17 - z * 0.96) * 147,
        depth: y * 0.8 + z * 0.6,
        z,
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
    const surface = study.querySelector("[data-mesh-surface]");
    const control = study.querySelector("input");
    const draw = () => {
      surface.innerHTML = renderMesh(Number(control.value) / 100);
      control.setAttribute("aria-valuetext", `${control.value}% deformation`);
    };
    draw();
    study.classList.add("is-interactive");
    control.addEventListener("input", draw);
  }
}
