import { createHash } from "node:crypto";
import { isDeepStrictEqual } from "node:util";

export function restoreRawSnapshot(current, { rawBytes, rawSha256 }) {
  if (!Number.isSafeInteger(rawBytes) || rawBytes <= 0 || rawBytes > current.length) return null;

  // The RAW appender replaces the closing bracket with a comma and preserves
  // the original trailing whitespace after the new closing bracket.
  const closing = current.lastIndexOf(0x5d);
  if (closing < 0) return null;
  const ending = current.subarray(closing);
  const boundary = rawBytes - ending.length;
  if (boundary < 1 || (boundary !== closing && current[boundary] !== 0x2c)) return null;
  const prefix = current.subarray(0, boundary);
  const digest = createHash("sha256").update(prefix).update(ending).digest("hex");
  if (digest !== rawSha256) return null;
  return boundary === closing ? current : Buffer.concat([prefix, ending], rawBytes);
}

export function matchesRecoveredIndicator(saved, recovered) {
  const { timings: _savedTimings, ...savedOutput } = saved;
  const { timings: _recoveredTimings, ...recoveredOutput } = recovered;
  return isDeepStrictEqual(savedOutput, recoveredOutput);
}
