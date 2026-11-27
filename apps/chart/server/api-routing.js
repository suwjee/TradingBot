export function useExactApi(middleware, path, handler) {
  middleware.use(path, (request, response, next) => {
    const originalPath = request.originalUrl?.split("?")[0];
    const requestPath = originalPath || request.url?.split("?")[0];
    const exact = requestPath === path || requestPath === `${path}/`;
    const stripped = !originalPath && (!requestPath || requestPath === "/");
    if (!exact && !stripped) return next();
    return handler(request, response, next);
  });
}

export function apiNotFound() {
  return {
    name: "local-api-not-found",
    configureServer(server) {
      server.middlewares.use("/api", (_request, response) => {
        response.writeHead(404, {
          "Content-Type": "application/json; charset=utf-8",
          "Cache-Control": "no-store",
        });
        response.end(JSON.stringify({ error: "API route not found." }));
      });
    },
  };
}
