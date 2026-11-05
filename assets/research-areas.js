(() => {
  const disclosure = document.getElementById("research-areas");
  const data = document.getElementById("research-area-data");
  const host = disclosure?.querySelector(".year-blocks");
  if (!host || !data) return;

  const { rows, domains } = JSON.parse(data.textContent);
  const groups = new Map();
  const datedYears = new Set();
  let hasUndated = false;
  for (const row of rows) {
    if (row.year == null) hasUndated = true;
    else datedYears.add(row.year);
    const key = row.domain + "/" + (row.year ?? "Undated");
    if (!groups.has(key)) groups.set(key, []);
    groups.get(key).push(row);
  }
  const years = [...datedYears].sort((a, b) => a - b);
  if (hasUndated) years.push("Undated");

  function element(tag, text, className) {
    const node = document.createElement(tag);
    if (text != null) node.textContent = text;
    if (className) node.className = className;
    return node;
  }

  function dotGroup(outputs, cellWidth) {
    const step = 7.5;
    const columns = Math.max(1, Math.min(6, outputs.length, Math.floor((cellWidth - 4) / step)));
    const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
    svg.setAttribute("width", columns * step);
    svg.setAttribute("height", Math.ceil(outputs.length / columns) * step);
    svg.setAttribute("aria-hidden", "true");
    outputs.forEach((output, index) => {
      const line = Math.floor(index / columns);
      const dotsInLine = Math.min(columns, outputs.length - line * columns);
      const circle = document.createElementNS(svg.namespaceURI, "circle");
      circle.setAttribute("cx", (index % columns + 0.5 + (columns - dotsInLine) / 2) * step);
      circle.setAttribute("cy", (line + 0.5) * step);
      circle.setAttribute("r", 2.65);
      circle.dataset.output = output.id;
      svg.append(circle);
    });
    return svg;
  }

  function titleList(outputs) {
    const list = element("ul");
    for (const output of outputs) list.append(element("li", output.title));
    return list;
  }

  const detail = element("div", null, "titles");
  detail.id = "research-area-titles";
  detail.setAttribute("aria-live", "polite");
  let selectedKey = null;
  let activeButton = null;
  let detailRow = null;
  let narrow = false;

  function selectGroup(button, showAll = false) {
    activeButton?.setAttribute("aria-pressed", "false");
    activeButton?.removeAttribute("aria-controls");
    activeButton = button;
    selectedKey = button.dataset.key;
    button.setAttribute("aria-pressed", "true");
    button.setAttribute("aria-controls", detail.id);
    detail.remove();
    detailRow?.remove();
    detailRow = null;

    const outputs = groups.get(selectedKey);
    detail.replaceChildren(element("h3", button.getAttribute("aria-label")), titleList(outputs.slice(0, 3)));
    if (outputs.length > 3) {
      const remaining = outputs.length - 3;
      const more = element("details");
      const label = `Show ${remaining} more ${remaining === 1 ? "title" : "titles"}`;
      more.append(element("summary", label, "area-small"), titleList(outputs.slice(3)));
      more.open = showAll;
      detail.append(more);
    }

    const table = button.closest("table");
    if (narrow) {
      detailRow = element("tr");
      const cell = detailRow.insertCell();
      cell.colSpan = table.tHead.rows[0].cells.length;
      cell.append(detail);
      button.closest("tr").after(detailRow);
    } else {
      table.after(detail);
    }
  }

  function render(width) {
    const focusedKey = document.activeElement?.dataset.key;
    const focusedMore = detail.contains(document.activeElement);
    const showAll = Boolean(detail.querySelector("details[open]"));
    const labelWidth = Math.min(155, Math.max(106, Math.round(width * 0.25)));
    const available = width - labelWidth;
    const minimumCellWidth = window.matchMedia("(pointer: coarse)").matches ? 44 : 32;
    const capacity = available >= 16 * minimumCellWidth ? 16 : available >= 8 * minimumCellWidth ? 8 : 4;
    narrow = capacity === 4;
    const buttons = new Map();
    host.replaceChildren();

    for (let offset = 0; offset < years.length; offset += capacity) {
      const span = years.slice(offset, offset + capacity);
      const table = element("table", null, "area-small");
      const range = span.length === 1 ? span[0] : span[0] + "–" + span[span.length - 1];
      table.setAttribute("aria-label", "Research outputs by area, " + range);
      const columns = element("colgroup");
      const labelColumn = element("col");
      labelColumn.style.width = labelWidth + "px";
      columns.append(labelColumn);
      for (const year of span) columns.append(element("col"));
      table.append(columns);
      const header = table.createTHead().insertRow();
      for (const value of ["Research area", ...span]) {
        const heading = element("th", value, "area-num");
        heading.scope = "col";
        header.append(heading);
      }
      const body = table.createTBody();
      for (const [domain, name] of Object.entries(domains)) {
        const row = body.insertRow();
        const heading = element("th", name);
        heading.scope = "row";
        row.append(heading);
        for (const year of span) {
          const key = domain + "/" + year;
          const cell = row.insertCell();
          cell.className = "year-cell";
          const outputs = groups.get(key);
          if (!outputs) continue;
          const button = element("button", null, "dots");
          button.type = "button";
          button.dataset.key = key;
          const count = outputs.length === 1 ? "1 output" : outputs.length + " outputs";
          button.setAttribute("aria-label", `${name} · ${year} · ${count}`);
          button.setAttribute("aria-pressed", "false");
          button.title = button.getAttribute("aria-label");
          button.append(dotGroup(outputs, available / span.length));
          cell.append(button);
          buttons.set(key, button);
        }
      }
      host.append(table);
    }
    if (buttons.has(selectedKey)) selectGroup(buttons.get(selectedKey), showAll);
    if (buttons.has(focusedKey)) buttons.get(focusedKey).focus({ preventScroll: true });
    if (focusedMore) detail.querySelector("summary")?.focus({ preventScroll: true });
  }

  host.addEventListener("click", event => {
    const button = event.target.closest("button.dots");
    if (button && button !== activeButton) selectGroup(button);
  });

  let lastWidth = 0;
  function draw() {
    if (!disclosure.open) return;
    const width = Math.floor(host.getBoundingClientRect().width);
    if (width > 0 && width !== lastWidth) {
      lastWidth = width;
      render(width);
    }
  }
  disclosure.addEventListener("toggle", draw);
  if ("ResizeObserver" in window) new ResizeObserver(draw).observe(host);
  else window.addEventListener("resize", draw);
  draw();
})();
