import "./styles/candle-export.css";

const $id = (root, id) => root.querySelector(`#${id}`);
const CANDLE_EXPORT_STATE_KEY = "qg:candle-export:v1";

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
      <div class="candle-export-heading"><span class="candle-export-logo">${icon("exportCandles", 20)}</span><div><h1 id="candleExportTitle">FARAZ Exporter</h1></div></div>
    </header>
    <div class="candle-export-scroll">
      <section class="candle-auth-card" aria-labelledby="candleAuthTitle">
        <div class="candle-section-title"><span>${icon("shield", 18)}</span><div><h2 id="candleAuthTitle">FARAZ session</h2></div></div>
        <div class="candle-auth-row">
          <span id="candleAuthBadge" class="candle-auth-badge" data-state="locked"><i></i><b>Authentication required</b></span>
          <span id="candleAuthDetail" class="candle-auth-detail">Sign in before configuring an export.</span>
          <button id="candleSignIn" class="candle-icon-button primary" type="button" aria-label="Sign in to FARAZ" title="Sign in to FARAZ">${icon("login", 18)}</button>
          <button id="candleOpenFaraz" class="candle-icon-button web" type="button" aria-label="Open FARAZ in browser" title="Open FARAZ in browser">${icon("web", 18)}</button><button id="candleCheckSession" class="candle-icon-button" type="button" aria-label="Refresh FARAZ session" title="Refresh FARAZ session">${icon("refresh", 18)}</button>
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
              <div class="candle-toggle-row"><span><b>End at current time</b></span><input id="candleCountToNow" type="checkbox" checked aria-label="End at current time"></div>
              <div id="candleCountToRow" class="candle-date-row hidden"><span>End</span><span class="candle-date-control"><button id="candleCountToButton" class="candle-date-button" type="button"><b id="candleCountToDisplay">Select date & time</b>${icon("calendar", 16)}</button><output id="candleCountToEpoch" class="candle-epoch">—</output></span><input id="candleCountTo" type="hidden"></div>
            </div>
            <div id="candleRangeMode" class="candle-mode-panel hidden">
              <div class="candle-date-row"><span>From</span><span class="candle-date-control"><button id="candleRangeFromButton" class="candle-date-button" type="button"><b id="candleRangeFromDisplay">Select date & time</b>${icon("calendar", 16)}</button><output id="candleRangeFromEpoch" class="candle-epoch">—</output></span><input id="candleRangeFrom" type="hidden"></div>
              <div class="candle-toggle-row"><span><b>End at current time</b></span><input id="candleRangeToNow" type="checkbox" checked aria-label="End at current time"></div>
              <div id="candleRangeToRow" class="candle-date-row hidden"><span>To</span><span class="candle-date-control"><button id="candleRangeToButton" class="candle-date-button" type="button"><b id="candleRangeToDisplay">Select date & time</b>${icon("calendar", 16)}</button><output id="candleRangeToEpoch" class="candle-epoch">—</output></span><input id="candleRangeTo" type="hidden"></div>
            </div>
          </section>

          <aside class="candle-side-stack"><section class="candle-export-card candle-status-card" aria-labelledby="candleStatusTitle">
            <div class="candle-section-title"><span id="candleStatusIcon" class="candle-status-icon" data-state="idle">${icon("activity", 18)}</span><div><h2 id="candleStatusTitle">Extraction status</h2></div></div>
            <div class="candle-status-metrics">
              <div><span>Stage</span><b id="candleStatusStage">Locked</b></div>
              <div><span>Packets</span><b id="candleStatusPackets">0 / 0</b></div>
              <div><span>Rows</span><b id="candleStatusRows">0</b></div>
              <div><span>Candles</span><b id="candleStatusCandles">0</b></div>
            </div>
            <div class="candle-progress-caption"><span id="candleProgressText">0 / 0 packets</span><b id="candleProgressPercent">0%</b></div>
            <div class="candle-progress-track" role="progressbar" aria-label="Candle extraction progress" aria-valuemin="0" aria-valuemax="100" aria-valuenow="0"><i id="candleProgressFill"></i></div>
          </section><section class="candle-export-card candle-info-card" aria-labelledby="candleInfoTitle"><div class="candle-section-title"><span>${icon("server", 18)}</span><div><h2 id="candleInfoTitle">Connection info</h2></div></div><dl class="candle-info-list"><div><dt>Endpoint</dt><dd id="candleInfoEndpoint">—</dd></div><div><dt>Site</dt><dd id="candleInfoSite">Unavailable</dd></div><div><dt>Ping</dt><dd id="candleInfoPing">—</dd></div><div><dt>User ID</dt><dd id="candleInfoUser">—</dd></div></dl></section><section class="candle-export-card candle-validation-card" aria-labelledby="candleValidationTitle"><div class="candle-section-title"><span>${icon("shield", 18)}</span><div><h2 id="candleValidationTitle">Saved file check</h2></div></div><div id="candleValidationList" class="candle-validation-list" aria-live="polite"><p class="candle-validation-empty">Awaiting a saved RAW file.</p></div></section></aside>
        </div>
        <section class="candle-export-card candle-log-card" aria-labelledby="candleLogTitle"><div class="candle-section-title"><span>${icon("history", 18)}</span><div><h2 id="candleLogTitle">Detailed log</h2></div></div><div id="candlePacketLog" class="candle-packet-log" aria-live="polite"><p>No packet activity yet.</p></div></section>
        <div class="candle-action-bar">
          <p id="candleActionHint">Completed JSON is saved automatically to market-data/raw with time, open, high, low, and close.</p>
          <div><button id="candleReset" class="candle-button" type="button">${icon("restart", 17)}<span>Reset</span></button><button id="candleCancel" class="candle-button danger" type="button" disabled>${icon("close", 17)}<span>Cancel</span></button><button id="candleOpenFile" class="candle-button success hidden" type="button">${icon("folder", 17)}<span>Open file</span></button><button id="candleStart" class="candle-button primary" type="button">${icon("play", 17)}<span>Start extraction</span></button></div>
        </div>
      </fieldset>
    </div>
  </section>`;
}

export function initCandleExport({ root, icon, toast, getDefaults, inputFromTehran, parseTehranInput, setDateTimeValue, openDateTimePicker, onConnectionChange }) {
  root.insertAdjacentHTML("beforeend", markup(icon));
  const view = $id(root, "candleExportView");
  const controls = $id(view, "candleExportControls");
  const lockedNotice = $id(view, "candleLockedNotice");
  const authBadge = $id(view, "candleAuthBadge");
  const authDetail = $id(view, "candleAuthDetail");
  const signIn = $id(view, "candleSignIn");
  const checkSession = $id(view, "candleCheckSession");
  let connected = false;
  let mode = "count";
  let currentJobId = null;
  let visible = false;
  let defaultsSet = false;
  let authTimer = null;
  let jobTimer = null;
  let hostInitialized = false;

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
      select.replaceChildren(...saved.symbols.filter((value) => typeof value === "string" && value.trim()).map((value) => new Option(value, value)));
      for (const symbol of ["FOREXCOM:XAUUSD", "FXCM:USOIL"])
        if (![...select.options].some((option) => option.value === symbol)) select.add(new Option(symbol, symbol), 0);
    }
    const values = {
      candleExportSymbol: saved.symbol,
      candleExportResolution: saved.resolution,
      candleExportHost: saved.host,
      candleExportPacketSize: saved.packetSize,
      candleExportRate: saved.rateLimitMs,
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
    defaultsSet = Boolean(saved.symbol || saved.resolution);
    setMode(saved.mode === "count" ? "count" : "range", false);
    $id(view, "candleCountToRow").classList.toggle("hidden", $id(view, "candleCountToNow").checked);
    $id(view, "candleRangeToRow").classList.toggle("hidden", $id(view, "candleRangeToNow").checked);
  }

  const nowValue = () => inputFromTehran(Date.now() / 1000);
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
      ? `${status.host || "faraz.io"} · Session available from the primary cache`
      : status.error || "Sign in before configuring an export.";
    signIn.classList.toggle("danger", connected);
    signIn.classList.toggle("primary", !connected);
    signIn.setAttribute("aria-label", connected ? "Sign out of FARAZ" : "Sign in to FARAZ");
    signIn.title = connected ? "Sign out of FARAZ" : "Sign in to FARAZ";
    signIn.innerHTML = icon(connected ? "logout" : "login", 18);
    $id(view, "candleStatusStage").textContent = connected ? "Ready" : "Locked";
    $id(view, "candleInfoSite").textContent = connected ? `${status.host || "faraz.io"} active` : "Unavailable";
    $id(view, "candleInfoPing").textContent = Number.isFinite(Number(status.pingMs)) ? `${Math.round(status.pingMs)} ms` : "—";
    $id(view, "candleInfoUser").textContent = status.userId || "Not exposed by FARAZ";
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
    renderJob({ stage: connected ? "Waiting" : "Locked", totalPackets: 0, receivedPackets: 0, receivedRows: 0, candleCountResult: 0, logs: [] });
  }

  async function refreshAuth() {
    try {
      const symbol = encodeURIComponent($id(view, "candleExportSymbol").value || getDefaults().symbol || "FXCM:USOIL");
      setConnected(await request(`/api/faraz/auth/status?symbolName=${symbol}`));
    } catch (error) {
      setConnected({ connected: false, error: error.message });
    }
  }

  async function openLogin() {
    if (connected) return signOut();
    toast("Opening FARAZ sign-in", "info");
    signIn.disabled = true;
    authDetail.textContent = "Opening FARAZ in your default system browser…";
    try {
      await request("/api/faraz/auth/open", { method: "POST" });
      authDetail.textContent = "Complete sign-in in the browser. The exporter will save the session without reopening the browser.";
      await refreshAuth();
    } catch (error) {
      toast(error.message, "error");
      authDetail.textContent = error.message;
    } finally {
      signIn.disabled = false;
    }
  }

  async function openFaraz() {
    toast("Opening FARAZ in your browser", "info");
    try { await request("/api/faraz/auth/browser", { method: "POST" }); }
    catch (error) { toast(error.message, "error"); }
  }

  async function signOut() {
    if (!window.confirm("Sign out of FARAZ? The session file in primary-cache/secret will be removed.")) return;
    signIn.disabled = true;
    try {
      await request("/api/faraz/auth/logout", { method: "POST" });
      setConnected({ connected: false, state: "not_connected" });
      toast("FARAZ session has been signed out", "success");
    } catch (error) {
      toast(error.message, "error");
    } finally {
      signIn.disabled = false;
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
      mode, to, symbolName: $id(view, "candleExportSymbol").value.trim(), resolution: $id(view, "candleExportResolution").value.trim(),
      host: $id(view, "candleExportHost").value,
      packetSize: Number($id(view, "candleExportPacketSize").value), rateLimitMs: Number($id(view, "candleExportRate").value),
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
      return;
    }
    for (const entry of logs) {
      const row = document.createElement("p");
      row.dataset.level = entry.level || "info";
      const time = new Date(entry.time).toLocaleString("en-GB", { timeZone: "Asia/Tehran", hour12: false, year: "numeric", month: "2-digit", day: "2-digit", hour: "2-digit", minute: "2-digit", second: "2-digit" });
      row.textContent = `[${time} UTC+3.5 Tehran] ${entry.message || ""}`;
      box.append(row);
    }
    box.scrollTop = box.scrollHeight;
  }

  function renderValidation(checks = []) {
    const list = $id(view, "candleValidationList");
    list.replaceChildren();
    if (!checks.length) {
      const empty = document.createElement("p");
      empty.className = "candle-validation-empty";
      empty.textContent = "Awaiting a saved RAW file.";
      list.append(empty);
      return;
    }
    for (const check of checks) {
      const item = document.createElement("div");
      const passed = Boolean(check.passed);
      item.className = "candle-validation-item";
      item.dataset.state = passed ? "pass" : "fail";
      item.innerHTML = `${icon(passed ? "check" : "cross", 17)}<span><b>${check.label || "Validation"}</b><small>${check.detail || "—"}</small></span>`;
      list.append(item);
    }
  }

  function renderJob(job) {
    const total = Number(job.totalPackets || 0);
    const received = Number(job.receivedPackets || 0);
    const percent = total ? Math.min(100, Math.round(received / total * 100)) : 0;
    $id(view, "candleStatusStage").textContent = job.stage || "—";
    $id(view, "candleStatusPackets").textContent = `${received} / ${total}`;
    $id(view, "candleStatusRows").textContent = Number(job.receivedRows || 0).toLocaleString("en-US");
    $id(view, "candleStatusCandles").textContent = Number(job.candleCountResult || 0).toLocaleString("en-US");
    $id(view, "candleProgressText").textContent = `${received} / ${total} packets`;
    $id(view, "candleProgressPercent").textContent = `${percent}%`;
    $id(view, "candleProgressFill").style.width = `${percent}%`;
    $id(view, "candleProgressFill").parentElement.setAttribute("aria-valuenow", String(percent));
    setExtractionState(job.done ? "success" : (job.cancelRequested || (!job.running && job.error) ? "error" : "idle"));
    $id(view, "candleStart").disabled = Boolean(job.running);
    $id(view, "candleCancel").disabled = !job.running;
    const openFile = $id(view, "candleOpenFile");
    openFile.classList.toggle("hidden", !job.openUrl);
    openFile.dataset.url = job.openUrl || "";
    if (job.savedPath) $id(view, "candleActionHint").textContent = `Saved automatically to ${job.savedPath}`;
    if (job.endpoint) $id(view, "candleInfoEndpoint").textContent = job.endpoint;
    renderLogs(job.logs);
    renderValidation(job.validation);
  }

  async function pollJob() {
    if (!currentJobId) return;
    try {
      const job = await request(`/api/faraz/candles/status?id=${encodeURIComponent(currentJobId)}`);
      renderJob(job);
      if (!job.running) {
        clearInterval(jobTimer);
        jobTimer = null;
        currentJobId = null;
        persistState();
        toast(job.done ? `${job.candleCountResult} candles are ready` : job.error || "Extraction stopped", job.done ? "success" : "error");
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
      clearExtractionStatus();
      const job = await request("/api/faraz/candles/start", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(params()) });
      currentJobId = job.id;
      persistState();
      renderJob(job);
      clearInterval(jobTimer);
      jobTimer = setInterval(pollJob, 800);
      await pollJob();
    } catch (error) {
      toast(error.message, "error");
    }
  }

  async function cancel() {
    if (!currentJobId) return;
    await request("/api/faraz/candles/cancel", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ id: currentJobId }) }).then(() => setExtractionState("error")).catch((error) => { setExtractionState("error"); toast(error.message, "error"); });
  }

  function reset() {
    currentJobId = null;
    clearInterval(jobTimer);
    jobTimer = null;
    defaultsSet = false;
    $id(view, "candleExportPacketSize").value = "1000";
    $id(view, "candleExportRate").value = "30";
    $id(view, "candleExportCount").value = "1000";
    $id(view, "candleCountToNow").checked = true;
    $id(view, "candleRangeToNow").checked = true;
    setMode("range");
    renderJob({ stage: connected ? "Ready" : "Locked", status: connected ? "Ready after authentication." : "Authentication required.", logs: [], validation: [] });
    applyDefaults();
    persistState();
  }

  restoreState();
  signIn.onclick = openLogin;
  checkSession.onclick = async () => {
    toast("Refreshing FARAZ session", "info");
    await refreshAuth();
    toast(connected ? "FARAZ session refreshed" : "FARAZ session is not connected", connected ? "success" : "error");
  };
  $id(view, "candleOpenFaraz").onclick = openFaraz;
  $id(view, "candleModeCount").onclick = () => setMode("count");
  $id(view, "candleModeRange").onclick = () => setMode("range");
  $id(view, "candleCountToNow").onchange = (event) => { $id(view, "candleCountToRow").classList.toggle("hidden", event.target.checked); renderEpochs(); };
  $id(view, "candleRangeToNow").onchange = (event) => { $id(view, "candleRangeToRow").classList.toggle("hidden", event.target.checked); renderEpochs(); };
  $id(view, "candleCountToButton").onclick = () => openDateTimePicker("#candleCountTo");
  $id(view, "candleRangeFromButton").onclick = () => openDateTimePicker("#candleRangeFrom");
  $id(view, "candleRangeToButton").onclick = () => openDateTimePicker("#candleRangeTo");
  $id(view, "candleStart").onclick = start;
  $id(view, "candleCancel").onclick = cancel;
  $id(view, "candleReset").onclick = reset;
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
  };
  $id(view, "candleSymbolRemove").onclick = () => {
    const select = $id(view, "candleExportSymbol");
    if (["FOREXCOM:XAUUSD", "FXCM:USOIL"].includes(select.value)) return toast("The two default symbols cannot be removed", "error");
    select.selectedOptions[0]?.remove();
    if (!select.options.length) toast("Add a symbol before starting extraction", "error");
    persistState();
  };
  $id(view, "candleExportHost").onchange = () => { hostInitialized = true; persistState(); };
  view.addEventListener("input", (event) => {
    if (event.target.closest("#candleExportControls")) persistState();
  });
  view.addEventListener("change", (event) => {
    if (event.target.closest("#candleExportControls")) persistState();
  });
  function renderEpochs() {
    const now = Math.floor(Date.now() / 1000);
    for (const [inputId, outputId, toNow] of [["candleCountTo", "candleCountToEpoch", $id(view, "candleCountToNow").checked], ["candleRangeFrom", "candleRangeFromEpoch", false], ["candleRangeTo", "candleRangeToEpoch", $id(view, "candleRangeToNow").checked]]) {
      const value = toNow ? now : parseTehranInput($id(view, inputId).value);
      $id(view, outputId).textContent = Number.isFinite(value) ? `${Math.floor(value)} UTC+3.5 Tehran` : "—";
    }
  }
  setInterval(renderEpochs, 1000);
  void refreshAuth();

  return {
    open() {
      visible = true;
      view.classList.remove("hidden");
      root.classList.add("candle-export-active");
      applyDefaults();
      renderEpochs();
      persistState();
      refreshAuth();
      if (currentJobId && !jobTimer) {
        pollJob().then(() => {
          if (currentJobId && !jobTimer && !$id(view, "candleCancel").disabled) jobTimer = setInterval(pollJob, 800);
        });
      }
      clearInterval(authTimer);
      authTimer = setInterval(() => { if (visible) refreshAuth(); }, 5000);
      $id(view, "candleSignIn").focus();
    },
    close() {
      visible = false;
      view.classList.add("hidden");
      root.classList.remove("candle-export-active");
      persistState();
      clearInterval(authTimer);
      authTimer = null;
    },
    refreshDefaults() { if (visible) { defaultsSet = false; applyDefaults(); } },
  };
}
