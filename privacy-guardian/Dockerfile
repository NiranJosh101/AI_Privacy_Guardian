# Use Bun for fast installs + builds
FROM oven/bun:1.1

WORKDIR /app

# 1. Cache dependencies
COPY package.json bun.lock ./
RUN bun install --frozen-lockfile

# 2. Copy source code
COPY . .

# 3. Build the extension
RUN bun run build

# Default command (optional, just shows build output exists)
CMD ["ls", "-la", "dist"]