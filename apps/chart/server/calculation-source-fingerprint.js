import fs from 'node:fs';
import path from 'node:path';
import { createHash } from 'node:crypto';

/**
 * Content-derived identity for an ordered group of calculation dependencies.
 * Keep the historical digest composition: basename + NUL + binary SHA-256
 * of each entire file. Never substitute timestamps or file sizes here.
 */
export function calculateSourceFingerprint(sources) {
  const hash = createHash('sha256');
  for (const file of sources) {
    hash.update(path.basename(file));
    hash.update('\0');
    hash.update(createHash('sha256').update(fs.readFileSync(file)).digest());
  }
  return hash.digest('hex');
}
