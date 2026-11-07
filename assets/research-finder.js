(() => {
  const triggers = document.querySelectorAll("[data-research-finder]");
  if (!triggers.length || typeof HTMLDialogElement === "undefined" ||
      !HTMLDialogElement.prototype.showModal) return;

  const dialog = document.createElement("dialog");
  dialog.id = "research-finder";
  dialog.setAttribute("aria-labelledby", "research-finder-heading");
  dialog.innerHTML = `
    <header>
      <div class="research-finder-heading">
        <h2 id="research-finder-heading">Find research</h2>
        <button type="button" class="research-finder-close">Close</button>
      </div>
      <label class="research-finder-label" for="research-finder-query">Title, author, year or research area</label>
      <input id="research-finder-query" type="search" autocomplete="off" spellcheck="false"
        placeholder="e.g. text analysis, Eilam, 2024" aria-describedby="research-finder-help" aria-controls="research-finder-results">
      <p id="research-finder-status" role="status" aria-live="polite"></p>
    </header>
    <div class="research-finder-scroll">
      <ul id="research-finder-results" aria-label="Research outputs"></ul>
      <p class="research-finder-message" hidden></p>
    </div>
    <footer>
      <p id="research-finder-help">↑↓ browse · Enter open · Esc close</p>
      <a href="publications.html">All publications</a>
    </footer>
  `;
  document.body.append(dialog);

  const input = dialog.querySelector("input");
  const results = dialog.querySelector("ul");
  const status = dialog.querySelector("[role='status']");
  const message = dialog.querySelector(".research-finder-message");
  const scroll = dialog.querySelector(".research-finder-scroll");
  let records = null;
  let loading = false;
  let previousFocus = null;

  function normalize(text) {
    return String(text).toLowerCase().normalize("NFKD")
      .replace(/[\u0300-\u036f]/g, "")
      .replace(/æ/g, "ae").replace(/ø/g, "o").replace(/ß/g, "ss");
  }

  function publicationURL(record) {
    if (record.url) {
      try {
        const url = new URL(record.url, location.href);
        if (["https:", "http:"].includes(url.protocol)) return url.href;
      } catch { /* Fall back to the local citation for missing or invalid URLs. */ }
    }
    return `publications.html#publication-${record.id}`;
  }

  async function copyCitation(record, item, button) {
    try {
      await navigator.clipboard.writeText(record.citation);
      button.textContent = "Copied";
      status.textContent = "Citation copied.";
      setTimeout(() => { button.textContent = "Copy citation"; }, 1800);
    } catch {
      // Clipboard access can be unavailable or denied. Keep the citation usable.
      let field = item.querySelector("textarea");
      if (!field) {
        field = document.createElement("textarea");
        field.className = "research-finder-manual-copy";
        field.readOnly = true;
        field.rows = 4;
        field.setAttribute("aria-label", `Citation for ${record.title}`);
        field.value = record.citation;
        item.append(field);
      }
      field.focus();
      field.select();
      status.textContent = "Citation selected. Use your device’s copy command.";
    }
  }

  function render() {
    if (!records) return;
    const query = normalize(input.value).trim();
    const terms = query.match(/[\p{L}\p{N}]+/gu) || [];
    const matches = terms.length ? records
      .filter(record => terms.every(term => record.search.includes(term)))
      .map(record => ({ record, score: terms.reduce((score, term) => score +
        (record.searchTitle.includes(term) ? 5 : 0) +
        (String(record.year) === term ? 4 : 0) +
        (record.searchArea.includes(term) ? 3 : 0), 0) }))
      .sort((a, b) => b.score - a.score || (b.record.year || 0) - (a.record.year || 0))
      .map(match => match.record) : records.slice(0, 8);

    status.textContent = terms.length
      ? `${matches.length} ${matches.length === 1 ? "result" : "results"}`
      : `${records.length} research outputs · ${matches.length} most recent`;
    results.replaceChildren();
    message.hidden = matches.length > 0;
    message.textContent = "No matching research. Try a different title, author, year or area.";
    const fragment = document.createDocumentFragment();
    matches.forEach(record => {
      const item = document.createElement("li");
      item.className = "research-finder-result";
      const link = document.createElement("a");
      link.className = "research-finder-title";
      link.href = publicationURL(record);
      link.textContent = record.title;
      // A local citation may be on this very page; dismiss the dialog before navigating.
      link.addEventListener("click", () => dialog.close());
      const foot = document.createElement("div");
      foot.className = "research-finder-result-foot";
      const meta = document.createElement("span");
      meta.className = "research-finder-meta";
      meta.textContent = `${record.year || "No year"} · ${record.area}`;
      const copy = document.createElement("button");
      copy.type = "button";
      copy.className = "research-finder-copy";
      copy.textContent = "Copy citation";
      copy.setAttribute("aria-label", `Copy citation for ${record.title}`);
      copy.addEventListener("click", () => copyCitation(record, item, copy));
      foot.append(meta, copy);
      item.append(link, foot);
      fragment.append(item);
    });
    results.append(fragment);
    scroll.scrollTop = 0;
  }

  async function load() {
    if (records || loading) return;
    loading = true;
    status.textContent = "Loading research…";
    message.hidden = true;
    try {
      const response = await fetch("assets/research-index.json");
      if (!response.ok) throw new Error("Research index unavailable");
      const data = await response.json();
      if (!Array.isArray(data.rows) || !data.domains || data.rows.some(row =>
        !Number.isInteger(row.id) || typeof row.title !== "string" || typeof row.citation !== "string")) {
        throw new Error("Invalid research index");
      }
      records = data.rows.map(row => {
        const area = data.domains[row.domain] || "Awaiting classification";
        return { ...row, area, searchTitle: normalize(row.title), searchArea: normalize(area),
          search: normalize(`${row.title} ${row.citation} ${row.year || ""} ${area}`) };
      }).sort((a, b) => (b.year || 0) - (a.year || 0));
      render();
    } catch {
      status.textContent = "Research search is unavailable.";
      message.replaceChildren("You can still browse the full publication list. ");
      const retry = document.createElement("button");
      retry.type = "button";
      retry.textContent = "Try again";
      retry.addEventListener("click", load);
      message.append(retry);
      message.hidden = false;
    } finally {
      loading = false;
    }
  }

  function open() {
    if (!dialog.open) {
      previousFocus = document.activeElement;
      dialog.showModal();
    }
    input.focus();
    input.select();
    load();
  }

  triggers.forEach(trigger => {
    trigger.setAttribute("aria-haspopup", "dialog");
    trigger.setAttribute("aria-controls", dialog.id);
    const shortcut = trigger.querySelector(".research-finder-shortcut");
    if (shortcut) {
      shortcut.textContent = /Mac|iPhone|iPad/.test(navigator.platform) ? "⌘K" : "Ctrl K";
      shortcut.setAttribute("aria-hidden", "true");
      shortcut.hidden = false;
    }
    trigger.addEventListener("click", event => {
      if (event.ctrlKey || event.metaKey || event.shiftKey || event.altKey) return;
      event.preventDefault();
      open();
    });
  });
  input.addEventListener("input", render);
  dialog.querySelector(".research-finder-close").addEventListener("click", () => dialog.close());
  dialog.addEventListener("close", () => previousFocus?.focus({ preventScroll: true }));
  dialog.addEventListener("click", event => {
    if (event.target !== dialog) return;
    const bounds = dialog.getBoundingClientRect();
    if (event.clientX < bounds.left || event.clientX > bounds.right ||
        event.clientY < bounds.top || event.clientY > bounds.bottom) dialog.close();
  });
  dialog.addEventListener("keydown", event => {
    if (event.isComposing) return;
    if (event.key === "Escape") {
      event.preventDefault();
      event.stopPropagation(); // Leave the existing emergence mode alone.
      dialog.close();
      return;
    }
    if (event.ctrlKey || event.metaKey || event.altKey || event.shiftKey ||
        event.target.closest("textarea")) return;
    const links = [...results.querySelectorAll(".research-finder-title")];
    const item = event.target.closest(".research-finder-result");
    if (event.key === "Enter" && event.target === input && links.length) {
      event.preventDefault();
      links[0].click();
    } else if (["ArrowDown", "ArrowUp"].includes(event.key) && (event.target === input || item)) {
      event.preventDefault();
      const index = item ? links.indexOf(item.querySelector("a")) : -1;
      const next = event.key === "ArrowDown" ? Math.min(index + 1, links.length - 1) : index - 1;
      if (next < 0) input.focus();
      else links[next]?.focus();
    }
  });
  document.addEventListener("keydown", event => {
    if (event.defaultPrevented || event.isComposing || event.repeat || event.altKey || event.shiftKey) return;
    if ((event.metaKey || event.ctrlKey) && event.key.toLowerCase() === "k") {
      event.preventDefault();
      open();
    }
  });
})();
