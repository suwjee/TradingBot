import { setAnchoredPopoverOpen } from "../ui/popover.js";
import { formatSymbolWithBroker } from "../ui/symbol-format.js";
import { marketCountdown, marketSession } from "./market-sessions.js";
import { formatTehranMetadataTime } from "./raw-file-contract.js";
import "../styles/market-clock.css";

const transitionClock = new Intl.DateTimeFormat("en-GB", {
  timeZone: "Asia/Tehran",
  weekday: "short",
  day: "numeric",
  month: "short",
  hour: "2-digit",
  minute: "2-digit",
  second: "2-digit",
  hourCycle: "h23",
  timeZoneName: "short",
});

export function mountMarketClock({ trigger, getInstrument }) {
  const clock = trigger.querySelector("time");
  trigger.title = "Tehran time · Market hours";
  trigger.insertAdjacentHTML("afterend", `
    <section class="market-clock-popup hidden" id="marketClockPopup" popover="manual" aria-labelledby="marketClockTitle">
      <header>
        <div>
          <strong id="marketClockTitle">Market hours</strong>
          <small data-market-instrument></small>
        </div>
        <span class="market-clock-status" data-market-status aria-live="polite"></span>
      </header>
      <div class="market-clock-transition">
        <span data-market-transition></span>
        <b data-market-remaining></b>
      </div>
      <footer>
        <time data-market-next></time>
        <a data-market-source target="_blank" rel="noopener noreferrer">Source</a>
      </footer>
    </section>`);
  const menu = trigger.nextElementSibling;
  const instrumentLabel = menu.querySelector("[data-market-instrument]");
  const status = menu.querySelector("[data-market-status]");
  const transition = menu.querySelector("[data-market-transition]");
  const remaining = menu.querySelector("[data-market-remaining]");
  const next = menu.querySelector("[data-market-next]");
  const source = menu.querySelector("[data-market-source]");
  let open = false;
  let pinned = false;
  let closeTimer;
  let currentInstrument;
  let currentSession;
  let refreshAt = 0;
  let lastObservedAt = -Infinity;

  function refreshMenu(now) {
    const instrument = getInstrument();
    const instrumentName = instrument ? formatSymbolWithBroker(instrument) : "No symbol selected";
    if (instrument !== currentInstrument || now >= refreshAt || now < lastObservedAt) {
      currentInstrument = instrument;
      currentSession = marketSession(instrument, now);
      refreshAt = Math.min(now + 60_000, currentSession.nextAt ?? Infinity, currentSession.validUntil ?? Infinity);
    }
    lastObservedAt = now;
    const session = currentSession;
    const statusText = { open: "Open", closed: "Closed", unknown: "Unavailable" }[session.state];
    instrumentLabel.textContent = session.specialHours ? `${instrumentName} · Holiday hours` : instrumentName;
    status.dataset.state = session.state;
    trigger.dataset.marketState = session.state;
    if (status.textContent !== statusText) status.textContent = statusText;
    if (session.nextAt) {
      transition.textContent = session.state === "open" ? "Closes in" : "Opens in";
      remaining.textContent = marketCountdown(session.nextAt, now);
      next.dateTime = new Date(session.nextAt).toISOString();
      next.textContent = transitionClock.format(session.nextAt);
    } else {
      transition.textContent = session.continuous ? "24/7 trading"
        : session.reason === "holiday" ? "Holiday hours unavailable"
        : instrument ? "Schedule unavailable for this instrument" : "Select a symbol to see its session";
      remaining.textContent = "";
      next.removeAttribute("datetime");
      next.textContent = session.source ? "Scheduled hours" : "";
    }
    source.hidden = !session.source;
    menu.querySelector("footer").hidden = !session.source;
    if (session.source) source.href = session.source;
  }

  function tick() {
    const now = Date.now();
    const timestamp = new Date(now);
    clock.dateTime = timestamp.toISOString();
    clock.textContent = formatTehranMetadataTime(Math.floor(now / 1000)).slice(0, 19);
    refreshMenu(now);
  }

  function setOpen(nextOpen) {
    clearTimeout(closeTimer);
    if (nextOpen) {
      refreshMenu(Date.now());
      if (!open) {
        menu.classList.remove("hidden");
        menu.showPopover?.();
      }
    } else if (open) menu.hidePopover?.();
    open = setAnchoredPopoverOpen({ menu, trigger, open: nextOpen });
    if (!open) pinned = false;
  }

  function closeWhenOutside() {
    clearTimeout(closeTimer);
    closeTimer = setTimeout(() => {
      if (!pinned && !trigger.matches(":hover, :focus-visible") && !menu.matches(":hover, :focus-within")) {
        setOpen(false);
      }
    }, 150);
  }

  function includes(target) {
    return trigger.contains(target) || menu.contains(target);
  }

  trigger.addEventListener("pointerenter", event => {
    if (event.pointerType === "mouse" || event.pointerType === "pen") setOpen(true);
  });
  trigger.addEventListener("pointerleave", closeWhenOutside);
  trigger.addEventListener("focusin", () => {
    if (trigger.matches(":focus-visible")) setOpen(true);
  });
  trigger.addEventListener("focusout", event => {
    if (!includes(event.relatedTarget)) closeWhenOutside();
  });
  trigger.addEventListener("click", () => {
    if (pinned) {
      setOpen(false);
    } else {
      pinned = true;
      setOpen(true);
    }
  });
  menu.addEventListener("pointerenter", () => clearTimeout(closeTimer));
  menu.addEventListener("pointerleave", closeWhenOutside);
  menu.addEventListener("focusout", event => {
    if (!includes(event.relatedTarget)) closeWhenOutside();
  });
  document.addEventListener("pointerdown", event => {
    if (open && !includes(event.target)) setOpen(false);
  });
  document.addEventListener("keydown", event => {
    if (!open || event.key !== "Escape") return;
    if (menu.contains(document.activeElement)) trigger.focus();
    setOpen(false);
  });
  window.addEventListener("resize", () => {
    if (open) setOpen(trigger.getClientRects().length > 0);
  });
  document.addEventListener("fullscreenchange", () => setOpen(false));
  document.addEventListener("visibilitychange", tick);
  tick();
  window.setInterval(tick, 1000);
}
