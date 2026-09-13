# --- Build stage -------------------------------------------------------
# Debian-based (glibc), not Alpine: Vite 8's bundler (Rolldown) ships
# platform-specific native binaries, and `npm ci` against a lockfile
# resolved on a different machine hits npm's long-standing optional-
# dependency bug (npm/cli#4828) -- it can't find its own native binding.
# `npm install` (not `npm ci`) re-resolves optional deps fresh for
# whatever platform is actually building the image, which is npm's own
# documented workaround. The runtime stage below is still Alpine -- it
# never gets node_modules, just the static dist/ output.
FROM node:20.18-bookworm-slim AS build
WORKDIR /app

COPY package.json ./
RUN npm install
RUN echo "--- diagnostic: rolldown optional binding state ---" \
    && node -p "process.platform + ' ' + process.arch" \
    && (ls node_modules/@rolldown/ 2>&1 || echo "no @rolldown dir") \
    && npm ls rolldown 2>&1 || true

COPY . .
RUN npm run build

# --- Runtime stage -------------------------------------------------------
# nginx-unprivileged: runs as a non-root user (uid 101) and listens on 8080
# by default, so no extra USER/port juggling is needed here.
FROM nginxinc/nginx-unprivileged:1.27-alpine

COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=5s --retries=3 --start-period=5s \
    CMD wget -qO- http://127.0.0.1:8080/ >/dev/null || exit 1
