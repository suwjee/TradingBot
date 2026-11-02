// Presentation-only event and scheduling ownership for chart viewport updates.
// This module must not decide candle/trading semantics or modify RAW inputs.
export function createViewportScheduler({
  hasData, isPointerPanning, getVisibleRange, render,
  setTimeoutFn = setTimeout,
  clearTimeoutFn = clearTimeout,
  requestAnimationFrameFn = requestAnimationFrame,
}) {
  let frame = 0;
  let timer = 0;
  function schedule(delay = 140) {
    if (!hasData()) return;
    clearTimeoutFn(timer);
    timer = setTimeoutFn(() => {
      if (frame) return;
      frame = requestAnimationFrameFn(() => {
        frame = 0;
        // Do not replace chart series while the pointer is dragging.
        if (isPointerPanning()) return;
        render(getVisibleRange(), { preserveRange: true });
      });
    }, delay);
  }
  return schedule;
}

export function bindViewportEvents({
  timeScale, shell, invalidateAnchors, scheduleDraw, scheduleViewport, setPointerPanning,
}) {
  const onLogicalRange = () => {
    invalidateAnchors();
    scheduleDraw();
    scheduleViewport();
  };
  const onTimeRange = () => {
    invalidateAnchors();
    scheduleDraw();
    scheduleViewport();
  };
  const onSize = () => {
    invalidateAnchors();
    scheduleDraw();
    scheduleViewport(0);
  };
  const onPointerMove = (event) => {
    if (event.buttons) scheduleDraw();
  };
  const onPointerDown = (event) => {
    if (event.button === 0) setPointerPanning(true);
  };
  const onPointerUp = () => {
    setPointerPanning(false);
    scheduleDraw();
    scheduleViewport(90);
  };
  const onPointerCancel = () => {
    setPointerPanning(false);
    scheduleViewport(90);
  };

  timeScale.subscribeVisibleLogicalRangeChange(onLogicalRange);
  timeScale.subscribeVisibleTimeRangeChange(onTimeRange);
  timeScale.subscribeSizeChange(onSize);
  shell.addEventListener("pointermove", onPointerMove, { passive: true });
  shell.addEventListener("pointerdown", onPointerDown, { passive: true });
  shell.addEventListener("pointerup", onPointerUp, { passive: true });
  shell.addEventListener("pointercancel", onPointerCancel, { passive: true });

  // Optional owner cleanup for future explicit teardown. No new lifecycle
  // cleanup is triggered by binding these handlers.
  return () => {
    timeScale.unsubscribeVisibleLogicalRangeChange(onLogicalRange);
    timeScale.unsubscribeVisibleTimeRangeChange(onTimeRange);
    timeScale.unsubscribeSizeChange(onSize);
    shell.removeEventListener("pointermove", onPointerMove);
    shell.removeEventListener("pointerdown", onPointerDown);
    shell.removeEventListener("pointerup", onPointerUp);
    shell.removeEventListener("pointercancel", onPointerCancel);
  };
}
