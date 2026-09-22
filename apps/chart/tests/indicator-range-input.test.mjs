import test from "node:test";
import assert from "node:assert/strict";
import { spawn } from "node:child_process";
import net from "node:net";
import path from "node:path";
import { fileURLToPath } from "node:url";

import {
  prepareIndicatorRangeInput,
  runIndicatorRangeCalculation,
  withIndicatorRangePipe,
} from "../server/indicator-range-input.js";

function candles(from = 60, to = 185, step = 5) {
  const rows = [];
  for (let time = from; time <= to; time += step) {
    rows.push({ time, open: time, high: time + 2, low: time - 1, close: time + 1 });
  }
  return rows;
}

function readPipeWithPython(pipePath) {
  const python = process.env.TRADINGBOT_PYTHON || "python";
  return new Promise((resolve, reject) => {
    const child = spawn(python, [
      "-c",
      "import sys; from pathlib import Path; sys.stdout.buffer.write(Path(sys.argv[1]).read_bytes())",
      pipePath,
    ], { windowsHide: true });
    let stdout = "";
    let stderr = "";
    child.stdout.setEncoding("utf8");
    child.stderr.setEncoding("utf8");
    child.stdout.on("data", (part) => { stdout += part; });
    child.stderr.on("data", (part) => { stderr += part; });
    child.on("error", reject);
    child.on("close", (code) => {
      if (code === 0) resolve(stdout);
      else reject(new Error(stderr || `Python exited with ${code}`));
    });
  });
}

function runActualBridge(inputPath, { fromTime, toTime }, timeframe = 5) {
  const python = process.env.TRADINGBOT_PYTHON || "python";
  const chartRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
  const workspaceRoot = path.resolve(chartRoot, "..", "..");
  const pipelineRoot = path.join(workspaceRoot, "engine", "pipeline");
  return new Promise((resolve, reject) => {
    const child = spawn(python, [
      path.join(workspaceRoot, "engine", "bridge", "trading_pipeline.py"),
      "--engine", path.join(pipelineRoot, "reaction_engine.py"),
      "--blue-engine", path.join(pipelineRoot, "blue_line_detector.py"),
      "--a-engine", path.join(pipelineRoot, "a_zone_detector.py"),
      "--s-engine", path.join(pipelineRoot, "s_zone_detector.py"),
      "--e-engine", path.join(pipelineRoot, "e_zone_detector.py"),
      "--stopall-engine", path.join(pipelineRoot, "lifecycle_engine.py"),
      "--data", inputPath,
      "--timeframe", String(timeframe),
      "--from-time", String(fromTime),
      "--to-time", String(toTime),
      "--direction", "bullish",
      "--blue-lines", "enabled",
      "--a-zones", "enabled",
      "--s-zones", "enabled",
    ], { windowsHide: true });
    let stdout = "";
    let stderr = "";
    child.stdout.setEncoding("utf8");
    child.stderr.setEncoding("utf8");
    child.stdout.on("data", (part) => { stdout += part; });
    child.stderr.on("data", (part) => { stderr += part; });
    child.on("error", reject);
    child.on("close", (code) => {
      if (code === 0) resolve(JSON.parse(stdout));
      else reject(new Error(stderr || stdout || `Bridge exited with ${code}`));
    });
  });
}

test("partial indicator range includes every RAW row in both selected chart candles", () => {
  const prepared = prepareIndicatorRangeInput(candles(), {
    from: 60,
    to: 120,
    chartTimeframeSeconds: 60,
  });

  assert.equal(prepared.usesCompleteSource, false);
  assert.deepEqual(prepared.rows.map((row) => row.time), [
    60, 65, 70, 75, 80, 85, 90, 95, 100, 105, 110, 115,
    120, 125, 130, 135, 140, 145, 150, 155, 160, 165, 170, 175,
  ]);
});

