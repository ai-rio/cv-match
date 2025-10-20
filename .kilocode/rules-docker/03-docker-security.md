# Docker Security Best Practices

## Container Security
- ALWAYS run containers as non-root users
- Use minimal base images (alpine, distroless)
- Remove unnecessary tools and packages
- Implement read-only filesystems where possible
- Use security scanning tools in CI/CD pipeline

## Image Security
- Scan images for vulnerabilities before deployment
- Use trusted base images from official repositories
- Regularly update base images and dependencies
- Sign images for production deployments
- Implement image vulnerability monitoring

## Network Security
- Use private networks for inter-service communication
- Expose only necessary ports
- Implement firewall rules at container level
- Use encrypted communication between services
- Limit container capabilities with `--cap-drop`

## Secrets Management
- NEVER store secrets in Docker images
- Use Docker secrets or external secret management
- Pass secrets through environment variables or mounted volumes
- Rotate secrets regularly
- Implement proper access controls for secrets

## Example Security Configuration

```dockerfile
# Secure Dockerfile example
FROM node:18-alpine AS builder
# Create non-root user
RUN addgroup -g 1001 -S nodejs && \
    adduser -S nextjs -u 1001

# Set working directory
WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN bun ci --only=production && bun cache clean --force

# Copy source code
COPY --chown=nextjs:nodejs . .

# Switch to non-root user
USER nextjs

# Expose port
EXPOSE 3000

# Set environment
ENV NODE_ENV production

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:3000/health || exit 1

# Start application
CMD ["node", "server.js"]
```

```yaml
# Secure docker-compose example
version: '3.8'

services:
  app:
    build:
      context: .
      dockerfile: Dockerfile
    user: "1001:1001"  # Non-root user
    read_only: true  # Read-only filesystem
    tmpfs:
      - /tmp  # Writable tmp directory
    cap_drop:
      - ALL  # Drop all capabilities
    cap_add:
      - NET_BIND_SERVICE  # Add only needed capability
    security_opt:
      - no-new-privileges:true  # Prevent privilege escalation
    environment:
      - NODE_ENV=production
    secrets:
      - db_password  # Use Docker secrets
    networks:
      - internal  # Use private network

secrets:
  db_password:
    external: true

networks:
  internal:
    driver: bridge
    internal: true  # Internal network only
```

## Common Security Mistakes to Avoid
❌ **NEVER DO:**
```dockerfile
FROM node:latest  # Unspecified version
USER root  # Running as root
ENV PASSWORD=secret123  # Hardcoded secret
```

✅ **ALWAYS DO:**
```dockerfile
FROM node:18-alpine  # Specific minimal image
USER node  # Non-root user
ENV PASSWORD=${DB_PASSWORD}  # Environment variable