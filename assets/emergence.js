(() => {
  const heading = document.querySelector("h1");
  if (!heading) return;

  const columns = 48;
  const rows = 20;
  const cellSize = 12;
  const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)");
  let cells = new Uint8Array(columns * rows);
  let nextCells = new Uint8Array(cells.length);
  let typed = "";
  let timer = null;
  let paused = reducedMotion.matches;
  let previousFocus = null;

  const figure = document.createElement("figure");
  figure.id = "emergence";
  figure.hidden = true;
  figure.innerHTML = `
    <button type="button" class="emergence-grid" aria-label="Seed a new Game of Life pattern" title="Click to seed a new pattern">
      <canvas width="576" height="240" aria-hidden="true"></canvas>
    </button>
    <figcaption>Simple rules. Complicated cultures.</figcaption>
    <div class="emergence-controls">
      <button type="button" class="emergence-pause">Pause</button>
      <button type="button" class="emergence-hide" title="Escape">Hide</button>
    </div>
  `;
  const canvas = figure.querySelector("canvas");
  const context = canvas.getContext("2d");
  if (!context) return;

  const grid = figure.querySelector(".emergence-grid");
  const pauseButton = figure.querySelector(".emergence-pause");
  heading.after(figure);

  function draw() {
    context.clearRect(0, 0, canvas.width, canvas.height);
    context.fillStyle = "#222";
    context.beginPath();
    cells.forEach((alive, index) => {
      if (!alive) return;
      const x = (index % columns + 0.5) * cellSize;
      const y = (Math.floor(index / columns) + 0.5) * cellSize;
      context.moveTo(x + 3.3, y);
      context.arc(x, y, 3.3, 0, Math.PI * 2);
    });
    context.fill();
  }

  function seed() {
    cells = Uint8Array.from(cells, () => Math.random() < 0.28 ? 1 : 0);
    draw();
  }

  function step() {
    for (let row = 0; row < rows; row++) {
      for (let column = 0; column < columns; column++) {
        let neighbours = 0;
        for (let dy = -1; dy <= 1; dy++) {
          for (let dx = -1; dx <= 1; dx++) {
            if (dx === 0 && dy === 0) continue;
            // Wrap the edges so patterns can travel across the small field.
            const y = (row + dy + rows) % rows;
            const x = (column + dx + columns) % columns;
            neighbours += cells[y * columns + x];
          }
        }
        const index = row * columns + column;
        nextCells[index] = neighbours === 3 || (cells[index] && neighbours === 2) ? 1 : 0;
      }
    }
    [cells, nextCells] = [nextCells, cells];
    draw();
  }

  function syncAnimation() {
    clearInterval(timer);
    timer = null;
    pauseButton.textContent = paused ? "Play" : "Pause";
    if (!figure.hidden && !document.hidden && !paused) {
      timer = setInterval(step, 180);
    }
  }

  function reveal() {
    if (figure.hidden) previousFocus = document.activeElement;
    figure.hidden = false;
    seed();
    syncAnimation();
    grid.focus({ preventScroll: true });
    figure.scrollIntoView({ block: "nearest" });
  }

  function hide() {
    const restoreFocus = figure.contains(document.activeElement);
    figure.hidden = true;
    typed = "";
    syncAnimation();
    if (restoreFocus) previousFocus?.focus({ preventScroll: true });
  }

  grid.addEventListener("click", seed);
  pauseButton.addEventListener("click", () => {
    paused = !paused;
    syncAnimation();
  });
  figure.querySelector(".emergence-hide").addEventListener("click", hide);
  document.addEventListener("visibilitychange", () => {
    typed = "";
    syncAnimation();
  });
  reducedMotion.addEventListener("change", () => {
    if (reducedMotion.matches) {
      paused = true;
      syncAnimation();
    }
  });

  document.addEventListener("keydown", event => {
    if (event.key === "Escape" && !figure.hidden) {
      hide();
      return;
    }
    if (event.defaultPrevented || event.isComposing || event.ctrlKey || event.metaKey || event.altKey ||
        event.target.isContentEditable || event.target.closest("input, textarea, select, [role='textbox']")) {
      typed = "";
      return;
    }
    if (event.repeat) return;
    if (event.key === "Shift") return;
    if (!/^[a-z]$/i.test(event.key)) {
      typed = "";
      return;
    }
    typed = (typed + event.key.toLowerCase()).slice(-"emergence".length);
    if (typed === "emergence") {
      typed = "";
      reveal();
    }
  });
})();
