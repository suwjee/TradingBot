import test from "node:test";
import assert from "node:assert/strict";

import { createProgressChannels } from "../../server/progress-channels.js";

test("progress replays bounded history and releases a finished disconnected channel", () => {
  const channels = createProgressChannels();
  for (let index = 0; index < 125; index++) channels.publish("request", { status: "started", label: String(index) });
  const messages = [];
  const client = { write: (message) => messages.push(message), end() {} };
  const detach = channels.attach("request", client);
  assert.equal(messages.length, 120);
  assert.match(messages[0], /"label":"5"/);
  channels.publish("request", { status: "finished", label: "Response ready" });
  assert.equal(messages.length, 121);
  detach();
  assert.equal(channels.stats().channels, 0);
});

test("unobserved terminal and active progress remain replayable", () => {
  const channels = createProgressChannels();
  channels.publish("finished", { status: "finished", label: "done" });
  channels.publish("failed", { status: "failed", label: "child failed" });
  channels.publish("active", { status: "started", label: "Engine" });
  assert.deepEqual(channels.stats(), { channels: 3, clients: 0 });
  channels.close();
  assert.deepEqual(channels.stats(), { channels: 0, clients: 0 });
});

test("closing progress channels closes owned SSE clients", () => {
  const channels = createProgressChannels();
  let ended = 0;
  channels.attach("request", { write() {}, end() { ended++; } });
  channels.publish("request", { status: "finished", label: "done" });
  channels.close();
  assert.equal(ended, 1);
  assert.deepEqual(channels.stats(), { channels: 0, clients: 0 });
});

test("reused progress identity keeps established replay order", () => {
  const channels = createProgressChannels();
  channels.publish("request", { status: "finished", label: "old" });
  channels.publish("request", { status: "started", label: "new" });
  const messages = [];
  channels.attach("request", { write: (message) => messages.push(message), end() {} });
  assert.match(messages[0], /"label":"old"/);
  assert.match(messages[1], /"label":"new"/);
  assert.equal(channels.stats().channels, 1);
  channels.close();
});

test("a broken SSE response cannot prevent shutdown", () => {
  const channels = createProgressChannels();
  channels.attach("request", { write() {}, end() { throw new Error("client gone"); } });
  channels.publish("request", { status: "failed", label: "error" });
  assert.doesNotThrow(() => channels.close());
  assert.equal(channels.stats().channels, 0);
});

test("disconnecting an unused progress subscription releases its channel", () => {
  const channels = createProgressChannels();
  const detach = channels.attach("unused-request", { write() {}, end() {} });
  assert.deepEqual(channels.stats(), { channels: 1, clients: 1 });
  detach();
  assert.deepEqual(channels.stats(), { channels: 0, clients: 0 });
});

test("late subscribers receive terminal progress that had no observer", () => {
  const channels = createProgressChannels();
  channels.publish("finished-request", { status: "finished", label: "Response ready" });
  channels.publish("failed-request", { status: "failed", label: "Engine failed" });
  const finished = [];
  const failed = [];
  channels.attach("finished-request", { write: (message) => finished.push(message), end() {} });
  channels.attach("failed-request", { write: (message) => failed.push(message), end() {} });
  assert.match(finished[0], /"status":"finished"/);
  assert.match(failed[0], /"status":"failed"/);
});

test("finished progress is removed when its last observer disconnects", () => {
  const channels = createProgressChannels();
  const detach = channels.attach("request", { write() {}, end() {} });
  channels.publish("request", { status: "finished", label: "Response ready" });
  detach();
  assert.deepEqual(channels.stats(), { channels: 0, clients: 0 });
});

test("abandoned progress is released at terminal events without losing bounded late replay", () => {
  const channels = createProgressChannels({ maxIdleChannels: 3 });
  const detach = channels.attach("abandoned", { write() {}, end() {} });
  channels.publish("abandoned", { status: "started", label: "Engine" });
  detach();
  channels.publish("abandoned", { status: "failed", label: "Engine failed" });
  assert.deepEqual(channels.stats(), { channels: 0, clients: 0 });
  for (let index = 0; index < 5; index++) channels.publish(String(index), { status: "finished", label: String(index) });
  assert.deepEqual(channels.stats(), { channels: 3, clients: 0 });
  const replay = [];
  channels.attach("4", { write: message => replay.push(message), end() {} });
  assert.match(replay[0], /"label":"4"/);
  channels.close();
});

test("a late subscriber replays cancelled progress then reaches the end of the stream", () => {
  const channels = createProgressChannels();
  channels.publish("late-request", { status: "started", label: "Engine" });
  channels.cancel("late-request", { status: "failed", label: "Calculation cancelled" });
  const messages = [];
  let ended = false;
  const detach = channels.attach("late-request", {
    write: message => messages.push(message),
    end() { ended = true; },
  });
  assert.match(messages[0], /"status":"started"/);
  assert.match(messages[1], /"label":"Calculation cancelled"/);
  assert.equal(ended, true);
  assert.deepEqual(channels.stats(), { channels: 0, clients: 0 });
  assert.equal(channels.shouldStopReconnect("late-request"), true);
  detach();
});

test("the reconnect stop marker is bounded and clears when a request ID starts new work", () => {
  const channels = createProgressChannels({ maxIdleChannels: 2 });
  const event = { status: "failed", label: "Calculation cancelled" };
  for (const id of ["old", "second", "last"]) {
    channels.attach(id, { write() {}, end() {} });
    channels.cancel(id, event);
  }
  assert.equal(channels.shouldStopReconnect("old"), false);
  assert.equal(channels.shouldStopReconnect("second"), true);
  assert.equal(channels.shouldStopReconnect("last"), true);
  channels.publish("last", { status: "started", label: "Retry" });
  assert.equal(channels.shouldStopReconnect("last"), false);
  const messages = [];
  const detach = channels.attach("last", { write: value => messages.push(value), end() {} });
  assert.match(messages[0], /"label":"Retry"/);
  assert.equal(channels.stats().clients, 1);
  detach();
});
