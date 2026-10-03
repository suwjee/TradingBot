import test from "node:test";
import assert from "node:assert/strict";

import { createCalculationCoordinator, parseEngineConcurrency } from "../../server/calculation-coordinator.js";

function deferred() {
  let resolve;
  let reject;
  const promise = new Promise((yes, no) => { resolve = yes; reject = no; });
  return { promise, resolve, reject };
}

test("Engine concurrency configuration has a bounded positive default", () => {
  assert.equal(parseEngineConcurrency(undefined), 1);
  assert.equal(parseEngineConcurrency("2"), 2);
  assert.equal(parseEngineConcurrency("1"), 1);
  assert.equal(parseEngineConcurrency("8"), 8);
  for (const value of ["0", "-1", "1.5", "abc", "9", "", " 2 ", "Infinity"]) {
    assert.throws(() => parseEngineConcurrency(value), /concurrency/i);
  }
});

test("maximum configured Engine concurrency starts eight jobs and queues the ninth", async () => {
  const coordinator = createCalculationCoordinator({ maxActive: 8 });
  const gates = Array.from({ length: 9 }, deferred);
  const starts = [];
  const work = gates.map((gate, index) => coordinator.run(`job-${index}`, () => {
    starts.push(index);
    return gate.promise;
  }));
  assert.deepEqual(starts, [0, 1, 2, 3, 4, 5, 6, 7]);
  assert.deepEqual(coordinator.stats(), { active: 8, pending: 1, inFlight: 9 });
  gates[0].resolve("first");
  assert.equal(await work[0], "first");
  assert.deepEqual(starts, [0, 1, 2, 3, 4, 5, 6, 7, 8]);
  for (const gate of gates.slice(1)) gate.resolve("done");
  await Promise.all(work);
  assert.deepEqual(coordinator.stats(), { active: 0, pending: 0, inFlight: 0 });
});

test("distinct calculations execute FIFO within the active Engine limit", async () => {
  const coordinator = createCalculationCoordinator({ maxActive: 1 });
  const gates = [deferred(), deferred(), deferred()];
  const starts = [];
  const work = gates.map((gate, index) => coordinator.run(`key-${index}`, async () => {
    starts.push(index);
    return gate.promise;
  }));
  assert.deepEqual(starts, [0]);
  assert.deepEqual(coordinator.stats(), { active: 1, pending: 2, inFlight: 3 });
  gates[0].resolve("first");
  assert.equal(await work[0], "first");
  await Promise.resolve();
  assert.deepEqual(starts, [0, 1]);
  gates[1].resolve("second");
  assert.equal(await work[1], "second");
  await Promise.resolve();
  assert.deepEqual(starts, [0, 1, 2]);
  gates[2].resolve("third");
  assert.equal(await work[2], "third");
  assert.deepEqual(coordinator.stats(), { active: 0, pending: 0, inFlight: 0 });
});

test("identical in-flight calculations share one execution and replay progress", async () => {
  const coordinator = createCalculationCoordinator({ maxActive: 1 });
  const gate = deferred();
  const firstEvents = [];
  const secondEvents = [];
  let executions = 0;
  const first = coordinator.run("same-cache-key", async (publish) => {
    executions++;
    publish({ status: "started", label: "Engine" });
    return gate.promise;
  }, (event) => firstEvents.push(event));
  const second = coordinator.run("same-cache-key", () => {
    throw new Error("Duplicate work must not execute.");
  }, (event) => secondEvents.push(event));
  assert.equal(executions, 1);
  assert.deepEqual(firstEvents, [{ status: "started", label: "Engine" }]);
  assert.deepEqual(secondEvents, firstEvents);
  gate.resolve("same serialized result");
  assert.deepEqual(await Promise.all([first, second]), ["same serialized result", "same serialized result"]);
  assert.equal(coordinator.stats().inFlight, 0);
});

test("failed shared calculation releases its slot and can be retried", async () => {
  const coordinator = createCalculationCoordinator({ maxActive: 1 });
  const gate = deferred();
  let attempts = 0;
  const first = coordinator.run("key", async () => { attempts++; return gate.promise; });
  const second = coordinator.run("key", () => { throw new Error("Duplicate execution"); });
  gate.reject(new Error("child failed"));
  const results = await Promise.allSettled([first, second]);
  assert.deepEqual(results.map((item) => item.reason?.message), ["child failed", "child failed"]);
  assert.deepEqual(coordinator.stats(), { active: 0, pending: 0, inFlight: 0 });
  assert.equal(await coordinator.run("key", async () => { attempts++; return "retry"; }), "retry");
  assert.equal(attempts, 2);
});

test("closing aborts owned active work and rejects queued work", async () => {
  const coordinator = createCalculationCoordinator({ maxActive: 1 });
  const active = coordinator.run("active", (_publish, signal) => new Promise((_resolve, reject) => {
    signal.addEventListener("abort", () => reject(new Error("child killed")), { once: true });
  }));
  const queued = coordinator.run("queued", () => { throw new Error("Queued work must not start"); });
  coordinator.close();
  coordinator.close();
  const results = await Promise.allSettled([active, queued]);
  assert.deepEqual(results.map((item) => item.status), ["rejected", "rejected"]);
  assert.equal(results[0].reason.message, "child killed");
  assert.match(results[1].reason.message, /shutting down/i);
  assert.deepEqual(coordinator.stats(), { active: 0, pending: 0, inFlight: 0 });
  await assert.rejects(coordinator.run("later", async () => "unreachable"), /shutting down/i);
});

test("a rejection without an Error still releases the slot and rejects callers", async () => {
  const coordinator = createCalculationCoordinator({ maxActive: 1 });
  const first = coordinator.run("first", () => Promise.reject(undefined));
  const second = coordinator.run("second", async () => "second result");
  const outcome = await Promise.allSettled([first, second]);
  assert.equal(outcome[0].status, "rejected");
  assert.equal(outcome[1].status, "fulfilled");
  assert.equal(outcome[1].value, "second result");
  assert.deepEqual(coordinator.stats(), { active: 0, pending: 0, inFlight: 0 });
});
