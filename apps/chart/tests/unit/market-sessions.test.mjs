import assert from "node:assert/strict";
import test from "node:test";
import { marketCountdown, marketSession } from "../../src/features/market-sessions.js";

const gold = { broker: "FOREX.COM", symbol: "XAU/USD" };
const oil = { broker: "FXCM", symbol: "USOIL" };

function expectTransition(instrument, now, state, next) {
  const result = marketSession(instrument, Date.parse(now));
  assert.equal(result.state, state);
  assert.equal(result.nextAt, Date.parse(next));
}

test("gold and oil have independent Friday close and Sunday reopen boundaries", () => {
  const friday = "2026-11-20T21:45:00Z";
  expectTransition(gold, friday, "open", "2026-11-20T22:00:00Z");
  expectTransition(oil, friday, "closed", "2026-11-22T23:00:00Z");
  expectTransition(oil, "2026-11-20T21:44:59Z", "open", friday);
  expectTransition(gold, "2026-11-22T22:59:59Z", "closed", "2026-11-22T23:00:00Z");
  expectTransition(gold, "2026-11-22T23:00:00Z", "open", "2026-11-23T22:00:00Z");
});

test("New York DST moves UTC trading hours at spring and autumn boundaries", () => {
  expectTransition(gold, "2026-03-07T12:00:00Z", "closed", "2026-03-08T22:00:00Z");
  expectTransition(gold, "2026-10-31T12:00:00Z", "closed", "2026-11-01T23:00:00Z");
  expectTransition(oil, "2026-03-09T21:00:00Z", "closed", "2026-03-09T22:00:00Z");
  expectTransition(oil, "2026-11-02T22:00:00Z", "closed", "2026-11-02T23:00:00Z");
  expectTransition(gold, "2027-03-13T12:00:00Z", "closed", "2027-03-14T22:00:00Z");
  expectTransition(gold, "2027-11-07T22:59:59Z", "closed", "2027-11-07T23:00:00Z");
});

test("published 2026 Thanksgiving breaks override both commodity profiles", () => {
  for (const profile of [gold, oil]) {
    expectTransition(profile, "2026-11-26T19:29:59Z", "open", "2026-11-26T19:30:00Z");
    expectTransition(profile, "2026-11-26T19:30:00Z", "closed", "2026-11-26T23:00:00Z");
    expectTransition(profile, "2026-11-26T23:00:00Z", "open", "2026-11-27T19:45:00Z");
    expectTransition(profile, "2026-11-27T19:45:00Z", "closed", "2026-11-29T23:00:00Z");
  }
});

test("a holiday without a published override has no estimated transition", () => {
  expectTransition(oil, "2026-12-23T21:59:59Z", "open", "2026-12-23T22:00:00Z");
  const breakBefore = marketSession(oil, Date.parse("2026-12-23T22:00:00Z"));
  assert.equal(breakBefore.state, "closed");
  assert.equal(breakBefore.reason, "holiday");
  assert.equal(breakBefore.nextAt, undefined);
  for (const time of ["2026-12-23T23:00:00Z", "2026-12-24T17:00:00Z", "2027-03-26T17:00:00Z"]) {
    const result = marketSession(oil, Date.parse(time));
    assert.equal(result.state, "unknown");
    assert.equal(result.reason, "holiday");
  }
  const weekendBefore = marketSession(gold, Date.parse("2026-05-24T21:59:59Z"));
  assert.equal(weekendBefore.state, "closed");
  assert.equal(weekendBefore.reason, "holiday");
  assert.equal(weekendBefore.nextAt, undefined);
  expectTransition(gold, "2026-12-26T17:00:00Z", "closed", "2026-12-27T23:00:00Z");
});

test("gold applies verified exchange holidays and skips closed sessions", () => {
  expectTransition(gold, "2026-12-24T18:44:59Z", "open", "2026-12-24T18:45:00Z");
  expectTransition(gold, "2026-12-24T18:45:00Z", "closed", "2026-12-27T23:00:00Z");
  expectTransition(gold, "2026-12-25T15:00:00Z", "closed", "2026-12-27T23:00:00Z");
  expectTransition(gold, "2026-12-31T21:59:59Z", "open", "2026-12-31T22:00:00Z");
  expectTransition(gold, "2026-12-31T22:00:00Z", "closed", "2027-01-03T23:00:00Z");
  expectTransition(gold, "2027-01-01T15:00:00Z", "closed", "2027-01-03T23:00:00Z");
  expectTransition(gold, "2027-03-25T20:59:59Z", "open", "2027-03-25T21:00:00Z");
  expectTransition(gold, "2027-03-25T21:00:00Z", "closed", "2027-03-28T22:00:00Z");
});

test("spot Bitcoin is continuous while FXCM Bitcoin follows CFD hours", () => {
  const saturday = "2026-11-28T19:45:00Z";
  const coinbase = marketSession({ symbol: "Coinbase:BTC-USD" }, Date.parse(saturday));
  const binance = marketSession({ broker: "Binance", symbol: "BTCUSDT" }, Date.parse(saturday));
  for (const spot of [coinbase, binance]) {
    assert.equal(spot.state, "open");
    assert.equal(spot.continuous, true);
    assert.equal(spot.nextAt, undefined);
  }
  expectTransition({ broker: "FXCM", symbol: "BTCUSD" }, saturday, "closed", "2026-11-29T22:00:00Z");
  expectTransition({ broker: "FXCM", symbol: "BTCUSD" }, "2026-11-26T19:30:00Z", "open", "2026-11-27T21:55:00Z");
  assert.equal(marketSession({ broker: "OTHER", symbol: "BTCUSD" }).state, "unknown");
});

test("the countdown rounds up to the next second and preserves multi-day waits", () => {
  assert.equal(marketCountdown(2000, 1999), "00:00:01");
  assert.equal(marketCountdown(2000, 2000), "00:00:00");
  assert.equal(marketCountdown(176_400_000, 0), "2d 01:00:00");
});
