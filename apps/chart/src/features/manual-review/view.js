export function reviewView(app, state) {
  const get = (id) => app.querySelector(`#${id}`);
  const ids = ["from", "to", "filter-search", "record-search"];
  const filters = [...app.querySelectorAll(".category-filter")];
  const formats = [...app.querySelectorAll('#export-form input[name="format"]')];
  const detailKey = (details) => {
    const { timeGroup, filterGroup, bridgeId } = details.dataset;
    if (timeGroup) return `day:${timeGroup}`;
    if (filterGroup) return `filter:${filterGroup}`;
    if (bridgeId) return `bridge:${bridgeId}`;
    return details.querySelector("summary strong")?.textContent;
  };
  if (!state) return {
    values: Object.fromEntries(ids.map(id => [id, get(id)?.value || ""])),
    open: [...app.querySelectorAll("details[open]")].map(detailKey),
    filters: filters.map(input => [input.value, input.checked]),
    families: [...app.querySelectorAll("[data-filter-parent]")].map(input => [
      input.dataset.filterParent, input.indeterminate ? null : input.checked,
    ]),
    collapsed: Boolean(get("filter-groups")?.hidden),
    includeBridge: get("include-bridge")?.checked ?? true,
    exportFormats: formats.length ? formats.filter(input => input.checked).map(input => input.value) : null,
    exportOpen: get("export-dialog")?.open ?? false,
  };

  for (const id of ids) get(id).value = state.values?.[id] ?? "";
  get("include-bridge").checked = state.includeBridge ?? true;
  if (state.exportFormats) {
    const selected = new Set(state.exportFormats);
    for (const input of formats) input.checked = selected.has(input.value);
  }
  const open = new Set(state.open);
  for (const details of app.querySelectorAll("details")) {
    if (open.has(detailKey(details))) details.open = true;
  }
  const oldFilters = new Map(state.filters);
  const oldFamilies = new Map(state.families);
  for (const input of filters) {
    input.checked = oldFilters.get(input.value) ?? oldFamilies.get(input.dataset.filterFamily) ?? input.checked;
  }
  if (state.collapsed && !state.values?.["filter-search"]) {
    const toggle = app.querySelector(".filter-all-toggle");
    toggle.setAttribute("aria-expanded", "false");
    toggle.setAttribute("aria-label", "Expand all filters");
    get("filter-groups").hidden = true;
  }
}
