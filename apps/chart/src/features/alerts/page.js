import { icon } from "../../ui/icons.js";
import { mountWorkspaceHeader, restoreWorkspaceHeader } from "../../ui/workspace-state.js";
import { ALERT_DIRECTIONS, alertEventLabel, createAlertMonitor, DEFAULT_ALERT_SECONDS, MAX_ALERT_SECONDS, normalizeAlertRule } from "./rules.js";
import { createAlertSound } from "./sound.js";

const STORAGE_KEY = "qg:alert-rules:v1";
const EVENT_GROUPS = [
  ["Base behaviors", ["reaction", "blue-line", "a"]],
  ["Secondary behaviors", ["s-blue", "s-red", "e-red", "e-blue", "stopall-1", "stopall-2", "stopall-3", "stopall-4", "stopall-5", "stopall-6", "stopall"]],
  ["Primary structure", ["ph-1", "ph-2", "ph-3", "ph", "pl-1", "pl-2", "pl-3", "pl"]],
];
const CUSTOM_EVENT_LABELS = { stopall: "Other StopAll number…", ph: "Other PH number…", pl: "Other PL number…" };

function eventOptions(choices) {
  return EVENT_GROUPS.map(([label, entries], index) => {
    const directions = index < 2 ? ALERT_DIRECTIONS : [null];
    const options = directions.flatMap(direction => entries.map(entry => {
      const type = direction ? `${direction}:${entry}` : entry;
      const label = alertEventLabel(type) || `${direction ? `${direction === "bullish" ? "Bullish" : "Bearish"} ` : ""}${CUSTOM_EVENT_LABELS[entry]}`;
      return choices.includes(type) ? "" : `<option value="${type}">${label}</option>`;
    }));
    return `<optgroup label="${label}">${options.join("")}</optgroup>`;
  }).join("");
}

function readRules(window) {
  try {
    const value = JSON.parse(window.localStorage.getItem(STORAGE_KEY) || "[]");
    return Array.isArray(value) ? value.map(normalizeAlertRule).filter(Boolean) : [];
  } catch {
    return [];
  }
}

