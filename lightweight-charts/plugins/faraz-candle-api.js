import fs from "node:fs";
import path from "node:path";
import { createHash, randomUUID } from "node:crypto";
import { execFile, execFileSync } from "node:child_process";
import { chromium } from "playwright-core";

const HISTORY_PATH = "/api/customer/trading-view/history";
const CHART_LIST_PATH = "/api/customer/chart-layout-v2/";
const AUTH_PROFILE_PATH = "/api/public/authentication/me";
const FARAZ_ORIGIN = "https://faraz.io";
const ALLOWED_HOSTS = new Set(["faraz.io", "ir3.faraz.io", "ir4.faraz.io"]);
const UNIT_SECONDS = { S: 1, M: 60, H: 3600, D: 86400, W: 604800 };
const MAX_PACKET_SIZE = 200_000;
const MAX_PACKETS = 200_000;
const MAX_RATE_LIMIT_MS = 60_000;
const MAX_RETRIES = 5;
const RETRY_BASE_DELAY_MS = 600;
const REQUEST_TIMEOUT_MS = 15_000;
const PRIMARY_CONCURRENCY = 6;
const SESSION_FILE_VERSION = 2;

export function parseResolutionToSeconds(value) {
  const resolution = String(value ?? "").trim().toUpperCase();
  if (/^\d+$/.test(resolution)) return Math.max(1, Number(resolution));
  const match = resolution.match(/^(\d+)(S|M|H|D|W)$/);
  if (!match || Number(match[1]) < 1) {
    throw new Error("Timeframe must look like 1S, 30S, 1M, 4H, 1D, or 1W.");
  }
  return Number(match[1]) * UNIT_SECONDS[match[2]];
}

export function normalizeHistoryPayload(payload) {
  return normalizeHistoryPayloadDetails(payload).candles;
}

export function normalizeHistoryPayloadDetails(payload) {
  const result = payload?.result && typeof payload.result === "object" ? payload.result : payload;
  if (result?.s === "no_data") return { candles: [], receivedRows: 0, rejectedRows: 0 };
  const t = Array.isArray(result?.t) ? result.t : [];
  const o = Array.isArray(result?.o) ? result.o : [];
  const h = Array.isArray(result?.h) ? result.h : [];
  const l = Array.isArray(result?.l) ? result.l : [];
  const c = Array.isArray(result?.c) ? result.c : [];
  const lengths = [t.length, o.length, h.length, l.length, c.length];
  if (!lengths.some(Boolean) && !Array.isArray(result?.t)) {
    throw new Error("FARAZ history response does not contain candle arrays.");
  }
  const rows = [];
  const receivedRows = Math.max(...lengths);
  let rejectedRows = receivedRows - Math.min(...lengths);
  for (let index = 0; index < Math.min(...lengths); index++) {
    const candle = { time: Math.trunc(Number(t[index])), open: Number(o[index]), high: Number(h[index]), low: Number(l[index]), close: Number(c[index]) };
    if (!Number.isSafeInteger(candle.time) || candle.time <= 0
      || ![candle.open, candle.high, candle.low, candle.close].every(Number.isFinite)
      || candle.high < Math.max(candle.open, candle.close, candle.low)
      || candle.low > Math.min(candle.open, candle.close, candle.high)) {
      rejectedRows++;
      continue;
    }
    rows.push(candle);
  }
  return { candles: rows, receivedRows, rejectedRows };
}

export function mergeCandles(chunks, from, to) {
  const sorted = [];
  for (const chunk of chunks) {
    for (const candle of chunk) {
      if (candle.time >= from && candle.time <= to) sorted.push(candle);
    }
  }
  sorted.sort((left, right) => left.time - right.time);
  const candles = [];
  let duplicates = 0;
  let conflicts = 0;
  for (const candle of sorted) {
    const previous = candles.at(-1);
    if (!previous || previous.time !== candle.time) {
      candles.push(candle);
      continue;
    }
    duplicates++;
    if (previous.open !== candle.open || previous.high !== candle.high || previous.low !== candle.low || previous.close !== candle.close) conflicts++;
  }
  return { candles, duplicates, conflicts };
}

function tehranDisplayTime(epochSeconds) {
  return `${tehranFilenameTime(epochSeconds)} UTC+3:30 Tehran`;
}

/**
 * This runs on the parsed temporary RAW file immediately before the atomic
 * move into market-data/raw.  Gaps are allowed (a market may have no candle),
 * but every present interval must be an integral multiple of the requested
 * timeframe and must stay inside the exact requested epoch bounds.
 */
export function verifySavedCandles(candles, { from, to, timeframeSeconds } = {}) {
  const rows = Array.isArray(candles) ? candles : [];
  const validRow = (candle) => candle && Object.keys(candle).length === 5
    && ["time", "open", "high", "low", "close"].every((key) => Object.hasOwn(candle, key))
    && Number.isSafeInteger(candle.time) && candle.time > 0
    && [candle.open, candle.high, candle.low, candle.close].every(Number.isFinite)
    && candle.high >= Math.max(candle.open, candle.close, candle.low)
    && candle.low <= Math.min(candle.open, candle.close, candle.high);
  const chronological = rows.length > 0 && rows.every((candle, index) => validRow(candle)
    && (!index || candle.time > rows[index - 1].time));
  const first = rows[0]?.time;
  const last = rows.at(-1)?.time;
  const bounds = Number.isFinite(from) && Number.isFinite(to)
    && rows.length > 0 && rows.every((candle) => candle.time >= from && candle.time <= to);
  const timeframe = Number(timeframeSeconds);
  const timeframeValid = Number.isSafeInteger(timeframe) && timeframe > 0 && rows.length > 0
    && rows.every((candle, index) => !index || (candle.time - rows[index - 1].time) % timeframe === 0);
  const checks = [
    { key: "chronology", label: "Timestamp order", passed: chronological, detail: chronological ? "Strict ascending timestamps; no duplicates." : "Rows are not strictly chronological or contain invalid data." },
    { key: "firstLast", label: "First and last candle", passed: Number.isFinite(first) && Number.isFinite(last), detail: Number.isFinite(first) && Number.isFinite(last) ? `First ${tehranDisplayTime(first)} · Last ${tehranDisplayTime(last)}` : "The saved file does not contain a valid first and last candle." },
    { key: "range", label: "Requested range", passed: bounds, detail: `Requested ${from} → ${to} · stored ${first ?? "—"} → ${last ?? "—"}` },
    { key: "integrity", label: "Saved OHLC integrity", passed: rows.length > 0 && rows.every(validRow), detail: rows.length ? `${rows.length.toLocaleString("en-US")} rows have exact fields and valid OHLC bounds.` : "No candles were saved." },
    { key: "timeframe", label: "Requested timeframe", passed: timeframeValid, detail: timeframeValid ? `Every adjacent stored interval is a multiple of ${timeframe} seconds; market gaps are retained.` : `Stored intervals do not match the requested ${timeframe || "unknown"}-second timeframe.` },
  ];
  return { valid: checks.every((check) => check.passed), checks };
}

