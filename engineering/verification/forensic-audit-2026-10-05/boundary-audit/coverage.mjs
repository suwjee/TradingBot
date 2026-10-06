import fs from 'node:fs';
import path from 'node:path';
import { createHash } from 'node:crypto';
import { fileURLToPath, pathToFileURL } from 'node:url';

const directory = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(directory, '../../../..');
const { parseAst } = await import(pathToFileURL(path.join(root, 'apps/chart/node_modules/rolldown/dist/parse-ast-index.mjs')));
const productionFiles = [
  'apps/chart/vite.config.js',
  'apps/chart/server/indicator-range-input.js',
  'apps/chart/server/calculation-cache.js',
  'apps/chart/server/raw-input-identity.js',
  'apps/chart/server/calculation-coordinator.js',
  'apps/chart/server/raw-resource-store.js',
  'apps/chart/server/local-state-paths.js',
  'apps/chart/server/request-body.js',
  'apps/chart/server/progress-channels.js',
  'apps/chart/src/features/raw-file-contract.js',
  'apps/chart/src/features/candle-update.js',
];
const testFiles = ['indicator-range-input', 'calculation-cache', 'raw-input-identity', 'calculation-coordinator'].map((name) => `apps/chart/tests/unit/${name}.test.mjs`);
const output = { parser: 'Installed Rolldown parseAst; read-only parsing, no config import or bundling', files: [], tests: [], scope: 'READ_FULL records reading coverage, not independent correctness of every callable.' };
const baselinePath = path.join(directory, '../protected-pre-hashes.json');
const baseline = fs.existsSync(baselinePath) ? JSON.parse(fs.readFileSync(baselinePath, 'utf8')) : {};
for (const relative of [...productionFiles, ...testFiles]) {
  const bytes = fs.readFileSync(path.join(root, relative));
  const source = bytes.toString('utf8');
  const lineAt = (offset) => source.slice(0, offset).split('\n').length;
  const functions = [];
  const ast = parseAst(source, null, relative);
  function visit(node, parent) {
    if (!node || typeof node !== 'object') return;
    if (['FunctionDeclaration', 'FunctionExpression', 'ArrowFunctionExpression'].includes(node.type)) {
      let name = node.id?.name;
      if (!name && parent?.type === 'VariableDeclarator') name = parent.id?.name;
      if (!name && parent?.type === 'Property') name = parent.key?.name || parent.key?.value;
      functions.push({ name: name || `<anonymous ${node.type}>`, startLine: lineAt(node.start), endLine: lineAt(node.end), nodeType: node.type, coverage: 'READ_FULL' });
    }
    for (const [key, value] of Object.entries(node)) {
      if (key === 'loc' || key === 'range') continue;
      if (Array.isArray(value)) for (const child of value) visit(child, node);
      else if (value && typeof value === 'object') visit(value, node);
    }
  }
  visit(ast, null);
  const record = { path: relative, coverage: 'READ_FULL', lines: source.split('\n').length - (source.endsWith('\n') ? 1 : 0), bytes: bytes.length, sha256: createHash('sha256').update(bytes).digest('hex'), functions: functions.sort((a, b) => a.startLine - b.startLine || a.endLine - b.endLine) };
  const originalHash = baseline[relative.replaceAll('/', '\\')];
  record.rootPreAuditIntegrity = originalHash ? (originalHash === record.sha256 ? 'PASS' : 'FAIL') : 'NOT IN ROOT PRE-AUDIT HASH SCOPE';
  if (record.rootPreAuditIntegrity === 'FAIL') throw new Error(`Protected file changed: ${relative}`);
  (testFiles.includes(relative) ? output.tests : output.files).push(record);
}
output.productionFunctionCount = output.files.reduce((count, file) => count + file.functions.length, 0);
output.productionLines = output.files.reduce((count, file) => count + file.lines, 0);
fs.writeFileSync(path.join(directory, 'coverage.json'), JSON.stringify(output, null, 2));
console.log(JSON.stringify({ status: 'PASS', fullProductionFiles: output.files.length, fullTestFiles: output.tests.length, productionFunctionCount: output.productionFunctionCount, productionLines: output.productionLines }));