export function mountAlerts({ root, headerRoot, toast, createId, formatTime }) {
  const document = root.ownerDocument;
  const window = document.defaultView;
  const monitor = createAlertMonitor();
  const sound = createAlertSound(window, renderDelivery);
  const lastMatch = new Map();
  let rules = readRules(window);
  let draft;
  let editing = false;
  let visible = false;
  let liveStatus = "Open a RAW chart to monitor alerts.";

  const view = document.createElement("section");
  view.className = "alert-workspace";
  view.setAttribute("aria-labelledby", "alertWorkspaceTitle");
  view.hidden = true;
  view.innerHTML = `
    <header class="alert-workspace-header">
      <span class="alert-title-icon">${icon("bell", 18)}</span>
      <h1 id="alertWorkspaceTitle">Alert</h1>
    </header>
    <div class="alert-scroll">
      <div class="alert-layout">
        <section class="alert-monitor" aria-label="Alert monitoring">
          <div class="alert-monitor-copy">
            <strong>Live monitoring</strong>
            <span data-monitor-status role="status"></span>
          </div>
          <div class="alert-actions">
            <button type="button" class="btn" data-action="stop-sound" hidden>Stop sound</button>
            <button type="button" class="btn" data-action="notifications"></button>
          </div>
        </section>
        <section class="alert-panel alert-rules" aria-labelledby="alertRulesTitle">
          <header class="alert-panel-head"><h2 id="alertRulesTitle">Rules <span data-rule-count></span></h2>
            <button class="btn primary" data-action="new" type="button">${icon("plus", 15)} New rule</button>
          </header>
          <div data-rule-list></div>
        </section>
        <section class="alert-panel alert-editor" aria-labelledby="alertEditorTitle">
          <header class="alert-panel-head"><h2 id="alertEditorTitle" tabindex="-1">Rule editor</h2></header>
          <div class="alert-empty" data-editor-empty>
            <span class="alert-empty-icon">${icon("account_tree", 21)}</span>
            <strong>Build an alert sequence</strong>
            <p>Create a rule or choose a saved rule to edit its steps.</p>
          </div>
          <form data-editor hidden>
            <div class="alert-form-intro">
              <label class="alert-field">Rule name<input name="ruleName" required autocomplete="off" placeholder="rule-1"></label>
              <label class="alert-toggle"><span>Rule enabled</span><span class="master-switch"><input name="enabled" type="checkbox" role="switch"><span aria-hidden="true"></span></span></label>
            </div>
            <section class="alert-form-section" aria-labelledby="alertSequenceTitle">
              <h3 id="alertSequenceTitle">Event sequence</h3>
              <p class="alert-help">Any event in a step can match. Each next step must occur later.</p>
              <ol class="alert-steps" data-steps></ol>
              <button type="button" class="btn" data-action="add-step">${icon("plus", 15)} Add step</button>
            </section>
            <section class="alert-form-section alert-sound" aria-labelledby="alertSoundTitle">
              <h3 id="alertSoundTitle">Alert sound</h3>
              <div class="alert-sound-controls">
                <label class="alert-toggle"><span>Play sound</span><span class="master-switch"><input name="sound" type="checkbox" role="switch"><span aria-hidden="true"></span></span></label>
                <label class="alert-field alert-duration">Duration in seconds<input required name="seconds" type="number" min="1" max="${MAX_ALERT_SECONDS}" step="1"></label>
                <button type="button" class="btn" data-action="test-sound">${icon("play", 15)} Test sound</button>
              </div>
            </section>
            <p class="alert-error" data-form-error role="alert" hidden></p>
            <footer class="alert-editor-actions">
              <button class="btn danger" data-action="delete" type="button" hidden>Delete rule</button>
              <div class="alert-actions"><button class="btn" data-action="cancel" type="button">Cancel</button><button class="btn primary" type="submit">Save rule</button></div>
            </footer>
          </form>
        </section>
      </div>
    </div>`;
  root.append(view);
  const find = selector => view.querySelector(selector);
  const header = find(".alert-workspace-header");
  const form = find("[data-editor]");
  const fields = form.elements;
  const steps = find("[data-steps]");

  function renderDelivery() {
    find('[data-action="stop-sound"]').hidden = !sound.isPlaying();
    const button = find('[data-action="notifications"]');
    const permission = window.Notification?.permission;
    button.hidden = !permission;
    button.disabled = permission !== "default";
    button.textContent = permission === "granted" ? "Desktop notifications on"
      : permission === "denied" ? "Desktop notifications blocked" : "Enable desktop notifications";
    button.title = permission === "denied" ? "Allow notifications in your browser’s site settings." : "";
  }

  function renderRules() {
    const list = find("[data-rule-list]");
    find("[data-rule-count]").textContent = rules.length;
    if (!rules.length) {
      list.innerHTML = '<p class="alert-list-empty">No rules yet.</p>';
      return;
    }
    const focused = list.contains(document.activeElement) ? document.activeElement.dataset.ruleId : null;
    list.replaceChildren(...rules.map(rule => {
      const row = document.createElement("button");
      row.type = "button";
      row.className = "alert-rule-row";
      row.dataset.ruleId = rule.id;
      row.setAttribute("aria-pressed", String(draft?.id === rule.id));
      row.innerHTML = `<span class="alert-rule-row-top"><strong></strong><span class="alert-rule-state" data-enabled="${rule.enabled}">${rule.enabled ? "Enabled" : "Disabled"}</span></span><span class="alert-rule-summary"></span><span class="alert-rule-meta"></span>`;
      row.querySelector("strong").textContent = rule.name;
      row.querySelector(".alert-rule-summary").textContent = rule.steps.map(step => step.map(alertEventLabel).join(" or ")).join(" → ");
      const progress = monitor.progress(rule.id);
      const hit = lastMatch.get(rule.id);
      row.querySelector(".alert-rule-meta").textContent = [
        progress ? `${progress}/${rule.steps.length} steps matched` : rule.sound ? `${rule.seconds}s sound` : "Sound off",
        hit ? `Triggered ${hit}` : "",
      ].filter(Boolean).join(" · ");
      return row;
    }));
    if (focused) [...list.children].find(row => row.dataset.ruleId === focused)?.focus();
  }

  function renderSteps() {
    steps.innerHTML = draft.steps.map((choices, index) => `
      <li class="alert-step" data-step="${index}">
        <span class="alert-step-number" aria-hidden="true">${index + 1}</span>
        <div class="alert-step-body">
          <div class="alert-step-head"><strong>Step ${index + 1}</strong><div class="alert-actions">
            <button class="icon-btn" type="button" data-action="move-up" ${index === 0 ? "disabled" : ""} aria-label="Move step ${index + 1} up" title="Move up">${icon("chevron", 16)}</button>
            <button class="icon-btn" type="button" data-action="move-down" ${index === draft.steps.length - 1 ? "disabled" : ""} aria-label="Move step ${index + 1} down" title="Move down">${icon("chevron", 16)}</button>
            <button class="icon-btn danger" type="button" data-action="remove-step" ${draft.steps.length === 1 ? "disabled" : ""} aria-label="Remove step ${index + 1}" title="Remove step">${icon("trash", 16)}</button>
          </div></div>
          <div class="alert-choices">${choices.map((type, choice) => `${choice ? '<span class="alert-or">OR</span>' : ""}<span class="alert-choice" data-event="${type}">${alertEventLabel(type)}<button type="button" data-action="remove-event" data-choice="${choice}" aria-label="Remove ${alertEventLabel(type)} from step ${index + 1}">${icon("close", 14)}</button></span>`).join("")}</div>
          <div class="alert-event-picker">
            <select aria-label="Add event to step ${index + 1}" data-event-picker>
              <option value="">Add an event…</option>
              ${eventOptions(choices)}
            </select>
            <div class="alert-custom-event" data-custom-event hidden>
              <input type="number" min="1" step="1" aria-label="Event number for step ${index + 1}" placeholder="Number" disabled>
              <button class="btn" type="button" data-action="add-custom-event">Add</button>
            </div>
          </div>
        </div>
      </li>`).join("");
  }

  function setError(message = "") {
    const error = find("[data-form-error]");
    error.textContent = message;
    error.hidden = !message;
  }

  function showEditor(rule) {
    editing = Boolean(rule);
    draft = rule ? { ...rule, steps: rule.steps.map(step => [...step]) } : {
      id: createId(), name: "", enabled: true, sound: true, seconds: DEFAULT_ALERT_SECONDS, steps: [[]],
    };
    find("#alertEditorTitle").textContent = editing ? "Edit rule" : "New rule";
    find("[data-editor-empty]").hidden = true;
    form.hidden = false;
    find('[data-action="delete"]').hidden = !editing;
    fields.ruleName.value = draft.name;
    fields.enabled.checked = draft.enabled;
    fields.sound.checked = draft.sound;
    fields.seconds.value = draft.seconds;
    updateSoundFields();
    setError();
    renderSteps();
    renderRules();
    fields.ruleName.focus();
  }

  function closeEditor() {
    draft = null;
    form.hidden = true;
    find("[data-editor-empty]").hidden = false;
    find("#alertEditorTitle").textContent = "Rule editor";
    renderRules();
    find('[data-action="new"]').focus();
  }

  function updateSoundFields() {
    fields.seconds.disabled = !fields.sound.checked;
    find('[data-action="test-sound"]').disabled = !fields.sound.checked;
  }

  function persist(id, changed) {
    try {
      const next = readRules(window);
      const index = next.findIndex(rule => rule.id === id);
      if (index === -1 && changed) next.push(changed);
      else if (index !== -1 && changed) next[index] = changed;
      else if (index !== -1) next.splice(index, 1);
      window.localStorage.setItem(STORAGE_KEY, JSON.stringify(next));
      rules = next;
    } catch {
      setError("Could not save rules in this browser.");
      return false;
    }
    monitor.resetRule(id);
    return true;
  }

  function enableSound() {
    return sound.prepare().catch(() => false);
  }

  function focusPicker(index) {
    steps.querySelector(`[data-step="${index}"] [data-event-picker]`)?.focus();
  }

  function addEvent(index, type) {
    if (!draft.steps[index].includes(type)) draft.steps[index].push(type);
    setError();
    renderSteps();
    focusPicker(index);
  }

  form.addEventListener("submit", event => {
    event.preventDefault();
    const rule = normalizeAlertRule({ ...draft, name: fields.ruleName.value, enabled: fields.enabled.checked,
      sound: fields.sound.checked, seconds: fields.sound.checked ? fields.seconds.value : draft.seconds });
    if (!rule) {
      setError(fields.ruleName.value.trim() ? "Add at least one event to every step." : "Enter a rule name.");
      if (!fields.ruleName.value.trim()) fields.ruleName.focus();
      else focusPicker(draft.steps.findIndex(step => !step.length));
      return;
    }
    if (!persist(rule.id, rule)) return;
    if (rule.enabled && rule.sound) void enableSound();
    lastMatch.delete(rule.id);
    toast(`Alert rule saved: ${rule.name}`, "success");
    closeEditor();
  });

  view.addEventListener("change", event => {
    const select = event.target;
    if (select === fields.sound) updateSoundFields();
    if (!select.matches("[data-event-picker]")) return;
    const step = select.closest("[data-step]");
    const custom = step.querySelector("[data-custom-event]");
    const number = custom.querySelector("input");
    const needsNumber = Boolean(select.value && !alertEventLabel(select.value));
    custom.hidden = number.disabled = !needsNumber;
    if (needsNumber) number.focus();
    else if (select.value) addEvent(Number(step.dataset.step), select.value);
  });

  view.addEventListener("keydown", event => {
    if (event.key !== "Enter" || !event.target.matches("[data-custom-event] input")) return;
    event.preventDefault();
    event.target.nextElementSibling.click();
  });

  view.addEventListener("click", async event => {
    const button = event.target.closest("button");
    if (!button) return;
    const selected = rules.find(rule => rule.id === button.dataset.ruleId);
    if (selected) showEditor(selected);
    const row = button.closest("[data-step]");
    const index = Number(row?.dataset.step);
    switch (button.dataset.action) {
      case "new": showEditor(); break;
      case "cancel": closeEditor(); break;
      case "delete":
        if (window.confirm(`Delete the alert rule “${draft.name}”?`) && persist(draft.id)) {
          lastMatch.delete(draft.id);
          closeEditor();
        }
        break;
      case "add-step": draft.steps.push([]); renderSteps(); focusPicker(draft.steps.length - 1); break;
      case "remove-step": draft.steps.splice(index, 1); renderSteps(); focusPicker(Math.min(index, draft.steps.length - 1)); break;
      case "move-up":
      case "move-down": {
        const destination = index + (button.dataset.action === "move-up" ? -1 : 1);
        const [step] = draft.steps.splice(index, 1);
        draft.steps.splice(destination, 0, step);
        renderSteps();
        focusPicker(destination);
        break;
      }
      case "remove-event": draft.steps[index].splice(Number(button.dataset.choice), 1); renderSteps(); focusPicker(index); break;
      case "add-custom-event": {
        const input = row.querySelector("[data-custom-event] input");
        const type = `${row.querySelector("[data-event-picker]").value}-${input.valueAsNumber}`;
        if (alertEventLabel(type)) addEvent(index, type);
        else { setError("Enter a positive whole event number."); input.focus(); }
        break;
      }
      case "stop-sound": sound.stop(); break;
      case "test-sound": {
        if (!fields.seconds.reportValidity()) return;
        const seconds = fields.seconds.valueAsNumber;
        if (!(await enableSound()) || !sound.play(seconds)) setError("This browser could not play the alert sound.");
        else setError();
        break;
      }
      case "notifications":
        try { await window.Notification.requestPermission(); }
        catch { toast("Desktop notifications could not be enabled.", "error"); }
        renderDelivery();
        break;
    }
  });

  window.addEventListener("storage", event => {
    if (event.key !== STORAGE_KEY && event.key !== null) return;
    const next = readRules(window);
    for (const before of rules) {
      if (JSON.stringify(before) !== JSON.stringify(next.find(rule => rule.id === before.id))) monitor.resetRule(before.id);
    }
    rules = next;
    if (draft && editing && !rules.some(rule => rule.id === draft.id)) {
      closeEditor();
      if (visible) toast("This alert rule was deleted in another tab.", "info");
    } else if (visible) renderRules();
  });
  document.addEventListener("click", () => {
    if (rules.some(rule => rule.enabled && rule.sound)) void enableSound();
  }, { capture: true });

  return {
    open() {
      if (visible) return;
      visible = true;
      mountWorkspaceHeader(headerRoot, header);
      root.classList.add("alert-workspace-active");
      view.hidden = false;
      find("[data-monitor-status]").textContent = liveStatus;
      renderDelivery();
      renderRules();
    },
    close() {
      if (!visible) return;
      visible = false;
      root.classList.remove("alert-workspace-active");
      view.hidden = true;
      restoreWorkspaceHeader(view, header);
    },
    setLiveStatus(message) {
      if (liveStatus === message) return;
      liveStatus = message;
      if (visible) find("[data-monitor-status]").textContent = message;
    },
    baseline(through) {
      monitor.baseline(through);
      if (visible) renderRules();
    },
    advance(payload, through, symbol, options) {
      const matches = monitor.advance(rules, payload, through, options);
      for (const { rule, events } of matches) {
        const last = events.at(-1);
        const timestamp = formatTime(last.time);
        lastMatch.set(rule.id, timestamp);
        const details = `${symbol} · ${events.map(({ type, direction }) => alertEventLabel(`${direction}:${type}`) ?? alertEventLabel(type)).join(" → ")}`;
        if (window.Notification?.permission === "granted") {
          try { new window.Notification(`TradingBot · ${rule.name}`, { body: details, silent: true }); } catch {}
        }
      }
      if (matches.length) {
        toast(`${matches.map(({ rule }) => rule.name).join(", ")} · ${symbol}`, "alert");
        const duration = Math.max(0, ...matches.filter(({ rule }) => rule.sound).map(({ rule }) => rule.seconds));
        if (duration) sound.play(duration);
      }
      if (visible) renderRules();
    },
  };
}
