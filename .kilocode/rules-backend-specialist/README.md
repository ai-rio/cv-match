# Backend Specialist Mode Rules

This directory contains specialized rules for the Backend Specialist mode in Kilo Code. These rules override the general rules when working in backend-specific contexts.

## Purpose

The Backend Specialist mode provides enhanced guidance for:
- Backend architecture patterns
- API design and implementation
- Database operations and optimization
- Security best practices for backend services
- Performance optimization techniques
- Testing strategies for backend code

## When to Use

Activate this mode when:
- Designing or implementing backend services
- Working with databases and data models
- Creating API endpoints
- Implementing authentication and authorization
- Optimizing backend performance
- Writing backend tests

## Rule Files

- `08-backend-architecture.md` - Backend architecture patterns
- `09-backend-security.md` - Security best practices
- `10-backend-performance.md` - Performance optimization
- `11-backend-architecture.md` - Additional architecture guidelines
- `12-backend-data-integrity.md` - Data integrity rules
- `13-backend-type-safety.md` - Type safety for backend
- `14-backend-logging.md` - Logging best practices
- `15-backend-testing.md` - Testing strategies
- `16-backend-documentation.md` - Documentation standards
- `17-backend-dependencies-config.md` - Dependencies and configuration
- `18-backend-rules-index.md` - Comprehensive index of all backend rules

## Mode-Specific Overrides

These rules take precedence over the general rules in the parent directory when the Backend Specialist mode is active.

## How to Activate

To activate the Backend Specialist mode in Kilo Code, use the mode selector or specify the mode when starting a new task. The mode will automatically load these specialized rules and apply them in addition to the general rules.

## Priority System

Backend rules follow a priority system:
- **Critical**: Must be followed without exception (security, data integrity, system stability)
- **High**: Should be followed in most cases (performance, maintainability, testing)
- **Medium**: Recommended for best practices (organization, development efficiency)

For detailed information about each rule category, refer to the `18-backend-rules-index.md` file.