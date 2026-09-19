import "../styles/candle-export.css";
import { boundedLogEntries, summarizeUiError } from "../ui/log-window.js";
import { farazActivityNotice, farazExtractionOutcome, farazLoginWaitingDetail } from "../ui/feedback.js";
import { mountWorkspaceHeader, restoreWorkspaceHeader } from "../ui/workspace-state.js";
import { rawInventoryPresentation, sortRawInventory } from "./raw-inventory.js";
import { parseTehranMetadataTime } from "./raw-file-contract.js";
import { isQualifiedFarazSymbol, normalizeFarazSymbol } from "./faraz-symbol.js";
import { shortChartId } from "../ui/chart-identity.js";

const $id = (root, id) => root.querySelector(`#${id}`);
const CANDLE_EXPORT_STATE_KEY = "qg:candle-export:v1";
const DEFAULT_ACTION_HINT = "Completed RAW is saved locally.";
const VALIDATION_CHECKS = [
  ["chronology", "Timestamp order"],
  ["firstLast", "First and last candle"],
  ["range", "Requested range"],
  ["integrity", "Saved OHLC integrity"],
  ["timeframe", "Requested timeframe"],
];

async function request(url, options) {
  const response = await fetch(url, { cache: "no-store", ...options });
  const payload = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(payload.error || `Request failed with HTTP ${response.status}.`);
  return payload;
}

function timeframeLabel(seconds) {
  const value = Number(seconds) || 1;
  if (value % 86400 === 0) return `${value / 86400}D`;
  if (value % 3600 === 0) return `${value / 3600}H`;
  if (value % 60 === 0) return `${value / 60}M`;
  return `${value}S`;
}

