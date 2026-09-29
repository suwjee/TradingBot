import path from 'node:path';

/** Resolve machine state independently from the checkout's source tree. */
export function resolveLocalStatePaths(workspaceRoot, configuredRoot = process.env.TRADINGBOT_LOCAL_STATE_ROOT) {
  const workspace = path.resolve(workspaceRoot);
  const root = configuredRoot?.trim()
    ? path.resolve(workspace, configuredRoot.trim())
    : path.join(path.dirname(workspace), `${path.basename(workspace)}-Local`);
  const relative = path.relative(workspace, root);
  if (!relative || (!path.isAbsolute(relative) && relative !== '..' && !relative.startsWith(`..${path.sep}`))) {
    throw new Error('TRADINGBOT_LOCAL_STATE_ROOT must be outside the repository.');
  }
  return Object.freeze({
    root,
    raw: path.join(root, 'data', 'raw'),
    cache: path.join(root, 'cache'),
    secret: path.join(root, 'secret'),
    tmp: path.join(root, 'tmp'),
  });
}