function json(res, status, body) {
  res.statusCode = status;
  res.setHeader("Content-Type", "application/json; charset=utf-8");
  res.setHeader("Cache-Control", "no-store");
  res.end(JSON.stringify(body));
}

function readJson(req, limit = 100_000) {
  return new Promise((resolve, reject) => {
    let body = "";
    req.setEncoding("utf8");
    req.on("data", (part) => {
      body += part;
      if (body.length > limit) reject(new Error("Request is too large."));
    });
    req.on("end", () => {
      try { resolve(JSON.parse(body || "{}")); }
      catch { reject(new Error("Request body must be valid JSON.")); }
    });
    req.on("error", reject);
  });
}

function registryDefaultBrowserExecutable() {
  if (process.platform !== "win32") return null;
  try {
    const association = execFileSync("reg.exe", ["query", "HKCU\\Software\\Microsoft\\Windows\\Shell\\Associations\\UrlAssociations\\https\\UserChoice", "/v", "ProgId"], { encoding: "utf8", windowsHide: true });
    const progId = association.match(/^\s*ProgId\s+REG_SZ\s+(.+)$/im)?.[1]?.trim();
    if (!progId) return null;
    const command = execFileSync("reg.exe", ["query", `HKCR\\${progId}\\shell\\open\\command`, "/ve"], { encoding: "utf8", windowsHide: true });
    const commandValue = command.match(/^\s*\(Default\)\s+REG_SZ\s+(.+)$/im)?.[1]?.trim();
    const executable = commandValue?.match(/^"([^"]+\.exe)"/i)?.[1] || commandValue?.match(/^([^\s]+\.exe)/i)?.[1];
    return executable && fs.existsSync(executable) ? executable : null;
  } catch {
    return null;
  }
}

function browserExecutable() {
  const explicit = process.env.FARAZ_BROWSER_PATH;
  if (explicit && fs.existsSync(explicit)) return explicit;
  const systemDefault = registryDefaultBrowserExecutable();
  if (systemDefault) {
    if (/\b(?:chrome|msedge|brave|vivaldi|chromium)\.exe$/i.test(systemDefault)) return systemDefault;
    throw new Error(`The Windows default browser (${path.basename(systemDefault)}) is not Chromium-based and cannot expose a FARAZ session to this local app.`);
  }
  const candidates = [
    process.platform === "win32" ? "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe" : null,
    process.platform === "win32" ? "C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe" : null,
    process.platform === "win32" ? "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe" : null,
    process.platform === "darwin" ? "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" : null,
    process.platform === "linux" ? "/usr/bin/google-chrome" : null,
    process.platform === "linux" ? "/usr/bin/chromium" : null,
  ].filter(Boolean);
  const executable = candidates.find((candidate) => fs.existsSync(candidate));
  if (!executable) throw new Error("A Chromium-based system browser was not found. Set FARAZ_BROWSER_PATH to its executable.");
  return executable;
}

function runDpapi(script, input) {
  if (process.platform !== "win32") throw new Error("Persistent FARAZ secret storage currently requires Windows DPAPI.");
  return execFileSync("powershell.exe", ["-NoLogo", "-NoProfile", "-NonInteractive", "-Command", script], {
    encoding: "utf8", input, windowsHide: true, maxBuffer: 20_000_000,
  }).trim();
}

function protectForCurrentWindowsUser(plainText) {
  return runDpapi("Add-Type -AssemblyName System.Security;$value=[Console]::In.ReadToEnd();$bytes=[Text.Encoding]::UTF8.GetBytes($value);$protected=[Security.Cryptography.ProtectedData]::Protect($bytes,$null,[Security.Cryptography.DataProtectionScope]::CurrentUser);[Convert]::ToBase64String($protected)", plainText);
}

function unprotectForCurrentWindowsUser(cipherText) {
  return runDpapi("Add-Type -AssemblyName System.Security;$value=[Console]::In.ReadToEnd().Trim();$protected=[Convert]::FromBase64String($value);$bytes=[Security.Cryptography.ProtectedData]::Unprotect($protected,$null,[Security.Cryptography.DataProtectionScope]::CurrentUser);[Text.Encoding]::UTF8.GetString($bytes)", cipherText);
}

function safeHost(value) {
  const host = String(value || "faraz.io").toLowerCase();
  if (!ALLOWED_HOSTS.has(host)) throw new Error("Unsupported FARAZ history host.");
  return host;
}

function chunkRange(from, to, timeframeSeconds, packetSize, startIndex = 0) {
  if (!Number.isFinite(from) || !Number.isFinite(to) || from >= to) throw new Error("The selected range is invalid.");
  const span = timeframeSeconds * packetSize;
  const chunks = [];
  for (let cursor = from, index = startIndex; cursor < to; cursor += span, index++) {
    if (chunks.length >= MAX_PACKETS) throw new Error("The request exceeds the packet safety limit.");
    const chunkTo = Math.min(to, cursor + span);
    chunks.push({ index, from: cursor, to: chunkTo, countback: packetSize, firstDataRequest: index === 0, latest: chunkTo >= to });
  }
  return chunks;
}

function sanitiseFilePart(value) {
  return String(value || "UNKNOWN").replace(/:/g, "_").replace(/[^a-zA-Z0-9._-]+/g, "-").replace(/^-+|-+$/g, "") || "UNKNOWN";
}

function tehranFilenameTime(epochSeconds) {
  const parts = new Intl.DateTimeFormat("en-CA", {
    timeZone: "Asia/Tehran", year: "numeric", month: "2-digit", day: "2-digit",
    hour: "2-digit", minute: "2-digit", second: "2-digit", hourCycle: "h23",
  }).formatToParts(new Date(epochSeconds * 1000)).reduce((out, part) => ((out[part.type] = part.value), out), {});
  return `${parts.year}-${parts.month}-${parts.day} ${parts.hour}-${parts.minute}-${parts.second}`;
}

export function buildCandleFilename(symbolName, resolution, firstTime, lastTime) {
  return `RAW ${sanitiseFilePart(symbolName)} ${String(resolution).toUpperCase()} FROM ${tehranFilenameTime(firstTime)} TO ${tehranFilenameTime(lastTime)}.json`;
}

function readCookieValue(cookieHeader, name) {
  const match = String(cookieHeader || "").match(new RegExp(`(?:^|;\\s*)${name}=([^;]*)`, "i"));
  return match ? match[1] : "";
}

function clearTextCredentials(value = {}) {
  return {
    xAccessToken: String(value["x-access-token"] || value.xAccessToken || "").trim(),
    farazSession: String(value.farazSession || "").trim(),
  };
}