test("single-candle indicator range retains the complete selected chart candle", () => {
  const prepared = prepareIndicatorRangeInput(candles(), {
    from: 120,
    to: 120,
    chartTimeframeSeconds: 60,
  });

  assert.equal(prepared.usesCompleteSource, false);
  assert.deepEqual(prepared.rows.map((row) => row.time), [
    120, 125, 130, 135, 140, 145, 150, 155, 160, 165, 170, 175,
  ]);
});

test("full indicator range keeps the original RAW source path eligible", () => {
  const source = candles();
  const prepared = prepareIndicatorRangeInput(source, {
    from: 60,
    to: 180,
    chartTimeframeSeconds: 60,
  });

  assert.equal(prepared.usesCompleteSource, true);
  assert.equal(prepared.rows, source);
});

test("indicator range rejects endpoints that are not real chart-candle buckets", () => {
  assert.throws(
    () => prepareIndicatorRangeInput(candles(), {
      from: 65,
      to: 120,
      chartTimeframeSeconds: 60,
    }),
    /chart-candle boundaries/i,
  );
});

test("Windows range pipe gives Python the selected JSON without creating a data file", {
  skip: process.platform !== "win32",
}, async () => {
  const rows = candles(120, 175);
  let pipePath = null;
  const payload = await withIndicatorRangePipe(rows, async (nextPipePath) => {
    pipePath = nextPipePath;
    assert.match(pipePath, /^\\\\\.\\pipe\\tradingbot-indicator-range-/i);
    return readPipeWithPython(pipePath);
  });

  assert.deepEqual(JSON.parse(payload), rows);
  assert.equal(pipePath.startsWith("\\\\.\\pipe\\"), true);
});

test("full-range calculation sends the original RAW path to the unchanged bridge runner", async () => {
  const source = candles();
  const originalPath = "X:\\TradingBot\\data\\raw\\source.json";
  let preparation = null;
  const observed = await runIndicatorRangeCalculation({
    rows: source,
    sourcePath: originalPath,
    from: 60,
    to: 180,
    chartTimeframeSeconds: 60,
    onPrepared: (prepared) => { preparation = prepared; },
    run: async (inputPath) => inputPath,
  });

  assert.equal(observed, originalPath);
  assert.equal(preparation.usesCompleteSource, true);
  assert.equal(preparation.rowCount, source.length);
});

test("partial-range calculation streams only selected rows to the unchanged bridge runner", {
  skip: process.platform !== "win32",
}, async () => {
  const payload = await runIndicatorRangeCalculation({
    rows: candles(),
    sourcePath: "X:\\TradingBot\\data\\raw\\source.json",
    from: 120,
    to: 120,
    chartTimeframeSeconds: 60,
    run: readPipeWithPython,
  });

  assert.deepEqual(JSON.parse(payload).map((row) => row.time), [
    120, 125, 130, 135, 140, 145, 150, 155, 160, 165, 170, 175,
  ]);
});

test("finer analysis timeframe remains visible through the end of the selected to candle", {
  skip: process.platform !== "win32",
}, async () => {
  const payload = await runIndicatorRangeCalculation({
    rows: candles(),
    sourcePath: "X:\\TradingBot\\data\\raw\\source.json",
    from: 120,
    to: 120,
    chartTimeframeSeconds: 60,
    run: (inputPath, bounds) => runActualBridge(inputPath, bounds, 5),
  });

  assert.equal(payload.actualFrom, 120);
  assert.equal(payload.actualTo, 175);
});

test("range pipe handles an abrupt reader disconnect without an unhandled socket error", {
  skip: process.platform !== "win32",
}, async () => {
  const largeRange = Array.from({ length: 80_000 }, (_, index) => ({
    time: index + 1,
    open: index,
    high: index + 1,
    low: index,
    close: index + 1,
  }));

  await assert.rejects(
    withIndicatorRangePipe(largeRange, (pipePath) => new Promise((resolve, reject) => {
      const socket = net.createConnection(pipePath, () => {
        socket.destroy();
        setTimeout(() => resolve("reader closed"), 100);
      });
      socket.on("error", reject);
    })),
    /pipe|reset|broken|closed|EPIPE|ECONNRESET/i,
  );
});
