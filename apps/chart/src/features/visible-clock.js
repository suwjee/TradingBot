/**
 * Update a UI-only clock while the page is visible.
 *
 * Timer ownership is explicit so hidden work stops and returning to a visible
 * tab refreshes the display immediately, before the next 1-second tick.
 */
export function startVisibleClock({
  document: page,
  tick,
  intervalMs = 1000,
  setIntervalFn = setInterval,
  clearIntervalFn = clearInterval,
}) {
  let intervalId = null;

  function syncVisibility() {
    if (page.visibilityState !== "visible") {
      if (intervalId !== null) clearIntervalFn(intervalId);
      intervalId = null;
      return;
    }
    tick();
    if (intervalId === null) intervalId = setIntervalFn(tick, intervalMs);
  }

  page.addEventListener("visibilitychange", syncVisibility);
  syncVisibility();

  return () => {
    page.removeEventListener("visibilitychange", syncVisibility);
    if (intervalId !== null) clearIntervalFn(intervalId);
    intervalId = null;
  };
}