// Clear text is accepted only as a one-time legacy/manual import. Loading it
// immediately rewrites the file as a current-user Windows DPAPI envelope.
export function normalizeClearTextSession(value) {
  if (!value || typeof value !== "object") return null;
  const credentials = clearTextCredentials(value);
  const storageState = value.storageState && typeof value.storageState === "object"
    ? structuredClone(value.storageState)
    : { cookies: [], origins: [] };
  storageState.cookies = Array.isArray(storageState.cookies) ? storageState.cookies : [];
  storageState.origins = Array.isArray(storageState.origins) ? storageState.origins : [];
  if (credentials.farazSession && !storageState.cookies.some((cookie) => cookie?.name === "farazSession" && /(^|\.)faraz\.io$/i.test(cookie.domain || ""))) {
    storageState.cookies.push({ name: "farazSession", value: credentials.farazSession, domain: ".faraz.io", path: "/", expires: -1, httpOnly: false, secure: true, sameSite: "Lax" });
  }
  const historyAuth = value.historyAuth && ALLOWED_HOSTS.has(value.historyAuth.host) ? value.historyAuth : null;
  if (!credentials.xAccessToken && !credentials.farazSession && !storageState.cookies.some((cookie) => /(^|\.)faraz\.io$/i.test(cookie?.domain || ""))) return null;
  return { storageState, credentials, historyAuth };
}