function markup(icon) {
  return `<section id="candleExportView" class="candle-export-view hidden" aria-labelledby="candleExportTitle">
    <header class="candle-export-header">
      <div class="candle-export-heading"><span class="candle-export-logo">${icon("sendReceive", 20)}</span><div><h1 id="candleExportTitle">FARAZ Exporter</h1></div></div>
    </header>
    <div class="candle-export-scroll">
      <section class="candle-auth-card" aria-labelledby="candleAuthTitle">
        <div class="candle-section-title"><span>${icon("shield", 18)}</span><div><h2 id="candleAuthTitle">FARAZ session</h2></div></div>
        <div class="candle-auth-row">
          <span id="candleAuthBadge" class="candle-auth-badge" data-state="locked"><i></i><b>Authentication required</b></span>
          <span id="candleAuthDetail" class="candle-auth-detail">Sign in before configuring an export.</span>
          <button id="candleSignIn" class="candle-icon-button session primary" type="button" aria-label="Sign in to FARAZ" title="Sign in to FARAZ">${icon("login", 18)}</button>
          <button id="candleOpenFaraz" class="candle-icon-button external" type="button" aria-label="Open FARAZ in browser" title="Open FARAZ in browser">${icon("external", 18)}</button><button id="candleCheckSession" class="candle-icon-button refresh" type="button" aria-label="Refresh FARAZ session" title="Refresh FARAZ session">${icon("refresh", 18)}</button>
        </div>
      </section>

      <div id="candleLockedNotice" class="candle-locked-notice" role="status">${icon("lock", 18)}<span>Export settings are locked until a valid FARAZ session is detected.</span></div>
      <fieldset id="candleExportControls" class="candle-export-controls" disabled>
        <legend class="sr-only">Candle export settings</legend>
        <div class="candle-export-grid">
          <section class="candle-export-card" aria-labelledby="candleSourceTitle">
            <div class="candle-section-title"><span>${icon("candles", 18)}</span><div><h2 id="candleSourceTitle">Data source</h2></div></div>
            <div class="candle-form-grid">
              <label><span>Symbol</span><span class="candle-select-actions"><select id="candleExportSymbol" aria-label="Symbol"><option value="FOREXCOM:XAUUSD">FOREXCOM:XAUUSD</option><option value="FXCM:USOIL">FXCM:USOIL</option></select><button id="candleSymbolAdd" class="candle-icon-button add" type="button" aria-label="Add a symbol" title="Add a symbol">${icon("plus", 16)}</button><button id="candleSymbolRemove" class="candle-icon-button remove" type="button" aria-label="Remove selected symbol" title="Remove selected symbol">${icon("trash", 16)}</button></span></label>
              <label><span>Timeframe</span><select id="candleExportResolution">${[1, 3, 5, 10, 15, 30, 60, 180, 300, 600, 900, 1800, 2700, 3600, 14400, 86400].map((seconds) => `<option value="${timeframeLabel(seconds).toUpperCase()}"${seconds === 30 ? " selected" : ""}>${timeframeLabel(seconds)}</option>`).join("")}</select></label>
              <label><span>History host</span><select id="candleExportHost"><option value="faraz.io">faraz.io</option><option value="ir3.faraz.io">ir3.faraz.io</option><option value="ir4.faraz.io">ir4.faraz.io</option></select></label>
              <label><span>Packet size</span><input id="candleExportPacketSize" type="number" min="1" max="1000" value="1000"></label>
              <label><span>Rate limit</span><span class="candle-unit-input"><input id="candleExportRate" type="number" min="30" max="60000" value="30"><em>ms</em></span></label>
              <label><span>Total attempts</span><input id="candleExportRetryCount" type="number" value="4" readonly aria-readonly="true"></label>
            </div>
          </section>

          <section class="candle-export-card" aria-labelledby="candleRangeTitle">
            <div class="candle-section-title"><span>${icon("calendar", 18)}</span><div><h2 id="candleRangeTitle">Extraction range</h2></div></div>
            <div class="candle-mode-switch" role="group" aria-label="Extraction mode">
              <button id="candleModeCount" type="button" aria-pressed="false">Previous candles</button>
              <button id="candleModeRange" class="active" type="button" aria-pressed="true">Time range</button>
            </div>
            <div id="candleCountMode" class="candle-mode-panel hidden">
              <label class="candle-inline-field"><span>Number of candles</span><input id="candleExportCount" type="number" min="1" value="1000"></label>
              <div class="candle-toggle-row"><span><b>End at current time</b><output class="candle-current-time" data-current-time-output="count" aria-live="off">—</output></span><input id="candleCountToNow" type="checkbox" checked aria-label="End at current time"></div>
              <div id="candleCountToRow" class="candle-date-row hidden"><span>End</span><span class="candle-date-control"><button id="candleCountToButton" class="candle-date-button" type="button"><b id="candleCountToDisplay">Select date & time</b>${icon("calendar", 16)}</button><output id="candleCountToReadable" class="candle-readable-time">—</output></span><input id="candleCountTo" type="hidden"></div>
            </div>
            <div id="candleRangeMode" class="candle-mode-panel hidden">
              <div class="candle-date-row"><span>From</span><span class="candle-date-control"><button id="candleRangeFromButton" class="candle-date-button" type="button"><b id="candleRangeFromDisplay">Select date & time</b>${icon("calendar", 16)}</button><output id="candleRangeFromReadable" class="candle-readable-time">—</output></span><input id="candleRangeFrom" type="hidden"></div>
              <div class="candle-toggle-row"><span><b>End at current time</b><output class="candle-current-time" data-current-time-output="range" aria-live="off">—</output></span><input id="candleRangeToNow" type="checkbox" checked aria-label="End at current time"></div>
              <div id="candleRangeToRow" class="candle-date-row hidden"><span>To</span><span class="candle-date-control"><button id="candleRangeToButton" class="candle-date-button" type="button"><b id="candleRangeToDisplay">Select date & time</b>${icon("calendar", 16)}</button><output id="candleRangeToReadable" class="candle-readable-time">—</output></span><input id="candleRangeTo" type="hidden"></div>
            </div>
          </section>

          <aside class="candle-side-stack"><section class="candle-export-card candle-status-card" aria-labelledby="candleStatusTitle">
            <div class="candle-section-title"><span id="candleStatusIcon" class="candle-status-icon" data-state="idle">${icon("activity", 18)}</span><div><h2 id="candleStatusTitle">Extraction status</h2></div></div>
            <div class="candle-status-metrics">
              <div><span>Stage</span><b id="candleStatusStage">Locked</b></div>
              <div><span>Elapsed</span><b id="candleStatusElapsed">0s</b></div>
              <div><span>Packets</span><b id="candleStatusPackets">0 / 0</b></div>
              <div><span>Rows</span><b id="candleStatusRows">0</b></div>
              <div><span>Candles</span><b id="candleStatusCandles">0</b></div>
            </div>
            <div class="candle-progress-caption"><span id="candleProgressText">0 / 0 packets</span><b id="candleProgressPercent">0%</b></div>
            <div class="candle-progress-track" role="progressbar" aria-label="Candle extraction progress" aria-valuemin="0" aria-valuemax="100" aria-valuenow="0"><i id="candleProgressFill"></i></div>
          </section><section class="candle-export-card candle-info-card" aria-labelledby="candleInfoTitle"><div class="candle-section-title"><span>${icon("server", 18)}</span><div><h2 id="candleInfoTitle">Connection info</h2></div></div><dl class="candle-info-list"><div><dt>Endpoint</dt><dd id="candleInfoEndpoint">—</dd></div><div><dt>Site</dt><dd id="candleInfoSite">Unavailable</dd></div><div><dt>Ping</dt><dd id="candleInfoPing" data-state="unavailable"><i aria-hidden="true"></i><span>Unavailable</span></dd></div><div><dt>User ID</dt><dd id="candleInfoUser">—</dd></div><div><dt>User name</dt><dd id="candleInfoUserName">—</dd></div><div><dt>Phone</dt><dd id="candleInfoPhone">—</dd></div></dl></section><section class="candle-export-card candle-validation-card" aria-labelledby="candleValidationTitle"><div class="candle-section-title"><span>${icon("shield", 18)}</span><div><h2 id="candleValidationTitle">Saved file check</h2></div></div><div id="candleValidationList" class="candle-validation-list" aria-live="polite"></div></section></aside>
        </div>
        <section class="candle-export-card candle-log-card" aria-labelledby="candleLogTitle"><div class="candle-section-title"><span>${icon("history", 18)}</span><div><h2 id="candleLogTitle">Detailed log</h2></div><button id="candleCopyLog" class="candle-log-copy" type="button" title="Copy extraction report" aria-label="Copy extraction report">${icon("copy", 17)}</button></div><div id="candlePacketLog" class="candle-packet-log" aria-live="polite"><p>No packet activity yet.</p></div></section>
        <div class="candle-action-bar">
          <p id="candleActionHint">Completed RAW is saved locally.</p>
          <div><button id="candleReset" class="candle-button" type="button">${icon("restart", 17)}<span>Reset</span></button><button id="candleCancel" class="candle-button danger" type="button" disabled>${icon("close", 17)}<span>Cancel</span></button><button id="candleOpenFile" class="candle-button success hidden" type="button">${icon("folder", 17)}<span>Open file</span></button><button id="candleStart" class="candle-button primary" type="button">${icon("play", 17)}<span>Start extraction</span></button></div>
        </div>
      </fieldset>
      <section class="candle-raw-inventory" aria-labelledby="candleRawInventoryTitle">
        <div class="candle-section-title"><span>${icon("folder", 18)}</span><div><h2 id="candleRawInventoryTitle">Local RAW files</h2></div><button id="candleRawRefresh" class="candle-log-copy" type="button" aria-label="Refresh local RAW files" title="Refresh local RAW files">${icon("refresh", 17)}</button></div>
        <p id="candleRawInventoryStatus" class="candle-raw-status">Checking local storage…</p>
        <div class="candle-raw-table-wrap" tabindex="0"><table class="candle-raw-table"><thead><tr><th><button type="button" data-raw-sort-key="filename">File name</button></th><th><button type="button" data-raw-sort-key="symbol">Symbol</button></th><th><button type="button" data-raw-sort-key="broker">Broker</button></th><th><button type="button" data-raw-sort-key="timeframe">Timeframe</button></th><th>Chart ID</th><th><button type="button" data-raw-sort-key="from">From</button></th><th><button type="button" data-raw-sort-key="to">To</button></th><th><button type="button" data-raw-sort-key="createdAt">Created</button></th><th><button type="button" data-raw-sort-key="updatedAt">Updated</button></th><th><button type="button" data-raw-sort-key="count">Candles</button></th><th><button type="button" data-raw-sort-key="bytes">Size</button></th><th><span class="sr-only">Actions</span></th></tr></thead><tbody id="candleRawInventoryList" aria-live="polite"></tbody></table></div>
      </section>
    </div>
    <div id="candleCoverageDecision" class="candle-decision-backdrop hidden">
      <section class="candle-decision-dialog" role="dialog" aria-modal="true" aria-labelledby="candleCoverageDecisionTitle" aria-describedby="candleCoverageDecisionDetail">
        <header><span>${icon("warning", 20)}</span><div><h2 id="candleCoverageDecisionTitle">Source data is unavailable</h2><p>FARAZ could not supply every requested candle.</p></div></header>
        <p id="candleCoverageDecisionDetail"></p>
        <dl class="candle-decision-summary"><div><dt>Missing</dt><dd id="candleCoverageMissing">—</dd></div><div><dt>Continue from</dt><dd id="candleCoverageContinueFrom">—</dd></div></dl>
        <p class="candle-decision-note">No file has been saved. Continuing saves only candles starting at the first available source candle.</p>
        <footer><button id="candleCoverageCancel" class="candle-button danger" type="button">Cancel extraction</button><button id="candleCoverageContinue" class="candle-button primary" type="button">Continue from available candle</button></footer>
      </section>
    </div>
  </section>`;
}

