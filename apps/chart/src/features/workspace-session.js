const WORKSPACES = new Set(["chart", "faraz", "algorithm"]);

export function resolveWorkspaceRefreshState(saved, { fileIds = [], timeframes = [] } = {}) {
  const value = saved && typeof saved === "object" ? saved : {};
  const workspace = WORKSPACES.has(value.workspace) ? value.workspace : "chart";
  const fileId = fileIds.includes(value.fileId) ? value.fileId : null;
  const timeframe = timeframes.includes(Number(value.timeframe)) ? Number(value.timeframe) : null;
  return { workspace, fileId, timeframe };
}
