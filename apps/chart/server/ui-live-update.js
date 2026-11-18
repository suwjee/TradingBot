import path from "node:path";

function contains(parent, entry) {
  const relative = path.relative(parent, entry);
  return relative === "" || (
    !path.isAbsolute(relative) && relative !== ".." && !relative.startsWith(`..${path.sep}`)
  );
}

export function chartWatchOptions({ chartRoot, engineStyles, engineSources = [], enabled, interval }) {
  if (!enabled) return { ignored: ["**/*"] };
  const roots = [path.join(chartRoot, "src"), path.join(chartRoot, "public"), engineStyles];
  const files = [path.join(chartRoot, "index.html"), path.join(chartRoot, "review.html"), ...engineSources];
  return {
    usePolling: true,
    interval,
    binaryInterval: interval,
    ignored: [entry => {
      const absolute = path.resolve(entry);
      return !roots.some(root => contains(root, absolute) || contains(absolute, root))
        && !files.some(file => contains(absolute, file));
    }],
  };
}

export function preserveOpenChart({ workspaceRoot, engineStyles, engineSources = [] }) {
  const engineFiles = new Set(engineSources.map(file => path.resolve(file)));
  return {
    name: "tradingbot-preserve-open-chart",
    apply: "serve",
    configureServer(server) {
      server.watcher.add([engineStyles, ...engineSources]);
      const hot = server.environments.client.hot;
      const send = hot.send.bind(hot);
      // Let Vite find and apply HMR boundaries. Keep incompatible packets from
      // navigating away from the workstation and destroying in-memory state.
      hot.send = (payload, ...args) => {
        const needsReload = payload?.type === "full-reload"
          || (payload?.type === "update" && payload.updates.some(update => update.isWithinCircularImport));
        if (!needsReload) return send(payload, ...args);
        const relative = payload.triggeredBy && path.relative(workspaceRoot, payload.triggeredBy);
        const file = relative && contains(workspaceRoot, payload.triggeredBy)
          ? relative.split(path.sep).join("/") : undefined;
        return send({ type: "custom", event: "tradingbot:ui-update-deferred", data: { file } });
      };
    },
    hotUpdate({ file }) {
      if (!engineFiles.has(path.resolve(file))) return;
      if (this.environment.name === "client") {
        this.environment.hot.send({ type: "custom", event: "tradingbot:engine-source-updated", data: {} });
      }
      return [];
    },
  };
}
