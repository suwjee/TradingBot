import test from "node:test";
import assert from "node:assert/strict";

import { setAnchoredPopoverOpen } from "../src/ui/popover.js";

function classes(...initial) {
  const values = new Set(initial);
  return {
    contains: (value) => values.has(value),
    toggle(value, force) {
      if (force) values.add(value);
      else values.delete(value);
    },
  };
}

test("opening an anchored popup escapes clipped header ancestors and stays inside the viewport", () => {
  const attributes = new Map();
  const trigger = {
    getBoundingClientRect: () => ({ left: 970, top: 8, right: 1002, bottom: 40, width: 32, height: 32 }),
    setAttribute: (name, value) => attributes.set(name, value),
  };
  const menu = {
    classList: classes("hidden"),
    style: {},
    getBoundingClientRect: () => ({ width: 252, height: 400 }),
  };

  setAnchoredPopoverOpen({ menu, trigger, open: true, viewport: { width: 1024, height: 768 } });

  assert.equal(menu.classList.contains("hidden"), false);
  assert.equal(attributes.get("aria-expanded"), "true");
  assert.equal(menu.style.position, "fixed");
  assert.equal(menu.style.left, "764px");
  assert.equal(menu.style.top, "46px");
});

test("an anchored popup flips above its trigger and close restores disclosure state", () => {
  const attributes = new Map();
  const trigger = {
    getBoundingClientRect: () => ({ left: 20, top: 700, right: 52, bottom: 732, width: 32, height: 32 }),
    setAttribute: (name, value) => attributes.set(name, value),
  };
  const menu = {
    classList: classes("hidden"),
    style: {},
    getBoundingClientRect: () => ({ width: 252, height: 300 }),
  };

  setAnchoredPopoverOpen({ menu, trigger, open: true, viewport: { width: 1024, height: 768 } });
  assert.equal(menu.style.top, "394px");

  setAnchoredPopoverOpen({ menu, trigger, open: false, viewport: { width: 1024, height: 768 } });
  assert.equal(menu.classList.contains("hidden"), true);
  assert.equal(attributes.get("aria-expanded"), "false");
});