export function createFarazCandleApi({ workspaceRoot = path.resolve(process.cwd(), ".."), launchBrowser, fetchImpl = globalThis.fetch } = {}) {
  const secretDir = path.join(workspaceRoot, "primary-cache", "secret");
  const secretPath = path.join(secretDir, "faraz-session.dpapi.json");
  const outputDir = path.join(workspaceRoot, "market-data", "raw");
  const temporaryOutputDir = path.join(workspaceRoot, "tmp", "faraz-candle-exports");
  const jobs = new Map();
  let browser = null;
  let context = null;
  let authPage = null;
  let contextHeadless = null;
  let browserServer = null;
  let browserPid = null;
  let historyAuth = null;
  let credentials = { xAccessToken: "", farazSession: "" };
  let storedStorageState = { cookies: [], origins: [] };
  let sessionCapturePending = null;
  const observedHistoryPages = new WeakSet();

  function loadStoredSession() {
    if (!fs.existsSync(secretPath)) return null;
    const envelope = JSON.parse(fs.readFileSync(secretPath, "utf8"));
    let decoded;
    let migrateClearText = false;
    if (envelope.version === SESSION_FILE_VERSION && envelope.protection === "windows-dpapi-current-user" && typeof envelope.payload === "string") {
      decoded = JSON.parse(unprotectForCurrentWindowsUser(envelope.payload));
    } else if (envelope.format === "clear-text") {
      decoded = envelope;
      migrateClearText = true;
    } else {
      throw new Error("The stored FARAZ session file has an unsupported format.");
    }
    const restored = normalizeClearTextSession(decoded);
    if (!restored) throw new Error("The stored FARAZ session file is empty or has an unsupported format.");
    credentials = restored.credentials;
    historyAuth = restored.historyAuth;
    storedStorageState = restored.storageState;
    if (migrateClearText) persistStorageState(storedStorageState);
    return storedStorageState;
  }

  function persistStorageState(storageState) {
    fs.mkdirSync(secretDir, { recursive: true, mode: 0o700 });
    storedStorageState = storageState;
    const protectedSession = protectForCurrentWindowsUser(JSON.stringify({
      version: SESSION_FILE_VERSION,
      updatedAt: new Date().toISOString(),
      "x-access-token": credentials.xAccessToken,
      farazSession: credentials.farazSession,
      storageState,
      historyAuth,
    }));
    const envelope = { version: SESSION_FILE_VERSION, protection: "windows-dpapi-current-user", payload: protectedSession };
    fs.writeFileSync(secretPath, JSON.stringify(envelope), { encoding: "utf8", mode: 0o600 });
  }

  async function persistSession() {
    const storageState = await context.storageState({ indexedDB: true });
    const sessionCookie = storageState.cookies.find((cookie) => cookie?.name === "farazSession" && /(^|\.)faraz\.io$/i.test(cookie.domain || ""));
    if (sessionCookie?.value) credentials.farazSession = sessionCookie.value;
    if (!credentials.xAccessToken && authPage && !authPage.isClosed()) {
      const pageToken = await authPage.evaluate(() => {
        const values = Object.values(localStorage);
        return values.map((value) => String(value).match(/eyJ[a-zA-Z0-9_-]+\.[a-zA-Z0-9_-]+\.[a-zA-Z0-9_-]+/)?.[0]).find(Boolean) || "";
      }).catch(() => "");
      if (pageToken) credentials.xAccessToken = pageToken;
    }
    persistStorageState(storageState);
  }

  function killBrowserProcessTree(pid) {
    if (process.platform !== "win32" || !Number.isSafeInteger(pid) || pid <= 0) return;
    try { execFileSync("taskkill.exe", ["/PID", String(pid), "/T", "/F"], { windowsHide: true, stdio: "ignore" }); }
    catch {}
  }

  async function closeBrowserContext({ forceKill = false } = {}) {
    const closingBrowser = browser;
    const closingServer = browserServer;
    const closingPid = browserPid;
    browser = null;
    browserServer = null;
    browserPid = null;
    context = null;
    authPage = null;
    contextHeadless = null;
    if (closingBrowser?.isConnected()) await closingBrowser.close().catch(() => {});
    await closingServer?.close().catch(() => {});
    if (forceKill) {
      await closingServer?.kill().catch(() => {});
      killBrowserProcessTree(closingPid);
    }
  }

  async function clearStoredSession() {
    await closeBrowserContext();
    historyAuth = null;
    credentials = { xAccessToken: "", farazSession: "" };
    storedStorageState = { cookies: [], origins: [] };
    if (fs.existsSync(secretPath)) fs.unlinkSync(secretPath);
  }

  function openSavedFile(outputPath) {
    if (!outputPath || !fs.existsSync(outputPath)) throw new Error("Saved RAW file was not found.");
    if (process.platform !== "win32") throw new Error("Opening saved RAW files is currently supported on Windows only.");
    return new Promise((resolve, reject) => {
      // Encoded PowerShell keeps the exact known path as one literal argument.
      const literalPath = outputPath.replaceAll("'", "''");
      const command = `Start-Process -FilePath '${literalPath}'`;
      const encoded = Buffer.from(command, "utf16le").toString("base64");
      execFile("powershell.exe", ["-NoLogo", "-NoProfile", "-NonInteractive", "-EncodedCommand", encoded], { windowsHide: true }, (error) => error ? reject(error) : resolve());
    });
  }

  function sessionHeaders(storageState = storedStorageState) {
    const now = Date.now() / 1000;
    const cookie = (storageState?.cookies || [])
      .filter((item) => item?.name && item?.value && /(^|\.)faraz\.io$/i.test(item.domain || "") && (!Number.isFinite(item.expires) || item.expires < 0 || item.expires > now))
      .map((item) => `${item.name}=${item.value}`)
      .join("; ");
    return {
      Accept: "application/json, text/plain, */*",
      ...(cookie ? { Cookie: cookie } : {}),
      ...(credentials.xAccessToken ? { "x-access-token": credentials.xAccessToken } : {}),
    };
  }

  async function directRequest(url, { timeoutMs = REQUEST_TIMEOUT_MS, controller = new AbortController() } = {}) {
    const timeout = setTimeout(() => controller.abort(), timeoutMs);
    try {
      return await fetchImpl(url, { method: "GET", signal: controller.signal, headers: sessionHeaders() });
    } finally {
      clearTimeout(timeout);
    }
  }

  async function probeStoredSession(symbolName = "FXCM:USOIL") {
    const host = safeHost(historyAuth?.host);
    const url = new URL(historyAuth?.endpoint && new URL(historyAuth.endpoint).host === host
      ? historyAuth.endpoint
      : `https://${host}${HISTORY_PATH}`);
    const to = Math.floor(Date.now() / 1000);
    for (const [key, value] of Object.entries({
      symbolName: endpointSymbolName(symbolName), resolution: historyAuth?.resolution || "30S",
      from: to - 86_400, to, countback: 1, firstDataRequest: true, latest: true,
      adjustType: historyAuth?.adjustType || "2", json: true,
    })) url.searchParams.set(key, String(value));
    const startedAt = Date.now();
    const response = await directRequest(url);
    const contentType = response.headers?.get?.("content-type") || "";
    return {
      connected: response.status !== 401 && response.status !== 403 && response.ok && /(?:application|text)\/json/i.test(contentType),
      status: response.status,
      pingMs: Date.now() - startedAt,
    };
  }

  async function readAuthenticatedProfile() {
    const response = await directRequest(new URL(`${FARAZ_ORIGIN}${AUTH_PROFILE_PATH}`));
    if (!response.ok) {
      const error = new Error(`FARAZ profile request failed with HTTP ${response.status}.`);
      error.status = response.status;
      throw error;
    }
    let payload;
    try { payload = JSON.parse(await response.text()); }
    catch { throw new Error("FARAZ profile response was not valid JSON."); }
    return {
      userId: typeof payload?._id === "string" ? payload._id : null,
      userName: typeof payload?.name === "string" ? payload.name : null,
      phone: typeof payload?.phone === "string" ? payload.phone : null,
    };
  }

  function captureHistoryRequest(request) {
    try {
      const url = new URL(request.url());
      if (!ALLOWED_HOSTS.has(url.host) || url.pathname !== HISTORY_PATH) return;
      historyAuth = {
        host: url.host,
        protocol: url.protocol,
        symbolName: url.searchParams.get("symbolName") || "",
        resolution: url.searchParams.get("resolution") || "",
        endpoint: `${url.origin}${url.pathname}`,
        adjustType: url.searchParams.get("adjustType") || "2",
        countback: Math.max(1, Number.parseInt(url.searchParams.get("countback"), 10) || 0),
        capturedAt: Date.now(),
      };
      const headers = request.headers();
      credentials = {
        xAccessToken: String(headers["x-access-token"] || headers.authorization || credentials.xAccessToken || "").replace(/^Bearer\s+/i, ""),
        farazSession: readCookieValue(headers.cookie, "farazSession") || credentials.farazSession,
      };
    } catch {}
  }

  function captureHistoryResponse(response) {
    try {
      const url = new URL(response.url());
      if (!ALLOWED_HOSTS.has(url.host) || url.pathname !== HISTORY_PATH || !response.ok()) return;
      if (sessionCapturePending) return;
      sessionCapturePending = (async () => {
        await persistSession();
        await closeBrowserContext({ forceKill: true });
      })().catch(() => {}).finally(() => { sessionCapturePending = null; });
    } catch {}
  }

  function observeHistoryRequests(page) {
    if (!page || observedHistoryPages.has(page)) return;
    observedHistoryPages.add(page);
    page.on("request", captureHistoryRequest);
    page.on("response", captureHistoryResponse);
  }

  function endpointSymbolName(symbolName) {
    const requested = String(symbolName || "").trim();
    const normalized = requested.replace(/:/g, "_").toUpperCase();
    if (historyAuth?.symbolName?.replace(/:/g, "_").toUpperCase() === normalized) return historyAuth.symbolName;
    return normalized;
  }

  async function ensureContext({ showLogin = false, showBrowser = false } = {}) {
    if (context && (showLogin || showBrowser) && contextHeadless) await closeBrowserContext();
    if (!context) {
      const executablePath = launchBrowser ? (process.env.FARAZ_BROWSER_PATH || null) : browserExecutable();
      let storageState;
      try {
        storageState = loadStoredSession();
      } catch (error) {
        // Only an explicit browser action may discard an obsolete encrypted
        // file.  Passive status checks must never recreate or alter it.
        if (!showLogin && !showBrowser) throw error;
        if (fs.existsSync(secretPath)) fs.unlinkSync(secretPath);
        historyAuth = null;
        credentials = { xAccessToken: "", farazSession: "" };
        storageState = null;
      }
      const headless = !showLogin && !showBrowser;
      const launch = launchBrowser || (async ({ executablePath }) => {
        const launchedServer = await chromium.launchServer({
          executablePath, headless,
          args: headless ? ["--no-first-run", "--no-default-browser-check"] : ["--start-maximized", "--no-first-run", "--no-default-browser-check"],
        });
        const launchedBrowser = await chromium.connect(launchedServer.wsEndpoint());
        const launchedContext = await launchedBrowser.newContext({ storageState: storageState || undefined, viewport: null });
        return { browser: launchedBrowser, context: launchedContext, browserServer: launchedServer, browserPid: launchedServer.process()?.pid || null };
      });
      const launched = await launch({ executablePath, headless, storageState });
      browser = launched.browser;
      context = launched.context;
      browserServer = launched.browserServer || null;
      browserPid = Number(launched.browserPid) || null;
      contextHeadless = headless;
      if (credentials.xAccessToken) await context.setExtraHTTPHeaders({ "x-access-token": credentials.xAccessToken });
      context.on?.("page", observeHistoryRequests);
      context.pages().forEach(observeHistoryRequests);
      browser.on?.("disconnected", () => {
        if (browser === launched.browser) {
          browser = null;
          context = null;
          authPage = null;
          contextHeadless = null;
        }
      });
    }
    const pages = context.pages();
    authPage = pages.find((page) => /^https:\/\/([^.]+\.)?faraz\.io\//i.test(page.url())) || pages[0] || await context.newPage();
    observeHistoryRequests(authPage);
    if (showLogin) {
      await authPage.goto(`${FARAZ_ORIGIN}/account/login`, { waitUntil: "domcontentloaded" });
    } else if (!/^https:\/\/([^.]+\.)?faraz\.io\//i.test(authPage.url())) {
      await authPage.goto(FARAZ_ORIGIN, { waitUntil: "domcontentloaded" });
    }
    if (showLogin || showBrowser) {
      await authPage.bringToFront();
    }
    return authPage;
  }

  async function authStatus(symbolName = "FXCM:USOIL") {
    try {
      if (!context) {
        if (!fs.existsSync(secretPath)) return { connected: false, state: "not_connected" };
        const storageState = loadStoredSession();
        const probe = await probeStoredSession(symbolName);
        const profile = probe.connected ? await readAuthenticatedProfile().catch(() => ({})) : {};
        return {
          connected: probe.connected,
          state: probe.connected ? "saved_session" : "expired_session",
          host: historyAuth?.host || "faraz.io",
          historyHost: historyAuth?.host || null,
          endpoint: historyAuth?.endpoint || null,
          httpStatus: probe.status,
          pingMs: probe.pingMs,
          ...profile,
          credentialStorage: "Windows-encrypted primary cache",
          savedCookies: storageState.cookies.filter((cookie) => /(^|\.)faraz\.io$/i.test(cookie?.domain || "")).length,
        };
      }
      if (!authPage || authPage.isClosed()) await ensureContext();
      const cookies = await context.cookies([FARAZ_ORIGIN]);
      if (!cookies.length) return { connected: false, state: "waiting_for_login" };
      if (!/^https:\/\/([^.]+\.)?faraz\.io\//i.test(authPage.url())) await authPage.goto(FARAZ_ORIGIN, { waitUntil: "domcontentloaded" });
      const probeStartedAt = Date.now();
      const probe = await authPage.evaluate(async ({ endpoint, symbol }) => {
        const response = await fetch(`${endpoint}?symbolName=${encodeURIComponent(symbol)}`, { credentials: "include", headers: { Accept: "application/json, text/plain, */*" } });
        return {
          status: response.status,
          ok: response.ok,
          contentType: response.headers.get("content-type") || "",
          redirectedToLogin: response.redirected && /\/account\/login/i.test(response.url),
        };
      }, { endpoint: CHART_LIST_PATH, symbol: symbolName });
      const connected = probe.status !== 401 && probe.status !== 403 && /(?:application|text)\/json/i.test(probe.contentType) && !probe.redirectedToLogin;
      const pageHost = new URL(authPage.url()).host;
      if (connected) {
        await persistSession();
        const storedProbe = await probeStoredSession(symbolName);
        const profile = storedProbe.connected ? await readAuthenticatedProfile().catch(() => ({})) : {};
        if (storedProbe.connected) await closeBrowserContext({ forceKill: true });
        return {
          connected,
          state: connected ? "connected" : "waiting_for_login",
          checkedAt: Date.now(),
          host: historyAuth?.host || pageHost,
          historyHost: historyAuth?.host || null,
          endpoint: historyAuth?.endpoint || null,
          adjustType: historyAuth?.adjustType || null,
          historyCapturedAt: historyAuth?.capturedAt || null,
          httpStatus: probe.status,
          pingMs: storedProbe.pingMs,
          credentialStorage: "Windows-encrypted primary cache",
          ...profile,
        };
      }
      return {
        connected,
        state: connected ? "connected" : "waiting_for_login",
        checkedAt: Date.now(),
        host: historyAuth?.host || pageHost,
        historyHost: historyAuth?.host || null,
        endpoint: historyAuth?.endpoint || null,
        adjustType: historyAuth?.adjustType || null,
        historyCapturedAt: historyAuth?.capturedAt || null,
        httpStatus: probe.status,
        pingMs: Date.now() - probeStartedAt,
        credentialStorage: "Windows-encrypted primary cache",
      };
    } catch (error) {
      return { connected: false, state: "waiting_for_login", error: error.message };
    }
  }

  function publicJob(job) {
    if (!job) return null;
    const { outputPath, abort, chunks, page, requestController, requestControllers, nextRequestAt, retryCooldownUntil, ...safe } = job;
    return { ...safe, totalPackets: chunks?.length || safe.totalPackets || 0, openUrl: job.done && outputPath ? `/api/faraz/candles/open?id=${encodeURIComponent(job.id)}` : null };
  }

  function log(job, level, message) {
    job.logs.push({ time: Date.now(), level, message });
    job.updatedAt = Date.now();
  }

  function captureHistoryResponse(job, chunk, response, text) {
    if (!job.responseAuditPath) return;
    try {
      const record = {
        capturedAt: new Date().toISOString(),
        stage: job.stage,
        request: {
          from: chunk.from,
          to: chunk.to,
          countback: chunk.countback,
          firstDataRequest: Boolean(chunk.firstDataRequest),
          latest: Boolean(chunk.latest),
        },
        response: { status: response.status, ok: response.ok, body: text },
      };
      fs.appendFileSync(job.responseAuditPath, `${JSON.stringify(record)}\n`, "utf8");
      job.capturedResponseCount = (job.capturedResponseCount || 0) + 1;
    } catch (error) {
      // Diagnostics must never turn an otherwise valid export into a failure.
      if (!job.responseAuditWriteFailed) {
        job.responseAuditWriteFailed = true;
        log(job, "warn", `Response audit could not be written: ${describeError(error)}.`);
      }
    }
  }

  function logPacketProgress(job, packetNumber, rows) {
    // Keep the browser responsive for long exports.  Packet-level successes
    // are sampled to at most 26 lines; failures and HTTP retries are never
    // sampled and retain their full diagnostic context.
    const total = job.chunks.length;
    const step = Math.max(1, Math.ceil(total / 24));
    if (packetNumber !== 1 && packetNumber !== total && packetNumber % step) return;
    const percent = total ? Math.round(packetNumber / total * 100) : 0;
    log(job, "success", `Primary progress ${Math.min(packetNumber, total)}/${total} (${percent}%): latest packet returned ${rows.length} in-range valid candle(s); total rows received ${job.receivedRows.toLocaleString("en-US")}.`);
  }

  function describeJobRequest(job, chunk) {
    return `stage=${job.stage}; endpoint=${job.endpoint}; symbol=${job.endpointSymbolName}; resolution=${job.resolution}; adjustType=${job.adjustType}; range=${chunk.from}→${chunk.to}`;
  }

  function describeError(error) {
    const cause = error?.cause?.message ? `; cause=${error.cause.message}` : "";
    const status = Number.isFinite(error?.status) ? `; httpStatus=${error.status}` : "";
    return `${error?.name || "Error"}: ${error?.message || "Unknown failure"}${status}${cause}`;
  }

  async function cancellableDelay(job, delayMs) {
    const deadline = Date.now() + delayMs;
    while (Date.now() < deadline) {
      if (job.abort.cancelled) throw new Error("Extraction cancelled.");
      await new Promise((resolve) => setTimeout(resolve, Math.min(100, deadline - Date.now())));
    }
  }

  async function paceRequest(job) {
    const now = Date.now();
    // The scheduler is shared by all workers: requests stay concurrent in
    // flight, while starts are smooth and a server-protection cooldown applies
    // globally instead of causing a retry burst.
    const scheduledAt = Math.max(now, Number(job.nextRequestAt) || now, Number(job.retryCooldownUntil) || now);
    job.nextRequestAt = scheduledAt + job.rateLimitMs;
    if (scheduledAt > now) await cancellableDelay(job, scheduledAt - now);
  }

  async function runConcurrent(job, entries, concurrency, worker) {
    const results = new Array(entries.length);
    let cursor = 0;
    const workers = Array.from({ length: Math.min(Math.max(1, concurrency), entries.length) }, async () => {
      while (!job.abort.cancelled) {
        const index = cursor++;
        if (index >= entries.length) return;
        results[index] = await worker(entries[index], index);
      }
      throw new Error("Extraction cancelled.");
    });
    await Promise.all(workers);
    return results;
  }

  async function fetchChunkOnce(job, chunk) {
    const url = new URL(job.endpoint);
    for (const [key, value] of Object.entries({
      symbolName: job.endpointSymbolName, resolution: job.resolution, from: chunk.from, to: chunk.to,
      countback: chunk.countback, firstDataRequest: chunk.firstDataRequest, latest: chunk.latest,
      adjustType: job.adjustType, json: true,
    })) url.searchParams.set(key, String(value));
    let response;
    const requestController = new AbortController();
    job.requestController = requestController;
    job.requestControllers?.add(requestController);
    try {
      await paceRequest(job);
      response = await directRequest(url, { controller: requestController });
    } catch (cause) {
      if (job.abort.cancelled) throw new Error("Extraction cancelled.");
      const error = new Error(cause?.name === "AbortError" ? "FARAZ history request timed out." : `FARAZ network error: ${cause?.message || "Network error"}`);
      error.cause = cause;
      throw error;
    } finally {
      if (job.requestController === requestController) job.requestController = null;
      job.requestControllers?.delete(requestController);
    }
    const text = await response.text();
    captureHistoryResponse(job, chunk, response, text);
    if (!response.ok) {
      const error = new Error(`FARAZ history request failed with HTTP ${response.status}: ${text}`);
      error.status = response.status;
      throw error;
    }
    let payload;
    try { payload = JSON.parse(text); }
    catch {
      const error = new Error("FARAZ returned invalid JSON with HTTP 200.");
      error.status = 200;
      throw error;
    }
    const normalized = normalizeHistoryPayloadDetails(payload);
    if (normalized.rejectedRows) {
      throw new Error(`FARAZ packet ${chunk.index + 1} contained ${normalized.rejectedRows} malformed or invalid candle row(s).`);
    }
    const inRange = normalized.candles.filter((candle) => candle.time >= chunk.from && candle.time <= chunk.to);
    const outsideRange = normalized.candles.length - inRange.length;
    if (outsideRange) {
      job.outsideRangePackets = (job.outsideRangePackets || 0) + 1;
      job.outsideRangeRows = (job.outsideRangeRows || 0) + outsideRange;
      const sampleStep = Math.max(1, Math.ceil(job.chunks.length / 12));
      if (job.outsideRangePackets <= 2 || job.outsideRangePackets % sampleStep === 0) {
        log(job, "warn", `${chunk.label || `Packet ${chunk.index + 1}/${job.chunks.length}`} returned ${outsideRange} countback candle(s) outside its requested range; they were excluded from validation and storage. Total excluded so far: ${job.outsideRangeRows}.`);
      }
    }
    return inRange;
  }

  async function fetchChunk(job, chunk) {
    for (let attempt = 1; attempt <= MAX_RETRIES; attempt++) {
      try {
        return await fetchChunkOnce(job, chunk);
      } catch (error) {
        if (job.abort.cancelled || error?.name === "AbortError") throw new Error("Extraction cancelled.");
        // A received HTTP 200 is authoritative, including an empty interval.
        // Retry traffic is reserved strictly for a concrete non-200 response.
        const retryableHttp = Number.isInteger(error?.status) && error.status !== 200;
        if (!retryableHttp || attempt === MAX_RETRIES) throw error;
        const delay = RETRY_BASE_DELAY_MS * 2 ** (attempt - 1) + Math.floor(Math.random() * RETRY_BASE_DELAY_MS);
        const label = chunk.label || `Packet ${chunk.index + 1}/${job.chunks.length}`;
        job.retryCooldownUntil = Math.max(Number(job.retryCooldownUntil) || 0, Date.now() + delay);
        log(job, "retry", `${label} received HTTP ${error.status}: ${describeError(error)}; ${describeJobRequest(job, chunk)}. HTTP retry ${attempt}/${MAX_RETRIES - 1} is queued after a shared ${delay} ms cooldown.`);
      }
    }
    throw new Error("FARAZ history request failed.");
  }

  function suspiciousGaps(candles, timeframeSeconds) {
    const gaps = [];
    for (let index = 1; index < candles.length; index++) {
      const previous = candles[index - 1];
      const next = candles[index];
      const difference = next.time - previous.time;
      if (difference <= timeframeSeconds || difference % timeframeSeconds !== 0) continue;
      gaps.push({
        key: `${previous.time}:${next.time}:${timeframeSeconds}`,
        previousTime: previous.time,
        nextTime: next.time,
        from: previous.time + timeframeSeconds,
        to: next.time - timeframeSeconds,
        missingCandles: difference / timeframeSeconds - 1,
      });
    }
    return gaps;
  }

  function recordSuspiciousGaps(job, initialCandles, attemptedGaps) {
    const gaps = suspiciousGaps(initialCandles, job.timeframeSeconds).filter((gap) => {
      if (attemptedGaps.has(gap.key)) return false;
      attemptedGaps.add(gap.key);
      return true;
    });
    if (!gaps.length) return { candles: initialCandles, supplemental: [], records: [] };
    const logStep = Math.max(1, Math.ceil(gaps.length / 24));
    log(job, "warn", `${gaps.length} suspicious gap interval(s) were detected. The detailed report retains every interval; this live log shows a compact sample.`);
    const records = gaps.map((gap, index) => {
      if (index < 2 || index === gaps.length - 1 || index % logStep === 0) {
        log(job, "warn", `Suspicious gap detected: ${gap.missingCandles} missing ${job.timeframeSeconds}s candle(s) from ${gap.from} (${tehranDisplayTime(gap.from)}) to ${gap.to} (${tehranDisplayTime(gap.to)}); retained without retry because the packet returned HTTP 200.`);
      }
      return { ...gap, attempts: 0, recoveredCandles: 0, remainingCandles: gap.missingCandles, status: "retained" };
    });
    return { candles: initialCandles, supplemental: [], records };
  }

  function verifyCollectedCandles(job, candles) {
    const verification = verifySavedCandles(candles, {
      from: job.mode === "count" ? candles[0]?.time : job.requestedFrom,
      to: job.requestedTo,
      timeframeSeconds: job.timeframeSeconds,
    });
    if (!verification.valid) {
      const failed = verification.checks.filter((check) => !check.passed).map((check) => `${check.label}: ${check.detail}`).join("; ");
      throw new Error(`Primary packet integrity verification failed: ${failed}`);
    }
    log(job, "success", `Primary packet integrity verification passed for ${candles.length.toLocaleString("en-US")} candle(s). No second HTTP-200 replay was sent.`);
    return candles;
  }

  async function runJob(job) {
    loadStoredSession();
    const status = await authStatus(job.symbolName);
    if (!status.connected) throw new Error("FARAZ authentication is required.");
    const collected = [];
    const gapSupplemental = [];
    const attemptedGaps = new Set();
    const suspiciousGapRecords = [];
    let cursor = 0;
    while (cursor < job.chunks.length) {
      if (job.abort.cancelled) throw new Error("Extraction cancelled.");
      job.stage = "Fetching candles";
      const batchStart = cursor;
      const batch = job.chunks.slice(cursor);
      log(job, "info", `Primary collection started for ${batch.length} packet(s) using ${PRIMARY_CONCURRENCY} concurrent worker(s); request starts are paced every ${job.rateLimitMs} ms.`);
      const rowsByChunk = await runConcurrent(job, batch, PRIMARY_CONCURRENCY, async (chunk, index) => {
        const packetNumber = batchStart + index + 1;
        job.sentPackets++;
        const rows = await fetchChunk(job, chunk);
        job.receivedPackets++;
        job.receivedRows += rows.length;
        logPacketProgress(job, packetNumber, rows);
        return rows;
      });
      collected.push(...rowsByChunk);
      cursor += batch.length;
      const primarySoFar = mergeCandles(collected, job.requestedFrom, job.requestedTo);
      if (primarySoFar.conflicts) throw new Error(`Extraction found ${primarySoFar.conflicts} conflicting duplicate candle(s); nothing was saved.`);
      if (cursor === job.chunks.length && job.mode === "count") {
        const merged = primarySoFar;
        if (merged.candles.length < job.candleCount) {
          const missing = job.candleCount - merged.candles.length;
          const currentSlots = Math.max(1, (job.requestedTo - job.requestedFrom) / job.timeframeSeconds);
          const density = merged.candles.length / currentSlots;
          const extensionSlots = Math.max(job.packetSize, Math.ceil((missing / Math.max(0.05, density)) * 1.15));
          const expandedFrom = job.requestedFrom - extensionSlots * job.timeframeSeconds;
          const extra = chunkRange(expandedFrom, job.requestedFrom, job.timeframeSeconds, job.packetSize, job.chunks.length);
          if (job.chunks.length + extra.length > MAX_PACKETS) throw new Error("The request exceeds the packet safety limit.");
          job.requestedFrom = expandedFrom;
          for (const extraChunk of extra) job.chunks.push(extraChunk);
          log(job, "warn", `${merged.candles.length}/${job.candleCount} candles collected; appended ${extra.length} older packet(s).`);
        }
      }
    }
    const primaryMerged = mergeCandles(collected, job.requestedFrom, job.requestedTo);
    const gapRecovery = recordSuspiciousGaps(job, primaryMerged.candles, attemptedGaps);
    if (gapRecovery.supplemental.length) gapSupplemental.push(...gapRecovery.supplemental);
    suspiciousGapRecords.push(...gapRecovery.records);
    const merged = mergeCandles([...collected, ...gapSupplemental], job.requestedFrom, job.requestedTo);
    let candles = merged.candles;
    if (job.mode === "count") candles = candles.slice(-job.candleCount);
    if (!candles.length) throw new Error("No valid candles were returned for the requested range.");
    if (job.mode === "count" && candles.length !== job.candleCount) throw new Error(`Only ${candles.length}/${job.candleCount} candles were available.`);
    if (merged.conflicts) throw new Error(`Extraction found ${merged.conflicts} conflicting duplicate candle(s); nothing was saved.`);
    job.stage = "Verifying completeness";
    candles = verifyCollectedCandles(job, candles);
    if (job.mode === "count") candles = candles.slice(-job.candleCount);
    let gaps = 0;
    for (let index = 1; index < candles.length; index++) if (candles[index].time - candles[index - 1].time > job.timeframeSeconds) gaps++;
    fs.mkdirSync(outputDir, { recursive: true });
    fs.mkdirSync(temporaryOutputDir, { recursive: true });
    const filename = buildCandleFilename(job.symbolName, job.resolution, candles[0].time, candles.at(-1).time);
    job.outputPath = path.join(outputDir, filename);
    const serialized = JSON.stringify(candles);
    if (fs.existsSync(job.outputPath)) {
      const existing = fs.readFileSync(job.outputPath, "utf8");
      if (existing !== serialized) {
        throw new Error(`A different candle file already exists at market-data/raw/${filename}.`);
      }
      const validation = verifySavedCandles(JSON.parse(existing), {
        from: job.requestedFrom, to: job.requestedTo, timeframeSeconds: job.timeframeSeconds,
      });
      job.validation = validation.checks;
      if (!validation.valid) throw new Error("Existing RAW file validation failed; it was not reused.");
    } else {
      const temporaryPath = path.join(temporaryOutputDir, `${job.id}.json.tmp`);
      let published = false;
      try {
        fs.writeFileSync(temporaryPath, serialized, { encoding: "utf8", flag: "wx" });
        const validation = verifySavedCandles(JSON.parse(fs.readFileSync(temporaryPath, "utf8")), {
          from: job.requestedFrom, to: job.requestedTo, timeframeSeconds: job.timeframeSeconds,
        });
        job.validation = validation.checks;
        if (!validation.valid) {
          for (const check of validation.checks.filter((item) => !item.passed)) log(job, "error", `Saved-file check failed: ${check.label}. ${check.detail}`);
          throw new Error("Saved RAW file validation failed; it was not moved into market-data/raw.");
        }
        const written = fs.readFileSync(temporaryPath);
        const expectedHash = createHash("sha256").update(serialized).digest("hex");
        const writtenHash = createHash("sha256").update(written).digest("hex");
        if (expectedHash !== writtenHash) throw new Error("Saved RAW file hash verification failed; the temporary file was not published.");
        fs.renameSync(temporaryPath, job.outputPath);
        published = true;
      } finally {
        if (!published && fs.existsSync(temporaryPath)) fs.unlinkSync(temporaryPath);
      }
    }
    Object.assign(job, { running: false, done: true, completedAt: Date.now(), stage: "Saved to market-data/raw", status: "Done", candleCountResult: candles.length, duplicates: merged.duplicates, conflicts: merged.conflicts, gaps, suspiciousGaps: suspiciousGapRecords, fileName: filename, savedPath: `market-data/raw/${filename}`, finalFrom: candles[0].time, finalTo: candles.at(-1).time });
    log(job, "success", `${candles.length} candles were saved to market-data/raw/${filename}.`);
  }

  async function startJob(params) {
    const symbolName = String(params.symbolName || "").trim();
    const resolution = String(params.resolution || "").trim().toUpperCase();
    if (!symbolName) throw new Error("Symbol is required.");
    const timeframeSeconds = parseResolutionToSeconds(resolution);
    const packetSize = Math.min(1000, Math.max(1, Math.trunc(Number(params.packetSize) || 1000)));
    const rateLimitValue = Number(params.rateLimitMs);
    const rateLimitMs = Math.min(MAX_RATE_LIMIT_MS, Math.max(30, Number.isFinite(rateLimitValue) ? Math.trunc(rateLimitValue) : 30));
    const mode = params.mode === "range" ? "range" : "count";
    const requestedTo = Math.trunc(Number(params.to));
    const candleCount = mode === "count" ? Math.max(1, Math.trunc(Number(params.candleCount) || 1000)) : null;
    const requestedFrom = mode === "count" ? requestedTo - Math.ceil(candleCount * timeframeSeconds * 1.35) : Math.trunc(Number(params.from));
    const chunks = chunkRange(requestedFrom, requestedTo, timeframeSeconds, packetSize);
    const id = randomUUID();
    if (!Number.isFinite(requestedTo) || requestedTo <= 0) throw new Error("End timestamp must be a valid Unix epoch.");
    if (mode === "range" && (!Number.isFinite(requestedFrom) || requestedFrom >= requestedTo)) throw new Error("From timestamp must be earlier than To.");
    const host = safeHost(params.host || historyAuth?.host);
    const capturedEndpoint = historyAuth?.endpoint && new URL(historyAuth.endpoint).host === host ? historyAuth.endpoint : null;
    const captureResponses = Boolean(params.captureResponses);
    const responseAuditPath = captureResponses ? path.join(temporaryOutputDir, `${id}.faraz-responses.ndjson`) : null;
    if (responseAuditPath) fs.mkdirSync(temporaryOutputDir, { recursive: true });
    const job = { id, running: true, done: false, error: null, stage: "Preparing", status: "Starting", mode, symbolName, endpointSymbolName: endpointSymbolName(symbolName), resolution, timeframeSeconds, packetSize, rateLimitMs, candleCount, requestedFrom, originalRequestedFrom: requestedFrom, requestedTo, host, endpoint: capturedEndpoint || `https://${host}${HISTORY_PATH}`, adjustType: historyAuth?.adjustType || "2", primaryConcurrency: PRIMARY_CONCURRENCY, retryConcurrency: PRIMARY_CONCURRENCY, sentPackets: 0, receivedPackets: 0, receivedRows: 0, outsideRangePackets: 0, outsideRangeRows: 0, captureResponses, responseAuditPath, capturedResponseCount: 0, createdAt: Date.now(), updatedAt: Date.now(), chunks, logs: [], validation: [], abort: { cancelled: false }, cancelRequested: false, requestControllers: new Set(), nextRequestAt: Date.now(), retryCooldownUntil: 0 };
    jobs.set(id, job);
    log(job, "info", `Extraction prepared with ${chunks.length} packet(s).`);
    runJob(job).catch((error) => {
      Object.assign(job, { running: false, done: false, failedAt: Date.now(), stage: error.message === "Extraction cancelled." ? "Cancelled" : "Error", status: "Failed", error: error.message });
      log(job, error.message === "Extraction cancelled." ? "warn" : "error", `${describeError(error)}; jobId=${job.id}; symbol=${job.endpointSymbolName}; resolution=${job.resolution}; endpoint=${job.endpoint}; requestedRange=${job.requestedFrom}→${job.requestedTo}; sentPackets=${job.sentPackets}; receivedPackets=${job.receivedPackets}; receivedRows=${job.receivedRows}.`);
    }).finally(() => { job.requestController = null; job.requestControllers?.clear(); });
    return publicJob(job);
  }

  return {
    name: "faraz-candle-export-api",
    configureServer(server) {
      // Authentication is intentionally user-driven.  Status checks inspect a
      // saved file only; they never launch a browser or migrate an old profile.
      server.middlewares.use("/api/faraz/auth/open", async (req, res) => {
        if (req.method !== "POST") return json(res, 405, { error: "POST is required." });
        try { await ensureContext({ showLogin: true }); json(res, 200, { ok: true, state: "waiting_for_login" }); }
        catch (error) { json(res, 500, { error: error.message }); }
      });
      server.middlewares.use("/api/faraz/auth/browser", async (req, res) => {
        if (req.method !== "POST") return json(res, 405, { error: "POST is required." });
        try { await ensureContext({ showBrowser: true }); json(res, 200, { ok: true }); }
        catch (error) { json(res, 500, { error: error.message }); }
      });
      server.middlewares.use("/api/faraz/auth/status", async (req, res) => {
        const symbol = new URL(req.url || "", "http://localhost").searchParams.get("symbolName") || undefined;
        json(res, 200, await authStatus(symbol));
      });
      server.middlewares.use("/api/faraz/auth/logout", async (req, res) => {
        if (req.method !== "POST") return json(res, 405, { error: "POST is required." });
        try { await clearStoredSession(); json(res, 200, { ok: true, state: "not_connected" }); }
        catch (error) { json(res, 500, { error: error.message }); }
      });
      server.middlewares.use("/api/faraz/candles/start", async (req, res) => {
        if (req.method !== "POST") return json(res, 405, { error: "POST is required." });
        try {
          const status = await authStatus();
          if (!status.connected) return json(res, 401, { error: "Sign in to FARAZ before starting extraction." });
          json(res, 202, await startJob(await readJson(req)));
        } catch (error) { json(res, 400, { error: error.message }); }
      });
      server.middlewares.use("/api/faraz/candles/status", (req, res) => {
        const id = new URL(req.url || "", "http://localhost").searchParams.get("id");
        const job = jobs.get(id);
        job ? json(res, 200, publicJob(job)) : json(res, 404, { error: "Extraction was not found." });
      });
      server.middlewares.use("/api/faraz/candles/cancel", async (req, res) => {
        if (req.method !== "POST") return json(res, 405, { error: "POST is required." });
        try {
          const { id } = await readJson(req);
          const job = jobs.get(id);
          if (!job) return json(res, 404, { error: "Extraction was not found." });
          job.abort.cancelled = true;
          job.cancelRequested = true;
          job.requestController?.abort();
          for (const controller of job.requestControllers || []) controller.abort();
          json(res, 200, { ok: true });
        } catch (error) { json(res, 400, { error: error.message }); }
      });
      server.middlewares.use("/api/faraz/candles/open", async (req, res) => {
        if (req.method !== "POST") return json(res, 405, { error: "POST is required." });
        const id = new URL(req.url || "", "http://localhost").searchParams.get("id");
        const job = jobs.get(id);
        try {
          if (!job?.done || !job.outputPath) throw new Error("Export file is not ready.");
          await openSavedFile(job.outputPath);
          json(res, 200, { ok: true });
        } catch (error) { json(res, 404, { error: error.message }); }
      });
      server.middlewares.use("/api/faraz/candles/download", (req, res) => {
        const id = new URL(req.url || "", "http://localhost").searchParams.get("id");
        const job = jobs.get(id);
        if (!job?.done || !job.outputPath || !fs.existsSync(job.outputPath)) return json(res, 404, { error: "Export file is not ready." });
        res.setHeader("Content-Type", "application/json; charset=utf-8");
        res.setHeader("Content-Disposition", `attachment; filename*=UTF-8''${encodeURIComponent(job.fileName)}`);
        res.setHeader("Cache-Control", "no-store");
        fs.createReadStream(job.outputPath).pipe(res);
      });
    },
  };
}

export default createFarazCandleApi();
