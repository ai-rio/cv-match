# Dockerfile Best Practices

## General Guidelines
- ALWAYS use specific base image versions (e.g., `node:18-alpine` not `node:latest`)
- Minimize the number of layers by combining related commands
- Use `.dockerignore` to exclude unnecessary files
- Order instructions from least to most likely to change
- Use multi-stage builds for production images

## Security Best Practices
- NEVER run containers as root user
- Use official base images when possible
- Regularly update base images to patch vulnerabilities
- Scan images for security vulnerabilities
- Don't include sensitive data in images

## Performance Optimization
- Use `.dockerignore` to reduce build context
- Leverage Docker layer caching effectively
- Use appropriate base image size (alpine for production)
- Remove unnecessary dependencies and tools
- Optimize for smaller image sizes

## Example Structure

```dockerfile
# Multi-stage build example
FROM node:18-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production && npm cache clean --force

FROM node:18-alpine AS runtime
RUN addgroup -g 1001 -S nodejs
RUN adduser -S nextjs -u 1001
WORKDIR /app
COPY --from=builder /app/node_modules ./node_modules
COPY --chown=nextjs:nodejs . .
USER nextjs
EXPOSE 3000
ENV NODE_ENV production
CMD ["node", "server.js"]
```

## Common Mistakes to Avoid
❌ **NEVER DO:**
```dockerfile
FROM node:latest  # No specific version
RUN apt-get update && apt-get install -y git  # Not cleaned up
USER root  # Running as root
COPY . .  # Copies everything including node_modules
```

✅ **ALWAYS DO:**
```dockerfile
FROM node:18-alpine  # Specific version
RUN apt-get update && apt-get install -y git && \
    apt-get clean && rm -rf /var/lib/apt/lists/*  # Clean up
USER node  # Non-root user
COPY package*.json ./  # Only copy what's needed first
RUN npm ci --only=production
COPY . .  # Then copy source code