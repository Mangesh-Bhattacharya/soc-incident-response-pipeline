# --- Build stage -------------------------------------------------------
FROM node:20.18-bookworm-slim AS build
WORKDIR /app

COPY package.json ./
RUN npm install

# Vite 8's bundler (Rolldown) ships its actual engine as a platform-specific
# optional dependency (@rolldown/binding-<platform>). npm correctly detects
# linux/x64 here but still doesn't install that package -- confirmed by
# inspecting node_modules/@rolldown/ in this exact image, which comes up
# empty of any binding package. That's npm's own documented optional-
# dependency bug (npm/cli#4828), most likely a libc-detection gap in this
# minimal Debian image causing npm to skip every libc-tagged optional
# package rather than assume glibc. Installing the exact matching version
# explicitly sidesteps whatever heuristic is failing.
RUN ROLLDOWN_VERSION="$(node -p "require('./node_modules/rolldown/package.json').version")" \
    && npm install --no-save "@rolldown/binding-linux-x64-gnu@${ROLLDOWN_VERSION}"

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
