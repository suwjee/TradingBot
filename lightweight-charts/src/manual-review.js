// Presentation-only offline review. Behavior identities, prices and orders
// come exclusively from the supplied bridge payload, never chart inference.
const collections = {
  reactions: ["Reaction", "firstTime"], resets: ["Reset", "time"],
  blueLines: ["Blue Line", "sourceTime"], aZones: ["A", "sourceTime"],
  sZones: ["S", "sourceTime"], eZones: ["E", "sourceTime"],
  stopAlls: ["StopAll", "sourceTime"], orderReactions: ["Order reaction", "firstTime"],
  orderAudit: ["Order audit", "firstTime"],
};
const escapeHtml = (value) => String(value ?? "").replace(/[&<>"']/g,
  (char) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[char]);
const jsonScript = (value) => JSON.stringify(value).replace(/</g, "\\u003c").replace(/\u2028/g, "\\u2028").replace(/\u2029/g, "\\u2029");
const tehran = new Intl.DateTimeFormat("en-CA", {
  timeZone: "Asia/Tehran", year: "numeric", month: "2-digit", day: "2-digit",
  hour: "2-digit", minute: "2-digit", second: "2-digit", hourCycle: "h23",
});
export function reviewTime(epoch) {
  if (typeof epoch !== "number" || !Number.isFinite(epoch)) return "Undated";
  const parts = Object.fromEntries(tehran.formatToParts(new Date(epoch * 1000)).map((p) => [p.type, p.value]));
  return `${parts.year}-${parts.month}-${parts.day} ${parts.hour}:${parts.minute}:${parts.second}`;
}
function labelFor(group, row) {
  if (group === "sZones") return `S ${row.color ?? "—"}`;
  if (group === "eZones") return `E${row.number ?? "—"} ${row.family ?? "—"}`;
  if (group === "stopAlls") return `StopAll${row.number ?? "—"}`;
  return collections[group]?.[0] || group;
}
export function reviewCategory(group, row, direction) {
  if (group === "reactions") return { key: `${group}:${direction}`, label: `${direction === "bullish" ? "Bullish" : "Bearish"} reaction` };
  if (group === "sZones" || group === "eZones") {
    const family = (group === "sZones" ? row?.color : row?.family) || "unknown";
    return { key: `${group}:${family}`, label: `${group === "sZones" ? "S" : "E"} ${family}` };
  }
  return { key: group, label: collections[group]?.[0] || group };
}
const colorSpec = {
  "reactions:bullish": ["bullBorder", "#22c55e"], "reactions:bearish": ["bearBorder", "#ef4444"],
  resets: ["blueColor", "#06b6d4"], blueLines: ["blueColor", "#06b6d4"], aZones: ["aColor", "#7c3aed"],
  "sZones:blue": ["sBullColor", "#2563eb"], "sZones:red": ["sBearColor", "#f23645"],
  "eZones:blue": ["eBlueColor", "#1e3a8a"], "eZones:red": ["eRedColor", "#7f1d1d"],
  stopAlls: ["stopAllBorder", "#ff9800"], orderReactions: ["orderColor", "#8a8f98"], orderAudit: ["orderColor", "#8a8f98"],
};
const objectKinds = { reactions: "reaction", blueLines: "blue", aZones: "a", sZones: "s", eZones: "e", stopAlls: "stopall" };
const safeColor = (value) => typeof value === "string" && /^#[0-9a-f]{6}$/i.test(value);
export function reviewColor(record, snapshot = {}, objects = new Map((snapshot.indicatorObjects || []).map((item) => [item.id, item]))) {
  const [setting, fallback] = colorSpec[record.category.key] || ["", "#475569"];
  const object = objects.get(`indicator:${record.direction}:${objectKinds[record.group]}:${record.index}`);
  const chosen = object?.customized ? object.color : snapshot.settings?.[setting];
  return safeColor(chosen) ? chosen : fallback;
}
// Label boxes stay neutral; behavior identity is carried by the exact chart
// foreground color. Reactions and order records deliberately use black text.
export function reviewColorSurface() { return "#f3f5f7"; }
export function reviewLabelColor(record, chartColor) {
  return ["reactions", "orderReactions", "orderAudit"].includes(record.group)
    ? "#111827" : chartColor;
}
export function manualReviewFilename(date = new Date(), extension = "html") {
  const two = (value) => String(value).padStart(2, "0");
  return `manualTest-${date.getFullYear()}_${two(date.getMonth() + 1)}_${two(date.getDate())} ${two(date.getHours())}_${two(date.getMinutes())}_${two(date.getSeconds())}.${extension}`;
}
export function reviewRecords(payload) {
  const records = [];
  for (const [direction, groups] of Object.entries(payload.directions || {})) {
    for (const [group, rows] of Object.entries(groups)) {
      if (!Array.isArray(rows)) continue;
      rows.forEach((row, index) => {
        const epoch = row?.[collections[group]?.[1] || "sourceTime"];
        records.push({ id: `${direction}:${group}:${index}`, direction, group, row, index,
          category: reviewCategory(group, row, direction),
          epoch, time: reviewTime(epoch), label: labelFor(group, row || {}) });
      });
    }
  }
  return records.sort((a, b) => (a.epoch ?? Infinity) - (b.epoch ?? Infinity));
}
function human(value, key = "") {
  if (Array.isArray(value)) return value.map((item) => human(item, key));
  if (value && typeof value === "object") return Object.fromEntries(Object.entries(value).map(([k, v]) => [k, human(v, k)]));
  if (typeof value === "number" && (key.endsWith("Time") || ["time", "actualFrom", "actualTo"].includes(key)))
    return { epoch: value, Tehran: reviewTime(value) };
  return value;
}
const detail = (value) => `<pre>${escapeHtml(JSON.stringify(human(value), null, 2))}</pre>`;
function eventCard(record) {
  const { id, direction, row, time, label } = record;
  const visibleTime = time === "Undated" ? time : time.slice(11);
  return `<article class="event" data-id="${escapeHtml(id)}" data-filter="${escapeHtml(record.category.key)}" data-time="${time}" data-label="${escapeHtml(`${direction} | ${label}`)}">
    <div class="state-control" role="group" aria-label="Review status">${["true", "false"].map((status) => `<label class="${status}-choice" title="Mark as ${status}"><input class="state" type="radio" name="${escapeHtml(id)}" value="${status}" aria-label="Mark ${escapeHtml(`${direction} ${label} ${time}`)} as ${status}"><span class="sr-only">Mark as ${status}</span></label>`).join("")}</div>
    <button class="event-time copy-line" type="button" title="Copy full timestamp and review status"><time datetime="${time === "Undated" ? "" : time.replace(" ", "T")}">${visibleTime}</time></button>
    <div><span class="chip" style="color:${reviewLabelColor(record, record.color)};background:${reviewColorSurface()}">${escapeHtml(label)}</span><small>${escapeHtml(direction)}</small></div>
    <details class="bridge-output"><summary>Bridge output</summary>${detail(row)}</details></article>`;
}

// Self-contained review behavior is embedded in the saved file; it makes no requests.
function reviewRuntime() {
  const q = (selector) => document.querySelector(selector);
  const events = [...document.querySelectorAll(".event")];
  const references = [...document.querySelectorAll(".reference-row")];
  const filters = [...document.querySelectorAll(".category-filter")];
  const days = [...document.querySelectorAll(".day")];
  const key = `timeline-review-v4-${document.body.dataset.payloadHash}-${document.body.dataset.reviewId}`;
  let saved = {};
  try { saved = JSON.parse(localStorage.getItem(key) || "{}") || {}; } catch {}
  for (const event of events) {
    const status = saved[event.dataset.id];
    if (["true", "false"].includes(status)) event.querySelector(`input[value="${status}"]`).checked = true;
  }
  const statusOf = (event) => event.querySelector("input:checked")?.value;
  const line = (event) => `${event.dataset.time} | ${event.dataset.label} | ${statusOf(event) === "true" ? "True" : statusOf(event) === "false" ? "False" : "Unselected"}`;
  function update() {
    const from = q("#from").value.trim().replace("T", " "), to = q("#to").value.trim().replace("T", " ");
    const mode = q("#mode").value;
    const selected = new Set(filters.filter((input) => input.checked).map((input) => input.value));
    const invalid = !!(from && to && from > to);
    q("#range-error").hidden = !invalid;
    q("#to").setAttribute("aria-invalid", String(invalid));
    const hidden = (event) => invalid || !selected.has(event.dataset.filter) ||
      !!((from && event.dataset.time < from) || (to && event.dataset.time > to));
    const output = ["Indicator timeline manual review", "Timezone: Asia/Tehran", ""];
    const statuses = {};
    for (const event of events) {
      const status = statusOf(event);
      event.hidden = hidden(event);
      event.dataset.status = status || "";
      if (status) statuses[event.dataset.id] = status;
      if (!event.hidden && status && (mode === "all" || status === mode)) output.push(line(event));
    }
    for (const row of references) row.hidden = hidden(row);
    document.querySelectorAll(".collection").forEach((group) => { group.hidden = !group.querySelector(".reference-row:not([hidden])"); });
    days.forEach((day) => {
      const visible = [...day.querySelectorAll(".event:not([hidden])")];
      day.hidden = !visible.length;
      day.querySelector(".day-count").textContent = `${visible.length.toLocaleString()} events · ${visible.filter(statusOf).length.toLocaleString()} reviewed`;
    });
    const visibleCount = events.filter((event) => !event.hidden).length;
    q("#empty").hidden = visibleCount !== 0;
    const values = Object.values(statuses);
    q("#filter-note").textContent = `${visibleCount.toLocaleString()} of ${events.length.toLocaleString()} events visible · ${values.filter((v) => v === "true").length.toLocaleString()} True · ${values.filter((v) => v === "false").length.toLocaleString()} False · ${(events.length - values.length).toLocaleString()} unreviewed (all records).`;
    q("#report-text").value = output.join("\n");
    try {
      if (values.length) localStorage.setItem(key, JSON.stringify(statuses));
      else localStorage.removeItem(key);
    } catch { q("#storage-note").textContent = "Browser storage unavailable. Download the TXT report before closing this page."; }
  }
  async function copy(text) {
    try { await navigator.clipboard.writeText(text); }
    catch {
      const input = document.createElement("textarea"); input.value = text;
      document.body.append(input); input.select(); document.execCommand("copy"); input.remove();
    }
  }
  events.forEach((event) => {
    event.querySelectorAll("input").forEach((input) => { input.onchange = update; });
    event.querySelector(".copy-line").onclick = () => copy(line(event));
  });
  q("#from").oninput = update; q("#to").oninput = update; q("#mode").onchange = update;
  filters.forEach((input) => { input.onchange = update; });
  q("#reset").onclick = () => { q("#from").value = ""; q("#to").value = ""; update(); };
  q("#copy").onclick = () => copy(q("#report-text").value);
  q("#download").onclick = () => {
    const url = URL.createObjectURL(new Blob([q("#report-text").value], { type: "text/plain;charset=utf-8" }));
    const a = document.createElement("a"); a.href = url;
    const date = new Date(), two = (value) => String(value).padStart(2, "0");
    a.download = `manualTest-${date.getFullYear()}_${two(date.getMonth() + 1)}_${two(date.getDate())} ${two(date.getHours())}_${two(date.getMinutes())}_${two(date.getSeconds())}.txt`;
    a.click();
    setTimeout(() => URL.revokeObjectURL(url), 1000);
  };
  update();
}

const styles = `
:root{color-scheme:light;--ink:#17212e;--muted:#526176;--line:#dbe3ed;--surface:#fff;--accent:#334c7e;--focus:#2563eb}
*{box-sizing:border-box}body{margin:0;background:#f5f7fa;color:var(--ink);font:15px/1.65 Inter,-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Arial,sans-serif}
header,main{width:min(1120px,calc(100% - 40px));margin:auto}header{padding:40px 0 12px}main{padding-bottom:64px}h1{font-size:clamp(25px,4vw,34px);line-height:1.3;letter-spacing:-.035em;margin:8px 0}h2{font-size:19px;margin:0 0 12px}p{max-width:80ch;margin:8px 0 16px}p,small,.eyebrow{color:var(--muted)}small{font-size:12px}.eyebrow{font-size:11px;font-weight:700;letter-spacing:.12em}
.skip-link{position:absolute;top:-80px;left:20px;background:white;padding:12px;z-index:10}.skip-link:focus{top:8px}
.metrics{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));border:1px solid var(--line);border-radius:12px;background:var(--surface);margin-top:24px}.metric{padding:14px 18px}.metric+.metric{border-left:1px solid var(--line)}.metric span,.metric strong,.event small{display:block}.metric span{font-size:12px;color:var(--muted)}.metric strong{overflow-wrap:anywhere;font-size:13px;font-weight:600}
.filters,.report{padding:24px;margin:20px 0 28px;border:1px solid var(--line);border-radius:14px;background:var(--surface)}
.filter-fields,.report-controls,.section-head,.filter-actions{display:flex;gap:12px;flex-wrap:wrap;align-items:center}.filter-fields{align-items:end;margin-top:16px}.filter-fields label{display:grid;gap:6px;font-size:13px;font-weight:600}.section-head{justify-content:space-between;margin:20px 0 14px}.section-head h2{margin:0}
fieldset{border:0;padding:0;margin:0}legend{font-size:13px;font-weight:600;margin-bottom:10px}.category-options{display:flex;flex-wrap:wrap;gap:8px}.category-choice{display:flex;align-items:center;gap:9px;min-height:44px;padding:8px 12px;border:1px solid #9aa9bb;border-radius:9px;font-size:13px;cursor:pointer;background:#fff}.category-choice:has(:checked){border-color:var(--accent);background:#edf2fb}.category-choice input{width:18px;height:18px;min-height:0;padding:0;margin:0;accent-color:var(--accent)}.swatch{width:10px;height:10px;border:1px solid #0002;border-radius:3px}.filter-actions{margin:16px 0 4px}#filter-note{font-size:13px;margin:16px 0 0;font-variant-numeric:tabular-nums}
.day{margin-bottom:16px;border:1px solid var(--line);border-radius:12px;background:var(--surface);overflow:clip}.day-head{padding:16px 20px;list-style:none;display:flex;align-items:center;gap:12px;background:#edf1f7;color:var(--ink);font-weight:650}.day-head::-webkit-details-marker{display:none}.day-head:before{content:"";width:8px;height:8px;border-right:2px solid currentColor;border-bottom:2px solid currentColor;transform:rotate(-45deg);margin-right:5px}.day[open]>.day-head:before{transform:rotate(45deg)}.day-count{margin-left:auto;font-weight:400}.event{display:grid;grid-template-columns:132px 198px minmax(120px,1fr) minmax(130px,1fr);gap:16px;align-items:start;padding:16px 20px;border-top:1px solid var(--line);border-left:3px solid transparent}.event:nth-child(2n){background:#f9fafc}.event:hover,.event:focus-within{box-shadow:inset 0 0 0 1px #94a3b8;background:#f1f5fc}.event[data-status=true]{border-left-color:#15803d;background:#f0faf4}.event[data-status=false]{border-left-color:#be123c;background:#fff3f5}
.state-control{display:flex;gap:8px}.state-control label{position:relative;min-width:60px;min-height:44px;cursor:pointer}.state{position:absolute;inset:0;width:100%;height:100%;opacity:0;margin:0;cursor:pointer}.state+span{display:grid;place-items:center;min-height:44px;padding:8px;border:1px solid #8c9bab;border-radius:8px;background:white;font-size:12px;font-weight:650}.true-choice{color:#166534}.false-choice{color:#9f1239}.state:checked+span{background:currentColor;border-color:currentColor}.true-choice .state:checked+span{color:#fff;background:#166534}.false-choice .state:checked+span{color:#fff;background:#9f1239}.state:checked+span:before{content:"✓";font-size:11px;line-height:1}.state-control label:focus-within{outline:3px solid var(--focus);outline-offset:3px;border-radius:8px}
button,input,select{min-height:44px;max-width:100%;border:1px solid #97a6b8;border-radius:8px;background:white;color:var(--ink);font:inherit;padding:8px 12px}button{cursor:pointer;font-size:13px;font-weight:600;transition:background-color 120ms}button:hover{background:#edf2f8}button:active{background:#dfe8f5}button:focus-visible,input:focus-visible,select:focus-visible,summary:focus-visible,a:focus-visible{outline:3px solid var(--focus);outline-offset:3px}.danger{color:#9f1239;border-color:#c98797}.event-time{border:0;background:transparent;padding:10px 0;text-align:left;color:#334c7e;font:13px/1.6 "SF Mono",Consolas,ui-monospace,monospace;white-space:nowrap}.event-time:hover{text-decoration:underline}.chip{display:inline-block;border-radius:6px;border:1px solid #e0e5ed;padding:4px 8px;font-size:13px;font-weight:650;overflow-wrap:anywhere}.event small{margin:4px 0}
details summary{cursor:pointer;min-height:44px;padding:9px 0;color:#334c7e;font-size:13px}.day>summary{padding:16px 20px;color:var(--ink);font-size:15px}.event>details{min-width:0}.feature{margin:10px 0;border:1px solid var(--line);border-radius:10px;padding:10px 18px;background:var(--surface)}.feature>summary{overflow-wrap:anywhere}.feature>summary small{margin-left:12px}
pre,#report-text{background:#f8fafc;border:1px solid var(--line);border-radius:8px;padding:14px;color:#263449;font:12px/1.7 "SF Mono",Consolas,ui-monospace,monospace;white-space:pre-wrap;overflow-wrap:anywhere;max-height:480px;overflow:auto}#report-text{width:100%;min-height:240px;margin-top:16px}.reference-row{border-top:1px solid var(--line);padding:12px 0}.empty{padding:28px;border:1px dashed #94a3b8;border-radius:12px;text-align:center}.error{color:#9f1239}#action-note{font-size:13px;min-height:24px}[hidden]{display:none!important}
@media(max-width:800px){.metrics{grid-template-columns:repeat(2,minmax(0,1fr))}.metric:nth-child(3){border-left:0;border-top:1px solid var(--line)}.metric:nth-child(4){border-top:1px solid var(--line)}.event{grid-template-columns:132px minmax(0,1fr);gap:10px 16px}.event>details{grid-column:1/-1}.event>div:nth-of-type(2){grid-column:2;grid-row:2}.event-time{white-space:normal}.filters,.report{padding:20px}}
@media(max-width:440px){header,main{width:calc(100% - 24px)}header{padding-top:24px}.filters,.report{padding:16px}.event{padding:14px 12px;column-gap:10px;grid-template-columns:120px minmax(0,1fr)}.state-control{gap:6px}.state-control label{min-width:56px}.event-time{font-size:12px}.day>summary{padding:14px 12px;flex-wrap:wrap}.day-count{margin-left:20px;width:100%}.filter-fields label,.filter-fields input{width:100%}.metric{padding:12px}.metric strong{font-size:12px}}
@media(prefers-reduced-motion:reduce){*{transition:none!important;scroll-behavior:auto!important}}
@media print{.filters,.report-controls,.filter-actions,.skip-link{display:none}.event{break-inside:avoid}body{background:white}}

/* Reference manual-result.html presentation: compact, linear, and quiet. */
:root{--bg:#fbfcfe;--surface:#fff;--line:#e3e8ef;--ink:#17212e;--muted:#6c7786;--true:#effaf2;--false:#fff1f3}
body{background:var(--bg);font-size:14px;color:var(--ink)}header,main{width:min(1080px,calc(100% - 32px))}header{padding:34px 0 18px;background:var(--bg);border:0}h1{font-size:2rem;margin:6px 0}.subtitle{max-width:760px;color:var(--muted);font-size:.92rem;margin-bottom:0}.eyebrow{font-size:10px;color:#1769aa}.metrics{grid-template-columns:repeat(4,1fr);gap:0;margin-top:20px;border:1px solid var(--line);border-radius:9px;overflow:hidden;background:var(--surface)}.metric{min-height:58px;padding:10px 12px;border:0;border-left:1px solid var(--line);box-shadow:none;border-radius:0}.metric strong{font:500 12px/1.25 "SF Mono",Consolas,ui-monospace,monospace}.filters,.report{margin:14px 0 22px;padding:14px 0;background:transparent;border:0;border-bottom:1px solid var(--line);border-radius:0;box-shadow:none}.filters{display:grid;grid-template-columns:1fr auto;gap:12px 20px;align-items:end}.filters fieldset,.filters>p{grid-column:1/-1}.filter-fields,.report-controls{gap:7px}.filter-fields label,.report-controls label{font-size:.76rem;color:var(--muted)}fieldset{margin:0}.filters legend{font-size:11px;color:var(--muted);margin-bottom:7px}.category-options{gap:6px}.category-choice{min-height:34px;padding:5px 8px;border-color:var(--line);border-radius:7px;font-size:11px;background:#fff}.category-choice:has(:checked){border-color:#b9c7d7;background:#f8fafc}.category-choice input{width:14px;height:14px;accent-color:#1769aa}.swatch{width:8px;height:8px;border-radius:50%}.filter-fields{margin:0}.filter-fields input,button,input,select{min-height:34px;font-size:12px;border-radius:8px}.filter-fields input{width:174px}.filters button,button{background:#1769aa;border-color:#1769aa;color:#fff}.filters button:hover,button:hover{background:#115889}.day{margin:0;border:0;border-radius:0;border-bottom:1px solid var(--line);box-shadow:none;background:var(--surface);overflow:visible}.day-head{padding:18px 0 9px;border:0;background:transparent;color:var(--ink);font-weight:400}.day-head:before{display:none}.day-head h2{margin:0;font:500 16px "SF Mono",Consolas,ui-monospace,monospace}.events{padding:0}.event{grid-template-columns:58px 88px 96px 1fr;gap:10px;align-items:center;padding:11px 0;border:0;border-bottom:1px solid var(--line);box-shadow:none;background:transparent}.event:nth-child(2n),.event:hover,.event:focus-within{background:transparent;box-shadow:none}.event[data-status=true],.event[data-status=false]{margin:0;padding:11px 8px;border-left:0}.event[data-status=true]{background:var(--true)}.event[data-status=false]{background:var(--false)}.state-control{gap:8px}.state-control label{width:18px;min-width:18px;height:18px;min-height:18px;padding:0;border-radius:50%;border:2px solid currentColor;position:relative}.state-control .state{position:absolute;opacity:0}.state-control .sr-only{position:absolute;width:1px;height:1px;padding:0;margin:-1px;overflow:hidden;clip:rect(0,0,0,0);white-space:nowrap;border:0}.state-control label:has(.state:checked)::after{content:"";width:8px;height:8px;border-radius:50%;background:currentColor;position:absolute;inset:3px}.true-choice{color:#259b57}.false-choice{color:#df4760}.state-control label:focus-within{outline:2px solid #1769aa;outline-offset:3px}.event-time{padding:0;color:#0c4d81;font:500 12px "SF Mono",Consolas,ui-monospace,monospace}.chip{border:0;border-radius:999px;padding:3px 7px;font:500 11px "SF Mono",Consolas,ui-monospace,monospace}.event small{display:none}.event details summary{display:list-item;min-height:0;padding:0;color:#1769aa;font-size:12px;list-style-position:inside}.event>details{min-width:0}.event>details[open]{grid-column:4}.event>details[open] pre{width:100%;margin-top:10px}.feature{margin:10px 0;border-radius:8px;box-shadow:none}.feature>summary{padding:13px 14px}.report{margin-top:28px;display:flex;flex-wrap:wrap;gap:12px 20px;align-items:end}.report>div:first-child{flex:1 1 430px}.report h2{font-size:1.1rem}.report-controls{flex:0 1 380px;justify-content:flex-end}pre,#report-text{background:#f8fafc;color:#1f3045;border-color:#d7e1ed}#report-text{min-height:250px;font-size:11px}.empty{padding:16px;border-radius:8px}.day-count{font-size:.8rem;color:var(--muted)}
.chip{border:1px solid #d7dce3;font-size:12px;font-weight:700;line-height:1.35}.day-head{cursor:pointer;user-select:none}.day-head:before{display:block;transition:transform 120ms ease}.day-head:hover{background:#f8fafc}.event-time{margin-left:-4px;padding:2px 4px;border-radius:5px;transition:background-color 120ms ease,color 120ms ease}.event-time:hover{background:#f3f6f9;color:#0b4a78;text-decoration:none}.event-time:active{background:#eaf0f5}.event-time:focus-visible{background:#f3f6f9}
@media(max-width:720px){.metrics{grid-template-columns:repeat(2,1fr)}.metric:nth-child(even){border-left:0}.filters{grid-template-columns:1fr}.filter-fields{grid-column:1}.filter-fields input{width:100%}.event{grid-template-columns:54px 78px 1fr}.event details{grid-column:1/-1}.report{display:block}.report-controls{margin-top:12px;justify-content:flex-start}}
@media print{header{padding:16px 0}.feature{border:1px solid #ddd}}
`;

export async function renderManualReview(payload, snapshot = {}, cryptoApi = globalThis.crypto) {
  if (!payload || !payload.directions || typeof payload.directions !== "object") throw new Error("Invalid indicator payload");
  const raw = JSON.stringify(payload);
  const digest = await cryptoApi.subtle.digest("SHA-256", new TextEncoder().encode(raw));
  const hash = Array.from(new Uint8Array(digest), (byte) => byte.toString(16).padStart(2, "0")).join("");
  const records = reviewRecords(payload), days = new Map(), groups = new Map(), categories = new Map();
  const objects = new Map((snapshot.indicatorObjects || []).map((item) => [item.id, item]));
  for (const record of records) {
    record.color = reviewColor(record, snapshot, objects);
    if (!categories.has(record.category.key)) categories.set(record.category.key, { ...record.category, color: record.color, count: 0 });
    categories.get(record.category.key).count++;
    const day = record.time === "Undated" ? "Undated" : record.time.slice(0, 10);
    if (!days.has(day)) days.set(day, []);
    days.get(day).push(record);
    const group = `${record.direction} · ${collections[record.group]?.[0] || record.group}`;
    if (!groups.has(group)) groups.set(group, []);
    groups.get(group).push(record);
  }
  const count = (group, predicate = () => true) => records.filter((record) => record.group === group && predicate(record.row)).length;
  const metrics = [["Timeframe", `${payload.timeframe ?? "—"} seconds`], ["Direction", Object.keys(payload.directions).join(", ")], ["Fresh payload", snapshot.source || "Cached chart payload"], ["A", count("aZones")], ["S blue", count("sZones", (row) => row.color === "blue")], ["S red", count("sZones", (row) => row.color === "red")], ["E", count("eZones")], ["Order audit", count("orderAudit")]];
  const timeline = [...days].map(([day, rows]) => `<details class="day" open><summary class="day-head"><h2>${day}</h2><span class="day-count">${rows.length.toLocaleString()} events</span></summary><div class="events">${rows.map(eventCard).join("")}</div></details>`).join("");
  const features = [...groups].map(([group, rows]) => `<details class="feature collection"><summary><span>${escapeHtml(group)}</span><small>${rows.length.toLocaleString()} total records</small></summary>${rows.map((r) => `<div class="reference-row" data-filter="${escapeHtml(r.category.key)}" data-time="${r.time}">${escapeHtml(`${r.time} | ${r.label}`)}<details><summary>Bridge output</summary>${detail(r.row)}</details></div>`).join("")}</details>`).join("");
  const categoryOrder = Object.keys(colorSpec);
  const filterControls = [...categories.values()].sort((a, b) => (categoryOrder.indexOf(a.key) < 0 ? 99 : categoryOrder.indexOf(a.key)) - (categoryOrder.indexOf(b.key) < 0 ? 99 : categoryOrder.indexOf(b.key)))
    .map((category) => `<label class="category-choice"><input class="category-filter" type="checkbox" value="${escapeHtml(category.key)}" checked><i class="swatch" style="background:${category.color}" aria-hidden="true"></i><span>${escapeHtml(category.label)}</span><small>${category.count.toLocaleString()}</small></label>`).join("");
  return `<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Indicator Timeline Review</title><style>${styles}</style></head><body data-payload-hash="${hash}" data-review-id="${escapeHtml(snapshot.exportedAt || "standalone")}">
<a class="skip-link" href="#timeline">Skip to timeline</a><header><span class="eyebrow">MANUAL BRIDGE REVIEW · ASIA/TEHRAN</span><h1>Indicator timeline review</h1><p class="subtitle">A chronological manual comparison workspace. The timeline is the primary review surface; the full A, S, E and audit lists remain available below as reference features.</p><div class="metrics">${metrics.map(([k,v]) => `<div class="metric"><span>${k}</span><strong>${escapeHtml(v)}</strong></div>`).join("")}</div></header>
<main><section class="filters" aria-labelledby="filter-title"><div><span class="eyebrow">TIMELINE FILTER</span><h2 id="filter-title">Show a precise review window</h2></div><div class="filter-fields"><label>From<input id="from" type="datetime-local" step="1" aria-describedby="range-hint"></label><label>To<input id="to" type="datetime-local" step="1" aria-describedby="range-hint range-error"></label><button id="reset" type="button">Reset</button></div><fieldset><legend>Behavior filters</legend><div class="category-options">${filterControls}</div></fieldset><p id="range-hint"><small>Leave dates blank for the full range. Filters hide records; they never remove exported data or reviews.</small></p><p class="error" id="range-error" role="alert" hidden>From must not be later than To.</p><p id="filter-note" role="status" aria-live="polite"></p></section><section id="timeline" aria-labelledby="timeline-title"><span class="eyebrow">PRIMARY REVIEW SURFACE</span><h2 id="timeline-title">Chronological timeline</h2><p class="subtitle">Events are grouped by Tehran calendar day and ordered by time. Check only the item you have verified against the chart.</p><p class="empty" id="empty" hidden>No matching events. Select one or more behavior filters.</p>${timeline || "<p>No events in the cached payload.</p>"}</section>
<section class="report" id="review-report" aria-labelledby="report-title"><div><span class="eyebrow">AI HANDOFF</span><h2 id="report-title">Live review report</h2><p>Every selected item is written on its own line. Use the selector to export all selected items or only one status.</p><p id="storage-note"><small>Reviews are saved in this browser for this export. Download TXT to keep or share your findings.</small></p></div><div class="report-controls"><label>Include <select id="mode"><option value="all">All selected</option><option value="true">True only</option><option value="false">False only</option></select></label><button id="copy">Copy report</button><button id="download">Download TXT</button></div><textarea id="report-text" readonly aria-label="Review report"></textarea></section>
<h2>Complete record collections</h2><p><small>Collection rows follow your filters. The original payload and chart snapshot below always contain all data.</small></p>${features}<details class="feature"><summary>Original cached Bridge payload · SHA-256 ${hash}</summary><pre>${escapeHtml(raw)}</pre></details><details class="feature"><summary>Export metadata, candles, drawings and settings</summary>${detail(snapshot)}</details></main>
<script type="application/json" id="indicator-payload">${jsonScript(payload)}</script><script type="application/json" id="chart-snapshot">${jsonScript(snapshot)}</script><script>(${reviewRuntime.toString()})();</script></body></html>`;
}

export async function saveManualReview(payload, snapshot, host = window, notify = () => {}) {
  // Copy before the picker yields: a later calculation must not change this export.
  const captured = structuredClone(payload), extra = structuredClone(snapshot || {});
  const now = new Date(), filename = manualReviewFilename(now);
  extra.exportedAt = now.toISOString();
  let handle;
  if (typeof host.showSaveFilePicker === "function") {
    try {
      handle = await host.showSaveFilePicker({ suggestedName: filename, types: [{ description: "Indicator review HTML", accept: { "text/html": [".html"] } }] });
    } catch (error) {
      if (error.name === "AbortError") return "cancelled";
      if (!["SecurityError", "NotAllowedError", "NotSupportedError"].includes(error.name)) throw error;
    }
  }
  const html = await renderManualReview(captured, extra, host.crypto);
  const blob = new Blob([html], { type: "text/html;charset=utf-8" });
  if (handle) {
    const writable = await handle.createWritable();
    try { await writable.write(blob); await writable.close(); }
    catch (error) { try { await writable.abort(); } catch {} throw error; }
    return "saved";
  }
  // No server write endpoint or additional filesystem permission is needed.
  notify(`Save As is unavailable in this browser. Downloading ${filename} to its download location; enable 'Ask where to save each file' in browser settings to choose a path.`);
  const url = host.URL.createObjectURL(blob), a = host.document.createElement("a");
  a.href = url; a.download = filename;
  host.document.body.append(a); a.click(); a.remove();
  host.setTimeout(() => host.URL.revokeObjectURL(url), 1000);
  return "downloaded";
}