export function initCandleExport({ root, headerRoot, icon, toast, getDefaults, inputFromTehran, parseTehranInput, setDateTimeValue, openDateTimePicker, onConnectionChange, onInventoryChanged }) {
  root.insertAdjacentHTML("beforeend", markup(icon));
  const view = $id(root, "candleExportView");
  const header = view.querySelector(".candle-export-header");
  const controls = $id(view, "candleExportControls");
  const lockedNotice = $id(view, "candleLockedNotice");
  const authBadge = $id(view, "candleAuthBadge");
  const authDetail = $id(view, "candleAuthDetail");
  const signIn = $id(view, "candleSignIn");
  const checkSession = $id(view, "candleCheckSession");
  const openFarazButton = $id(view, "candleOpenFaraz");
  let connected = false;
  const notifyActivity = (activity, detail) => {
    const notice = farazActivityNotice(activity, detail);
    if (notice) toast(notice.message, notice.type);
  };
  let mode = "count";
  let currentJobId = null;
  let visible = false;
  let defaultsSet = false;
  let jobTimer = null;
  let hostInitialized = false;
  let followLogTail = true;
  let lastRenderedJob = null;
  let coverageDecisionLastFocus = null;
  let rawInventorySort = { key: "updatedAt", direction: "desc" };

  function inventoryTime(value) {
    const numeric = Number(value);
    return Number.isFinite(numeric) ? inputFromTehran(numeric).replace("T", " ") : "—";
  }

  function metadataTime(value) {
    const tehranSeconds = parseTehranMetadataTime(value);
    if (Number.isFinite(tehranSeconds)) return inventoryTime(tehranSeconds);
    const parsed = typeof value === "number" ? value : Date.parse(value);
    if (!Number.isFinite(parsed)) return "—";
    return inventoryTime((parsed < 100000000000 ? parsed * 1000 : parsed) / 1000);
  }

  function bytesLabel(value) {
    const bytes = Number(value) || 0;
    return bytes >= 1048576 ? `${(bytes / 1048576).toFixed(2)} MB` : `${Math.ceil(bytes / 1024)} KB`;
  }

  function renderRawSortHeaders() {
    view.querySelectorAll("[data-raw-sort-key]").forEach((button) => {
      const active = button.dataset.rawSortKey === rawInventorySort.key;
      button.setAttribute("aria-sort", active ? (rawInventorySort.direction === "asc" ? "ascending" : "descending") : "none");
      const labels = { filename: "File name", symbol: "Symbol", broker: "Broker", timeframe: "Timeframe", from: "From", to: "To", createdAt: "Created", updatedAt: "Updated", count: "Candles", bytes: "Size" };
      button.textContent = `${labels[button.dataset.rawSortKey] || button.dataset.rawSortKey}${active ? (rawInventorySort.direction === "asc" ? " ↑" : " ↓") : ""}`;
    });
  }

  function renderRawInventory(items) {
    const list = $id(view, "candleRawInventoryList");
    const status = $id(view, "candleRawInventoryStatus");
    list.replaceChildren();
    renderRawSortHeaders();
    if (!items.length) {
      status.textContent = "No local RAW files.";
      return;
    }
    status.textContent = `${items.length.toLocaleString("en-US")} local RAW file${items.length === 1 ? "" : "s"}`;
    for (const item of sortRawInventory(items, rawInventorySort)) {
      const row = rawInventoryPresentation(item, inventoryTime);
      const element = document.createElement("tr");
      const cells = [row.filename, row.symbol, String(item.broker || "UNKNOWN"), String(item.timeframe || "—"), shortChartId(row.chartId), inventoryTime(item.from), inventoryTime(item.to), metadataTime(item.createdAt), metadataTime(item.updatedAt || item.savedAt), Number(item.count || 0).toLocaleString("en-US"), bytesLabel(item.bytes)];
      for (const [index, value] of cells.entries()) {
        const cell = document.createElement("td");
        cell.textContent = value;
        if (index === 4) cell.title = row.chartId;
        element.append(cell);
      }
      const remove = document.createElement("button");
      remove.className = "candle-icon-button candle-raw-delete remove";
      remove.type = "button";
      remove.title = `Permanently delete ${row.filename}`;
      remove.setAttribute("aria-label", remove.title);
      remove.innerHTML = icon("trash", 14);
      remove.onclick = async () => {
        if (!window.confirm(`Permanently delete this RAW file?\n\n${row.filename}\n\nThis cannot be undone.`)) return;
        remove.disabled = true;
        try {
          await request("/api/candle-files/delete", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ id: row.id }) });
          toast("RAW file deleted", "success");
          await refreshRawInventory();
          onInventoryChanged?.();
        } catch (error) {
          toast(error.message, "error");
        } finally {
          remove.disabled = false;
        }
      };
      const actions = document.createElement("td");
      actions.append(remove);
      element.append(actions);
      list.append(element);
    }
  }

  async function refreshRawInventory() {
    const status = $id(view, "candleRawInventoryStatus");
    try {
      const items = await request("/api/symbols");
      renderRawInventory(Array.isArray(items) ? items : []);
    } catch (error) {
      status.textContent = `Local RAW inventory is unavailable: ${summarizeUiError(error.message)}`;
    }
  }

  function syncRawInventory(items) {
    if (visible) renderRawInventory(Array.isArray(items) ? items : []);
  }

  function persistedState() {
    return {
      mode,
      currentJobId,
      symbols: [...$id(view, "candleExportSymbol").options].map((option) => option.value),
      symbol: $id(view, "candleExportSymbol").value,
      resolution: $id(view, "candleExportResolution").value,
      host: $id(view, "candleExportHost").value,
      packetSize: $id(view, "candleExportPacketSize").value,
      rateLimitMs: $id(view, "candleExportRate").value,
      retryCount: $id(view, "candleExportRetryCount").value,
      candleCount: $id(view, "candleExportCount").value,
      countToNow: $id(view, "candleCountToNow").checked,
      countTo: $id(view, "candleCountTo").value,
      rangeFrom: $id(view, "candleRangeFrom").value,
      rangeToNow: $id(view, "candleRangeToNow").checked,
      rangeTo: $id(view, "candleRangeTo").value,
    };
  }

  function persistState() {
    try { localStorage.setItem(CANDLE_EXPORT_STATE_KEY, JSON.stringify(persistedState())); }
    catch {}
  }

  function restoreState() {
    let saved;
    try { saved = JSON.parse(localStorage.getItem(CANDLE_EXPORT_STATE_KEY) || "null"); }
    catch { return; }
    if (!saved || typeof saved !== "object") return;
    if (Array.isArray(saved.symbols)) {
      const select = $id(view, "candleExportSymbol");
      select.replaceChildren(...saved.symbols.filter(isQualifiedFarazSymbol).map((value) => {
        const symbol = String(value).trim().toUpperCase();
        return new Option(symbol, symbol);
      }));
      for (const symbol of ["FOREXCOM:XAUUSD", "FXCM:USOIL"])
        if (![...select.options].some((option) => option.value === symbol)) select.add(new Option(symbol, symbol), 0);
    }
    const values = {
      candleExportSymbol: isQualifiedFarazSymbol(saved.symbol) ? String(saved.symbol).trim().toUpperCase() : undefined,
      candleExportResolution: saved.resolution,
      candleExportHost: saved.host,
      candleExportPacketSize: saved.packetSize,
      candleExportRate: saved.rateLimitMs,
      candleExportRetryCount: saved.retryCount,
      candleExportCount: saved.candleCount,
    };
    for (const [id, value] of Object.entries(values)) {
      if (value !== undefined && value !== null && $id(view, id)) $id(view, id).value = String(value);
    }
    for (const [id, value] of [["candleCountTo", saved.countTo], ["candleRangeFrom", saved.rangeFrom], ["candleRangeTo", saved.rangeTo]]) {
      if (typeof value === "string" && value) setDateTimeValue(`#${id}`, value);
    }
    if (typeof saved.countToNow === "boolean") $id(view, "candleCountToNow").checked = saved.countToNow;
    if (typeof saved.rangeToNow === "boolean") $id(view, "candleRangeToNow").checked = saved.rangeToNow;
    currentJobId = typeof saved.currentJobId === "string" ? saved.currentJobId : null;
    // A saved host is only a previous preference.  The current FARAZ history
    // request remains authoritative when this dev-server session reconnects.
    hostInitialized = false;
    defaultsSet = Boolean(isQualifiedFarazSymbol(saved.symbol) && saved.resolution);
    setMode(saved.mode === "count" ? "count" : "range", false);
    $id(view, "candleCountToRow").classList.toggle("hidden", $id(view, "candleCountToNow").checked);
    $id(view, "candleRangeToRow").classList.toggle("hidden", $id(view, "candleRangeToNow").checked);
  }

  const nowValue = () => inputFromTehran(Date.now() / 1000);
  function farazSymbol(value) {
    const defaultSymbol = String(getDefaults().symbol || "").trim();
    return normalizeFarazSymbol(value, defaultSymbol) || "FXCM:USOIL";
  }
  const applyDefaults = () => {
    const defaults = getDefaults();
    if (!defaultsSet) {
      const symbol = String(defaults.symbol || "").trim();
      const symbols = $id(view, "candleExportSymbol");
      if (symbol) {
        if (![...symbols.options].some((option) => option.value === symbol)) symbols.add(new Option(symbol, symbol));
        symbols.value = symbol;
      }
      const resolution = timeframeLabel(defaults.timeframeSeconds).toUpperCase();
      if ([...$id(view, "candleExportResolution").options].some((option) => option.value === resolution)) $id(view, "candleExportResolution").value = resolution;
      defaultsSet = true;
    }
    const now = nowValue();
    if (!$id(view, "candleCountTo").value) setDateTimeValue("#candleCountTo", now);
    if (!$id(view, "candleRangeTo").value) setDateTimeValue("#candleRangeTo", now);
    if (!$id(view, "candleRangeFrom").value) setDateTimeValue("#candleRangeFrom", inputFromTehran(Date.now() / 1000 - 3600));
  };

  function setConnected(status) {
    connected = Boolean(status.connected);
    controls.disabled = !connected;
    lockedNotice.classList.toggle("hidden", connected);
    authBadge.dataset.state = connected ? "connected" : "locked";
    authBadge.querySelector("b").textContent = connected ? "Session connected" : "Authentication required";
    authDetail.textContent = connected
      ? `${status.host || "faraz.io"} · Session verified from the local secret file`
      : status.error ? summarizeUiError(status.error)
        : status.state === "expired_session" ? "Saved session was rejected by FARAZ. Edit the secret file or sign in again."
          : "Sign in before configuring an export.";
    signIn.classList.toggle("danger", connected);
    signIn.classList.toggle("primary", !connected);
    signIn.setAttribute("aria-label", connected ? "Sign out of FARAZ" : "Sign in to FARAZ");
    signIn.title = connected ? "Sign out of FARAZ" : "Sign in to FARAZ";
    signIn.innerHTML = icon(connected ? "logout" : "login", 18);
    $id(view, "candleStatusStage").textContent = connected ? "Ready" : "Locked";
    $id(view, "candleInfoSite").textContent = connected ? `${status.host || "faraz.io"} active` : "Unavailable";
    const ping = $id(view, "candleInfoPing");
    const pingAvailable = connected && Number.isFinite(Number(status.pingMs));
    ping.dataset.state = pingAvailable ? "active" : "unavailable";
    ping.querySelector("span").textContent = pingAvailable ? `${Math.round(status.pingMs)} ms` : "Unavailable";
    $id(view, "candleInfoUser").textContent = status.userId || "—";
    $id(view, "candleInfoUserName").textContent = status.userName || "—";
    $id(view, "candleInfoPhone").textContent = status.phone || "—";
    if (status.endpoint) $id(view, "candleInfoEndpoint").textContent = status.endpoint;
    if (connected && status.historyHost && !hostInitialized) {
      $id(view, "candleExportHost").value = status.historyHost;
      hostInitialized = true;
      persistState();
    }
    onConnectionChange?.(connected, status);
    if (connected) applyDefaults();
  }

  function setExtractionState(state) {
    $id(view, "candleStatusIcon").dataset.state = state;
  }

  function clearExtractionStatus() {
    setExtractionState("idle");
    $id(view, "candleActionHint").textContent = DEFAULT_ACTION_HINT;
    renderJob({ stage: connected ? "Waiting" : "Locked", totalPackets: 0, receivedPackets: 0, receivedRows: 0, candleCountResult: 0, logs: [] });
  }

  async function refreshAuth() {
    try {
      const symbol = encodeURIComponent(farazSymbol($id(view, "candleExportSymbol").value || getDefaults().symbol || "FXCM:USOIL"));
      const status = await request(`/api/faraz/auth/status?symbolName=${symbol}`);
      setConnected(status);
      return status;
    } catch (error) {
      const status = { connected: false, error: error.message };
      setConnected(status);
      return status;
    }
  }

  function setActionBusy(button, busy) {
    button.disabled = busy;
    button.classList.toggle("is-loading", busy);
    button.setAttribute("aria-busy", String(busy));
  }

  async function openLogin() {
    if (connected) return signOut();
    toast("Opening FARAZ sign-in", "info");
    setActionBusy(signIn, true);
    authDetail.textContent = "Opening the dedicated FARAZ sign-in browser…";
    try {
      await request("/api/faraz/auth/open", { method: "POST" });
      authDetail.textContent = "Complete sign-in in the FARAZ browser. After the local session is saved, that browser closes automatically.";
      const status = await refreshAuth();
      authDetail.textContent = farazLoginWaitingDetail(status) || authDetail.textContent;
    } catch (error) {
      toast(error.message, "error");
      authDetail.textContent = error.message;
    } finally {
      setActionBusy(signIn, false);
    }
  }

  async function openFaraz() {
    setActionBusy(openFarazButton, true);
    try {
      await request("/api/faraz/auth/browser", { method: "POST" });
      toast("FARAZ opened in your browser", "success");
    } catch (error) {
      toast(error.message, "error");
    } finally {
      setActionBusy(openFarazButton, false);
    }
  }

  async function signOut() {
    if (!window.confirm("Remove the local FARAZ session from this workstation? This does not sign you out of the FARAZ website.")) return;
    setActionBusy(signIn, true);
    try {
      await request("/api/faraz/auth/logout", { method: "POST" });
      setConnected({ connected: false, state: "not_connected" });
      toast("Local FARAZ session removed", "success");
    } catch (error) {
      toast(error.message, "error");
    } finally {
      setActionBusy(signIn, false);
    }
  }

  function setMode(next, shouldPersist = true) {
    mode = next;
    for (const [buttonId, panelId, value] of [["candleModeCount", "candleCountMode", "count"], ["candleModeRange", "candleRangeMode", "range"]]) {
      const active = next === value;
      $id(view, buttonId).classList.toggle("active", active);
      $id(view, buttonId).setAttribute("aria-pressed", String(active));
      $id(view, panelId).classList.toggle("hidden", !active);
    }
    if (shouldPersist) persistState();
  }

  function epoch(value, label) {
    const parsed = parseTehranInput(value);
    if (!Number.isFinite(parsed)) throw new Error(`Select a valid ${label} in Asia/Tehran.`);
    return parsed;
  }

  function params() {
    const toNow = mode === "count" ? $id(view, "candleCountToNow").checked : $id(view, "candleRangeToNow").checked;
    const to = toNow ? Math.floor(Date.now() / 1000) : epoch($id(view, mode === "count" ? "candleCountTo" : "candleRangeTo").value, "end date and time");
    const common = {
      mode, to, symbolName: farazSymbol($id(view, "candleExportSymbol").value.trim()), resolution: $id(view, "candleExportResolution").value.trim(),
      host: $id(view, "candleExportHost").value,
      packetSize: Number($id(view, "candleExportPacketSize").value), rateLimitMs: Number($id(view, "candleExportRate").value), retryCount: 4,
    };
    if (!common.symbolName) throw new Error("Symbol is required.");
    if (mode === "count") return { ...common, candleCount: Number($id(view, "candleExportCount").value) };
    const from = epoch($id(view, "candleRangeFrom").value, "start date and time");
    if (from >= to) throw new Error("From must be earlier than To.");
    return { ...common, from };
  }

  function renderLogs(logs = []) {
    const box = $id(view, "candlePacketLog");
    box.replaceChildren();
    if (!logs.length) {
      const empty = document.createElement("p");
      empty.textContent = "No packet activity yet.";
      box.append(empty);
      followLogTail = true;
      return;
    }
    const { entries, omitted } = boundedLogEntries(logs);
    if (omitted) {
      const summary = document.createElement("p");
      summary.dataset.level = "summary";
      summary.textContent = `${omitted.toLocaleString()} older events are retained in the extraction report.`;
      box.append(summary);
    }
    for (const entry of entries) {
      const row = document.createElement("p");
      row.dataset.level = entry.level || "info";
      const time = new Date(entry.time).toLocaleString("en-GB", { timeZone: "Asia/Tehran", hour12: false, year: "numeric", month: "2-digit", day: "2-digit", hour: "2-digit", minute: "2-digit", second: "2-digit" });
      row.textContent = `[${time} UTC+3.5 Tehran] ${entry.message || ""}`;
      box.append(row);
    }
    // Start at the latest activity, but never steal the reader's place after
    // they deliberately scroll upward.
    if (followLogTail) box.scrollTop = box.scrollHeight;
  }

  function buildLogSummary(job) {
    const logs = Array.isArray(job?.logs) ? job.logs : [];
    const count = (level) => logs.filter((entry) => entry.level === level).length;
    const unique = (level) => [...new Set(logs.filter((entry) => entry.level === level).map((entry) => entry.message).filter(Boolean))];
    const errorMessages = unique("error");
    const retryMessages = unique("retry");
    const gaps = Array.isArray(job?.suspiciousGaps) ? job.suspiciousGaps : [];
    const recovered = gaps.filter((gap) => gap.status === "recovered");
    const unresolved = gaps.filter((gap) => gap.status === "source_gap");
    const lines = [
      "FARAZ extraction report",
      `Generated: ${new Date().toLocaleString("en-GB", { timeZone: "Asia/Tehran", hour12: false })} UTC+3.5 Tehran`,
      `Status: ${job?.done ? (job?.continuedFromAvailable ? "completed from first available source candle" : (job.coverageComplete === false ? "completed with unresolved source gaps" : "completed")) : (job?.awaitingCoverageDecision ? "waiting for source-data decision" : (job?.error ? "failed" : (job?.running ? "running" : "idle")))}`,
      `Stage: ${job?.stage || "—"}`,
      `Symbol / resolution: ${job?.symbolName || "—"} / ${job?.resolution || "—"}`,
      `Requested range: ${readableJobTime(job?.requestedFrom)} → ${readableJobTime(job?.requestedTo)}`,
      `Packets: ${job?.receivedPackets || 0}/${job?.totalPackets || 0}; valid rows: ${Number(job?.receivedRows || 0).toLocaleString("en-US")}; saved candles: ${Number(job?.candleCountResult || 0).toLocaleString("en-US")}`,
      `Log events: ${logs.length}; errors: ${count("error")}; HTTP retry events: ${count("retry")}; warnings: ${count("warn")}.`,
    ];
    if (job?.rangeAdjusted) lines.push(`Original manual range: ${readableJobTime(job.originalRequestedFrom)} → ${readableJobTime(job.originalRequestedTo)}; adjusted inward to complete ${job.resolution || "timeframe"} candles.`);
    if (job?.outsideRangeRows) lines.push(`Excluded countback rows outside request bounds: ${job.outsideRangeRows} across ${job.outsideRangePackets} packet(s).`);
    if (errorMessages.length) lines.push("", "Errors:", ...errorMessages.map((message, index) => `${index + 1}. ${message}`));
    if (retryMessages.length) lines.push("", "HTTP retries:", ...retryMessages.map((message, index) => `${index + 1}. ${message}`));
    if (recovered.length) lines.push("", `Coverage replays recovered ${recovered.reduce((sum, gap) => sum + Number(gap.recoveredCandles || 0), 0)} candle(s) across ${recovered.length} interval(s).`);
    if (unresolved.length) {
      lines.push("", `Unresolved source gaps after precise replays: ${unresolved.length} interval(s), ${unresolved.reduce((sum, gap) => sum + Number(gap.remainingCandles || 0), 0)} missing candle(s). The export is marked incomplete.`);
      lines.push(...unresolved.slice(0, 24).map((gap) => `- ${readableJobTime(gap.from)} → ${readableJobTime(gap.to)}: ${gap.remainingCandles} candle(s) remain after ${gap.attempts} replay(s).`));
      if (unresolved.length > 24) lines.push(`- ${unresolved.length - 24} additional unresolved interval(s) are included in the count above.`);
    }
    if (job?.error && !errorMessages.includes(job.error)) lines.push("", `Failure detail: ${job.error}`);
    return lines.join("\n");
  }

  async function copyLogSummary() {
    const report = buildLogSummary(lastRenderedJob);
    try {
      if (navigator.clipboard?.writeText) await navigator.clipboard.writeText(report);
      else {
        const input = document.createElement("textarea");
        input.value = report;
        input.setAttribute("readonly", "");
        input.className = "sr-only";
        document.body.append(input);
        input.select();
        if (!document.execCommand("copy")) throw new Error("Clipboard copy was rejected.");
        input.remove();
      }
      toast("Extraction report copied", "success");
    } catch (error) {
      toast(`Unable to copy extraction report: ${error.message}`, "error");
    }
  }

  function renderValidation(checks = []) {
    const list = $id(view, "candleValidationList");
    list.replaceChildren();
    const received = new Map(checks.map((check) => [check.key, check]));
    for (const [key, label] of VALIDATION_CHECKS) {
      const check = received.get(key);
      const item = document.createElement("div");
      const passed = Boolean(check?.passed);
      item.className = "candle-validation-item";
      item.dataset.state = check ? (passed ? "pass" : "fail") : "pending";
      const stateIcon = check ? (passed ? "check" : "cross") : "activity";
      const detail = check?.detail || "Awaiting saved-file validation.";
      item.innerHTML = `${icon(stateIcon, 17)}<span><b>${check?.label || label}</b><small>${detail}</small></span>`;
      list.append(item);
    }
  }

  function elapsedLabel(job) {
    const started = Number(job.createdAt);
    if (!Number.isFinite(started)) return "0s";
    const finished = Number(job.completedAt || job.failedAt);
    const elapsedSeconds = Math.max(0, Math.floor(((Number.isFinite(finished) ? finished : Date.now()) - started) / 1000));
    const hours = Math.floor(elapsedSeconds / 3600);
    const minutes = Math.floor((elapsedSeconds % 3600) / 60);
    const seconds = elapsedSeconds % 60;
    if (hours) return `${hours}h ${minutes}m ${seconds}s`;
    if (minutes) return `${minutes}m ${seconds}s`;
    return `${seconds}s`;
  }

  function renderJob(job) {
    lastRenderedJob = job;
    const total = Number(job.totalPackets || 0);
    const received = Number(job.receivedPackets || 0);
    const percent = total ? Math.min(100, Math.round(received / total * 100)) : 0;
    $id(view, "candleStatusStage").textContent = job.stage || "—";
    $id(view, "candleStatusElapsed").textContent = elapsedLabel(job);
    $id(view, "candleStatusPackets").textContent = `${received} / ${total}`;
    $id(view, "candleStatusRows").textContent = Number(job.receivedRows || 0).toLocaleString("en-US");
    $id(view, "candleStatusCandles").textContent = Number(job.candleCountResult || 0).toLocaleString("en-US");
    $id(view, "candleProgressText").textContent = `${received} / ${total} packets`;
    $id(view, "candleProgressPercent").textContent = `${percent}%`;
    $id(view, "candleProgressFill").style.width = `${percent}%`;
    $id(view, "candleProgressFill").parentElement.setAttribute("aria-valuenow", String(percent));
    const outcome = farazExtractionOutcome(job);
    setExtractionState(job.awaitingCoverageDecision || job.done ? outcome.state : (job.cancelRequested || (!job.running && job.error) ? "error" : "idle"));
    $id(view, "candleStart").disabled = Boolean(job.running);
    $id(view, "candleCancel").disabled = !job.running;
    const openFile = $id(view, "candleOpenFile");
    openFile.classList.toggle("hidden", !job.openUrl);
    openFile.dataset.url = job.openUrl || "";
    if (job.savedPath) $id(view, "candleActionHint").textContent = `Saved automatically to ${job.savedPath}`;
    else if (job.rangeAdjusted) $id(view, "candleActionHint").textContent = `Range adjusted inward to complete ${job.resolution || "timeframe"} candles: ${readableJobTime(job.requestedFrom)} → ${readableJobTime(job.requestedTo)}.`;
    if (job.endpoint) $id(view, "candleInfoEndpoint").textContent = job.endpoint;
    renderLogs(job.logs);
    renderValidation(job.validation);
  }

  function formatCoverageDecisionTime(time) {
    const value = Number(time);
    return Number.isFinite(value) ? `${inputFromTehran(value).replace("T", " ")} Asia/Tehran` : "—";
  }

  function showCoverageDecision(job) {
    const dialog = $id(view, "candleCoverageDecision");
    const gaps = Array.isArray(job.suspiciousGaps) ? job.suspiciousGaps.filter((gap) => gap.status === "source_gap") : [];
    const missingCandles = gaps.reduce((total, gap) => total + Number(gap.remainingCandles || 0), 0);
    $id(view, "candleCoverageDecisionDetail").textContent = `Automatic recovery did not find ${missingCandles.toLocaleString("en-US")} requested candle(s) across ${gaps.length} interval(s).`;
    $id(view, "candleCoverageMissing").textContent = `${missingCandles.toLocaleString("en-US")} candle(s) in ${gaps.length} interval(s)`;
    $id(view, "candleCoverageContinueFrom").textContent = formatCoverageDecisionTime(job.continueFrom);
    if (dialog.classList.contains("hidden")) {
      coverageDecisionLastFocus = document.activeElement;
      dialog.classList.remove("hidden");
      requestAnimationFrame(() => $id(view, "candleCoverageContinue").focus());
    }
  }

  function hideCoverageDecision() {
    const dialog = $id(view, "candleCoverageDecision");
    if (dialog.classList.contains("hidden")) return;
    dialog.classList.add("hidden");
    coverageDecisionLastFocus?.focus?.();
    coverageDecisionLastFocus = null;
  }

  async function resolveCoverageDecision(decision) {
    if (!currentJobId) return;
    const cancelButton = $id(view, "candleCoverageCancel");
    const continueButton = $id(view, "candleCoverageContinue");
    cancelButton.disabled = true;
    continueButton.disabled = true;
    try {
      const job = await request("/api/faraz/candles/coverage-decision", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ id: currentJobId, decision }),
      });
      renderJob(job);
      currentJobId = null;
      persistState();
      hideCoverageDecision();
      if (job.done) {
        await refreshRawInventory();
        onInventoryChanged?.();
        const outcome = farazExtractionOutcome(job);
        toast(outcome.message, outcome.type);
      } else {
        toast("Extraction cancelled. No file was saved.", "info");
      }
    } catch (error) {
      toast(error.message, "error");
    } finally {
      cancelButton.disabled = false;
      continueButton.disabled = false;
    }
  }

  async function pollJob() {
    if (!currentJobId) return;
    try {
      const job = await request(`/api/faraz/candles/status?id=${encodeURIComponent(currentJobId)}`);
      renderJob(job);
      if (job.awaitingCoverageDecision) {
        clearInterval(jobTimer);
        jobTimer = null;
        showCoverageDecision(job);
        return;
      }
      if (!job.running) {
        clearInterval(jobTimer);
        jobTimer = null;
        currentJobId = null;
        persistState();
        if (job.done) {
          await refreshRawInventory();
          onInventoryChanged?.();
        }
        const outcome = farazExtractionOutcome(job);
        toast(job.done ? outcome.message : job.error || outcome.message, job.done ? outcome.type : "error");
      }
    } catch (error) {
      clearInterval(jobTimer);
      jobTimer = null;
      if (/Extraction was not found/i.test(error.message)) {
        currentJobId = null;
        persistState();
        clearExtractionStatus();
        return;
      }
      setExtractionState("error");
      toast(error.message, "error");
    }
  }

  async function start() {
    if (!connected) return toast("Sign in to FARAZ first", "error");
    try {
      currentJobId = null;
      hideCoverageDecision();
      clearExtractionStatus();
      const job = await request("/api/faraz/candles/start", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(params()) });
      currentJobId = job.id;
      persistState();
      renderJob(job);
      notifyActivity("start");
      clearInterval(jobTimer);
      jobTimer = setInterval(pollJob, 800);
      await pollJob();
    } catch (error) {
      toast(error.message, "error");
    }
  }

  async function cancel() {
    if (!currentJobId) return;
    await request("/api/faraz/candles/cancel", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ id: currentJobId }) }).then(() => {
      setExtractionState("error");
      notifyActivity("cancel");
    }).catch((error) => { setExtractionState("error"); toast(error.message, "error"); });
  }

  function reset() {
    currentJobId = null;
    clearInterval(jobTimer);
    jobTimer = null;
    hideCoverageDecision();
    defaultsSet = false;
    $id(view, "candleExportPacketSize").value = "1000";
    $id(view, "candleExportRate").value = "30";
    $id(view, "candleExportRetryCount").value = "4";
    $id(view, "candleExportCount").value = "1000";
    $id(view, "candleCountToNow").checked = true;
    $id(view, "candleRangeToNow").checked = true;
    setMode("range");
    renderJob({ stage: connected ? "Ready" : "Locked", status: connected ? "Ready after authentication." : "Authentication required.", logs: [], validation: [] });
    applyDefaults();
    persistState();
    notifyActivity("reset");
  }

  restoreState();
  renderValidation();
  $id(view, "candlePacketLog").addEventListener("scroll", (event) => {
    const box = event.currentTarget;
    followLogTail = box.scrollTop + box.clientHeight >= box.scrollHeight - 8;
  });
  $id(view, "candleCopyLog").onclick = copyLogSummary;
  $id(view, "candleRawRefresh").onclick = refreshRawInventory;
  view.querySelectorAll("[data-raw-sort-key]").forEach((button) => {
    button.onclick = () => {
      const key = button.dataset.rawSortKey;
      rawInventorySort = { key, direction: rawInventorySort.key === key && rawInventorySort.direction === "asc" ? "desc" : "asc" };
      refreshRawInventory();
    };
  });
  signIn.onclick = openLogin;
  checkSession.onclick = async () => {
    setActionBusy(checkSession, true);
    try {
      await refreshAuth();
      toast(connected ? "FARAZ session refreshed" : "FARAZ session is not connected", connected ? "success" : "error");
    } finally {
      setActionBusy(checkSession, false);
    }
  };
  openFarazButton.onclick = openFaraz;
  $id(view, "candleModeCount").onclick = () => setMode("count");
  $id(view, "candleModeRange").onclick = () => setMode("range");
  $id(view, "candleCountToNow").onchange = (event) => { $id(view, "candleCountToRow").classList.toggle("hidden", event.target.checked); renderReadableTimes(); };
  $id(view, "candleRangeToNow").onchange = (event) => { $id(view, "candleRangeToRow").classList.toggle("hidden", event.target.checked); renderReadableTimes(); };
  $id(view, "candleCountToButton").onclick = () => openDateTimePicker("#candleCountTo");
  $id(view, "candleRangeFromButton").onclick = () => openDateTimePicker("#candleRangeFrom");
  $id(view, "candleRangeToButton").onclick = () => openDateTimePicker("#candleRangeTo");
  $id(view, "candleStart").onclick = start;
  $id(view, "candleCancel").onclick = cancel;
  $id(view, "candleReset").onclick = reset;
  $id(view, "candleCoverageCancel").onclick = () => resolveCoverageDecision("cancel");
  $id(view, "candleCoverageContinue").onclick = () => resolveCoverageDecision("continue_from_available");
  $id(view, "candleCoverageDecision").addEventListener("keydown", (event) => {
    if (event.key !== "Tab") return;
    const controls = [$id(view, "candleCoverageCancel"), $id(view, "candleCoverageContinue")];
    const index = controls.indexOf(document.activeElement);
    if (event.shiftKey && index <= 0) {
      event.preventDefault();
      controls.at(-1).focus();
    } else if (!event.shiftKey && index === controls.length - 1) {
      event.preventDefault();
      controls[0].focus();
    }
  });
  $id(view, "candleOpenFile").onclick = async (event) => {
    const url = event.currentTarget.dataset.url;
    if (!url) return;
    try { await request(url, { method: "POST" }); toast("Saved RAW file opened", "success"); }
    catch (error) { toast(error.message, "error"); }
  };
  $id(view, "candleSymbolAdd").onclick = () => {
    const next = window.prompt("Enter a FARAZ symbol, for example FXCM:USOIL");
    const symbol = String(next || "").trim().toUpperCase();
    if (!symbol) return;
    const select = $id(view, "candleExportSymbol");
    if (![...select.options].some((option) => option.value === symbol)) select.add(new Option(symbol, symbol));
    select.value = symbol;
    persistState();
    notifyActivity("symbol-added", symbol);
  };
  $id(view, "candleSymbolRemove").onclick = () => {
    const select = $id(view, "candleExportSymbol");
    if (["FOREXCOM:XAUUSD", "FXCM:USOIL"].includes(select.value)) return toast("The two default symbols cannot be removed", "error");
    const removed = select.value;
    select.selectedOptions[0]?.remove();
    if (!select.options.length) toast("Add a symbol before starting extraction", "error");
    else notifyActivity("symbol-removed", removed);
    persistState();
  };
  $id(view, "candleExportHost").onchange = () => { hostInitialized = true; persistState(); };
  view.addEventListener("input", (event) => {
    if (event.target.closest("#candleExportControls")) persistState();
  });
  view.addEventListener("change", (event) => {
    if (event.target.closest("#candleExportControls")) persistState();
  });
  function readableJobTime(value) {
    const numeric = Number(value);
    return Number.isFinite(numeric) ? `${inputFromTehran(numeric).replace("T", " ")} Asia/Tehran` : "—";
  }

  function renderReadableTimes() {
    const now = Math.floor(Date.now() / 1000);
    for (const [inputId, outputId, toNow] of [["candleCountTo", "candleCountToReadable", $id(view, "candleCountToNow").checked], ["candleRangeFrom", "candleRangeFromReadable", false], ["candleRangeTo", "candleRangeToReadable", $id(view, "candleRangeToNow").checked]]) {
      const value = toNow ? now : parseTehranInput($id(view, inputId).value);
      $id(view, outputId).textContent = readableJobTime(value);
    }
    view.querySelector('[data-current-time-output="count"]').textContent = readableJobTime(now);
    view.querySelector('[data-current-time-output="range"]').textContent = readableJobTime(now);
  }
  setInterval(renderReadableTimes, 1000);
  void refreshRawInventory();
  void refreshAuth();
  // The footer remains visible outside the exporter. Keep it synchronized
  // with manual edits or deletion of the sole local session file.
  setInterval(refreshAuth, 5000);

  return {
    open() {
      visible = true;
      mountWorkspaceHeader(headerRoot, header);
      view.classList.remove("hidden");
      root.classList.add("candle-export-active");
      applyDefaults();
      renderReadableTimes();
      persistState();
      void refreshRawInventory();
      refreshAuth();
      if (currentJobId && !jobTimer) {
        pollJob().then(() => {
          if (currentJobId && !jobTimer && !$id(view, "candleCancel").disabled) jobTimer = setInterval(pollJob, 800);
        });
      }
      $id(view, "candleSignIn").focus();
    },
    close() {
      visible = false;
      view.classList.add("hidden");
      restoreWorkspaceHeader(view, header);
      root.classList.remove("candle-export-active");
      persistState();
    },
    refreshDefaults() { if (visible) { defaultsSet = false; applyDefaults(); } },
    syncRawInventory(items) { syncRawInventory(items); },
  };
}
