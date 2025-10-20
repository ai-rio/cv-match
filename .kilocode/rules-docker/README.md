# Docker Rules Mode

This directory contains specialized rules for the Docker mode in Kilo Code. These rules override the general rules when working with Docker-related tasks.

## Purpose

The Docker mode provides enhanced guidance for:
- Dockerfile best practices and optimization
- Docker Compose configuration and orchestration
- Container security and hardening
- Multi-stage builds and image optimization
- Docker networking and volume management
- Container deployment and monitoring

## When to Use

Activate this mode when:
- Creating or modifying Dockerfiles
- Writing Docker Compose configurations
- Optimizing container images
- Setting up containerized development environments
- Implementing container security measures
- Troubleshooting Docker issues
- Designing container architecture

## Rule Files

- `01-dockerfile-best-practices.md` - Dockerfile writing guidelines and optimizations
- `02-docker-compose-best-practices.md` - Docker Compose configuration patterns
- `03-docker-security.md` - Container security best practices

## Mode-Specific Overrides

These rules take precedence over the general rules in the parent directory when the Docker mode is active.

## How to Activate

To activate the Docker mode in Kilo Code, use the mode selector or specify the mode when starting a new task. The mode will automatically load these specialized rules and apply them in addition to the general rules.

## Key Principles

The Docker mode emphasizes:
- **Security**: Running containers with minimal privileges and proper isolation
- **Efficiency**: Optimizing image sizes and build times
- **Maintainability**: Writing clear, reusable Docker configurations
- **Scalability**: Designing containerized applications for horizontal scaling
- **Portability**: Ensuring containers work consistently across environments
- **Monitoring**: Implementing proper logging and health checks

## Integration with Project Structure

These rules work with the project's existing Docker setup:
- Frontend Dockerfile (Next.js application)
- Backend Dockerfile (Python FastAPI application)
- Development and production Docker Compose files
- Multi-environment configurations

## Common Workflows

1. **Development Setup**: Using Docker Compose for local development
2. **Production Deployment**: Building optimized images for production
3. **Security Hardening**: Implementing container security best practices
4. **Performance Optimization**: Reducing image sizes and improving build times
5. **Troubleshooting**: Diagnosing and fixing common Docker issues