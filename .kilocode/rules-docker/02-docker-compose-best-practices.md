# Docker Compose Best Practices

## General Guidelines
- Use version 3.x or later of Docker Compose format
- Define explicit versions for all services
- Use environment variables for configuration
- Implement proper health checks
- Use appropriate restart policies

## Service Configuration
- Set resource limits (memory, CPU) for production
- Configure proper networking between services
- Use named volumes for persistent data
- Implement proper dependency management with `depends_on`

## Environment Management
- Use `.env` files for environment-specific variables
- Never commit sensitive data to version control
- Use different compose files for different environments
- Implement proper secret management

## Example Structure

```yaml
version: '3.8'

services:
  app:
    build:
      context: .
      dockerfile: Dockerfile
    ports:
      - "3000:3000"
    environment:
      - NODE_ENV=production
    restart: unless-stopped
    depends_on:
      db:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:3000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  db:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: ${DB_NAME}
      POSTGRES_USER: ${DB_USER}
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${DB_USER}"]
      interval: 10s
      timeout: 5s
      retries: 5

volumes:
  postgres_data:
```

## Common Mistakes to Avoid
❌ **NEVER DO:**
```yaml
version: '2'  # Outdated version
services:
  app:
    image: node:latest  # No specific version
    ports:
      - "3000"  # Missing host port
    environment:
      - PASSWORD=secret123  # Hardcoded secret
```

✅ **ALWAYS DO:**
```yaml
version: '3.8'  # Current version
services:
  app:
    image: node:18-alpine  # Specific version
    ports:
      - "3000:3000"  # Proper port mapping
    environment:
      - PASSWORD=${DB_PASSWORD}  # Environment variable
    env_file:
      - .env  # Load from file