function numeric(value, fallback = 0) {
  const number = Number(value);
  return Number.isFinite(number) ? number : fallback;
}

export function setAnchoredPopoverOpen({
  menu,
  trigger,
  open,
  viewport = { width: globalThis.innerWidth, height: globalThis.innerHeight },
  gap = 6,
  margin = 8,
}) {
  if (!menu || !trigger) throw new TypeError("An anchored popup requires a menu and trigger");
  menu.classList.toggle("hidden", !open);
  trigger.setAttribute("aria-expanded", String(open));
  if (!open) return false;

  menu.style.position = "fixed";
  const anchor = trigger.getBoundingClientRect();
  const popover = menu.getBoundingClientRect();
  const width = numeric(viewport?.width, globalThis.innerWidth);
  const height = numeric(viewport?.height, globalThis.innerHeight);
  const popoverWidth = numeric(popover.width);
  const popoverHeight = numeric(popover.height);
  const safeMargin = Math.max(0, numeric(margin, 8));
  const safeGap = Math.max(0, numeric(gap, 6));
  const maxLeft = Math.max(safeMargin, width - popoverWidth - safeMargin);
  const left = Math.min(Math.max(numeric(anchor.left), safeMargin), maxLeft);
  const below = numeric(anchor.bottom) + safeGap;
  const above = numeric(anchor.top) - safeGap - popoverHeight;
  const top = below + popoverHeight <= height - safeMargin
    ? below
    : Math.max(safeMargin, above);

  menu.style.left = `${Math.round(left)}px`;
  menu.style.top = `${Math.round(top)}px`;
  return open;
}
