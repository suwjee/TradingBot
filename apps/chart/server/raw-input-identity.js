import fs from "node:fs";
import { createHash } from "node:crypto";

const identityFields = ["dev", "ino", "size", "birthtimeMs", "ctimeMs", "mtimeMs"];
const changedMessage = "The selected RAW file changed while calculating. Apply again with the current file.";

export class RawInputChangedError extends Error {
  constructor(cause) {
    super(changedMessage, { cause });
  }
}

function sameStat(left, right) {
  return left.isFile() && right.isFile()
    && identityFields.every((field) => left[field] === right[field]);
}

export async function captureRawInputIdentity(sourcePath, { includeBytes = false, signal } = {}) {
  try {
    signal?.throwIfAborted();
    const before = fs.statSync(sourcePath);
    if (!before.isFile()) throw new RawInputChangedError();
    const hash = createHash("sha256");
    let bytes;
    if (includeBytes) {
      bytes = await fs.promises.readFile(sourcePath, { signal });
      hash.update(bytes);
    } else {
      for await (const chunk of fs.createReadStream(sourcePath, { signal })) hash.update(chunk);
    }
    const after = fs.statSync(sourcePath);
    if (!sameStat(before, after)) throw new RawInputChangedError();
    const identity = { stat: after, sha256: hash.digest("hex") };
    if (includeBytes) identity.bytes = bytes;
    return identity;
  } catch (error) {
    signal?.throwIfAborted();
    if (error instanceof RawInputChangedError) throw error;
    if (error.code === "ENOENT" || error.code === "ENOTDIR") throw new RawInputChangedError(error);
    throw new Error(changedMessage, { cause: error });
  }
}

export async function assertRawInputUnchanged(sourcePath, selected, options) {
  const current = await captureRawInputIdentity(sourcePath, options);
  if (!sameStat(current.stat, selected.stat) || current.sha256 !== selected.sha256) {
    throw new RawInputChangedError();
  }
  return current.bytes;
}
