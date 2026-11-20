import fs from "node:fs";
import { pipeline } from "node:stream/promises";

function entityTag(stat) {
  return `"${[stat.dev, stat.ino, stat.size, stat.mtimeNs, stat.ctimeNs].map(value => value.toString(16)).join("-")}"`;
}

function matchesEntityTag(header, expected) {
  return String(header || "")
    .split(",")
    .map((value) => value.trim().replace(/^W\//, ""))
    .includes(expected);
}

export async function sendCandleFile(req, res, dataPath) {
  const file = await fs.promises.open(dataPath, "r");
  try {
    const stat = await file.stat({ bigint: true });
    const etag = entityTag(stat);
    res.setHeader("Content-Type", "application/json; charset=utf-8");
    res.setHeader("Cache-Control", "private, no-cache");
    res.setHeader("ETag", etag);
    if (matchesEntityTag(req.headers?.["if-none-match"], etag)) {
      res.statusCode = 304;
      res.end();
      return;
    }
    res.setHeader("Content-Length", stat.size.toString());
    await pipeline(file.createReadStream({ autoClose: false }), res);
  } finally {
    await file.close();
  }
}
