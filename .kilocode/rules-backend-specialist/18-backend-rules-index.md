# Backend Rules Index

This document provides a comprehensive index of all backend-specific rules for the CV-Match project. Rules are organized by category and priority to guide development and ensure consistency.

## 📋 Rule Categories

### 🔒 Security (BE-SEC)
| Rule ID | Priority | Description |
|---------|----------|-------------|
| [BE-SEC-001](09-backend-security.md#be-sec-001-input-validation-critical) | Critical | Input validation with Pydantic schemas |
| [BE-SEC-002](09-backend-security.md#be-sec-002-authentication--authorization-critical) | Critical | JWT authentication and role-based access control |
| [BE-SEC-003](09-backend-security.md#be-sec-003-environment-variables--secrets-critical) | Critical | Environment variable management with BaseSettings |
| [BE-SEC-004](09-backend-security.md#be-sec-004-rate-limiting-critical) | Critical | Rate limiting with Redis backend |
| [BE-SEC-005](09-backend-security.md#be-sec-005-cors-configuration-high) | High | CORS configuration with explicit origins |
| [BE-SEC-006](09-backend-security.md#be-sec-006-error-handling-high) | High | Comprehensive error handling with custom exceptions |

### ⚡ Performance (BE-PER)
| Rule ID | Priority | Description |
|---------|----------|-------------|
| [BE-PER-001](10-backend-performance.md#be-per-001-async-operations-critical) | Critical | Async/await for all I/O operations |
| [BE-PER-002](10-backend-performance.md#be-per-002-database-connection-pooling-critical) | Critical | Database connection pooling with AsyncSession |
| [BE-PER-003](10-backend-performance.md#be-per-003-redis-caching-high) | High | Redis caching for expensive operations |
| [BE-PER-004](10-backend-performance.md#be-per-004-database-optimization-high) | High | Database indexes and query optimization |
| [BE-PER-005](10-backend-performance.md#be-per-005-background-tasks-medium) | Medium | Background tasks with FastAPI/Celery |

### 🏗️ Architecture (BE-ARC)
| Rule ID | Priority | Description |
|---------|----------|-------------|
| [BE-ARC-001](11-backend-architecture.md#be-arc-001-layered-architecture-critical) | Critical | Layered architecture with clear separation |
| [BE-ARC-002](11-backend-architecture.md#be-arc-002-dependency-injection-critical) | Critical | Dependency injection with FastAPI's Depends |
| [BE-ARC-003](11-backend-architecture.md#be-arc-003-repository-pattern-high) | High | Repository pattern for data access |
| [BE-ARC-004](11-backend-architecture.md#be-arc-004-feature-based-organization-high) | High | Feature-based module organization |
| [BE-ARC-005](11-backend-architecture.md#be-arc-005-pydantic-schema-design-medium) | Medium | Pydantic models for request/response schemas |

### 🗃️ Data Integrity (BE-DATA)
| Rule ID | Priority | Description |
|---------|----------|-------------|
| [BE-DATA-001](12-backend-data-integrity.md#be-data-001-schema-first-validation-critical) | Critical | Schema-first validation with Pydantic |
| [BE-DATA-002](12-backend-data-integrity.md#be-data-002-database-constraints-critical) | Critical | Database constraints and relationships |
| [BE-DATA-003](12-backend-data-integrity.md#be-data-003-transaction-management-high) | High | Database transactions with commit/rollback |
| [BE-DATA-004](12-backend-data-integrity.md#be-data-004-database-migrations-high) | High | Database migrations with Alembic |
| [BE-DATA-005](12-backend-data-integrity.md#be-data-005-foreign-key-relationships-medium) | Medium | Foreign key relationships with cascade options |

### 🔧 Type Safety (BE-TYPE)
| Rule ID | Priority | Description |
|---------|----------|-------------|
| [BE-TYPE-001](13-backend-type-safety.md#be-type-001-strict-type-hints-critical) | Critical | Strict type hints for all functions |
| [BE-TYPE-002](13-backend-type-safety.md#be-type-002-pydantic-models-high) | High | Pydantic models for data structures |
| [BE-TYPE-003](13-backend-type-safety.md#be-type-003-internal-data-structures-medium) | Medium | TypedDict/dataclasses for internal data |

### 📝 Logging (BE-LOG)
| Rule ID | Priority | Description |
|---------|----------|-------------|
| [BE-LOG-001](14-backend-logging.md#be-log-001-structured-logging-critical) | Critical | Structured JSON logging with context |
| [BE-LOG-002](14-backend-logging.md#be-log-002-security-event-logging-high) | High | Security event logging with alerting |
| [BE-LOG-003](14-backend-logging.md#be-log-003-log-level-management-medium) | Medium | Consistent log level usage |

### 🧪 Testing (BE-TEST)
| Rule ID | Priority | Description |
|---------|----------|-------------|
| [BE-TEST-001](15-backend-testing.md#be-test-001-unit-tests-for-service-layer-critical) | Critical | Unit tests for service layer |
| [BE-TEST-002](15-backend-testing.md#be-test-002-integration-tests-for-api-endpoints-high) | High | Integration tests for API endpoints |
| [BE-TEST-003](15-backend-testing.md#be-test-003-database-tests-with-transaction-rollback-medium) | Medium | Database tests with transaction rollback |

### 📚 Documentation (BE-DOC)
| Rule ID | Priority | Description |
|---------|----------|-------------|
| [BE-DOC-001](16-backend-documentation.md#be-doc-001-api-documentation-with-openapi-high) | High | OpenAPI documentation with examples |
| [BE-DOC-002](16-backend-documentation.md#be-doc-002-service-method-documentation-medium) | Medium | Comprehensive docstrings for services |

### 🔌 Dependencies & Configuration (BE-DEP/BE-CONFIG)
| Rule ID | Priority | Description |
|---------|----------|-------------|
| [BE-DEP-001](17-backend-dependencies-config.md#be-dep-001-dependency-injection-medium) | Medium | Dependency injection with FastAPI's Depends |
| [BE-DEP-002](17-backend-dependencies-config.md#be-dep-002-circular-import-prevention-medium) | Medium | Circular import prevention strategies |
| [BE-CONFIG-001](17-backend-dependencies-config.md#be-config-001-configuration-management-high) | High | Pydantic BaseSettings for configuration |
| [BE-CONFIG-002](17-backend-dependencies-config.md#be-config-002-environment-specific-configuration-medium) | Medium | Environment-specific configurations |

## 🎯 Priority Guidelines

### Critical Priority Rules
These rules must be followed without exception as they impact:
- Security vulnerabilities
- Data integrity
- System stability
- Core functionality

### High Priority Rules
These rules should be followed in most cases as they impact:
- Performance optimization
- Code maintainability
- Testing coverage
- Documentation quality

### Medium Priority Rules
These rules are recommended for best practices as they impact:
- Code organization
- Development efficiency
- Long-term maintainability

## 🚀 Implementation Workflow

1. **Development Phase**: Follow all Critical and High priority rules
2. **Code Review**: Verify compliance with applicable rules
3. **Testing**: Ensure BE-TEST rules are followed
4. **Deployment**: Verify BE-CONFIG rules for environment
5. **Documentation**: Update according to BE-DOC rules

## 📖 Quick Reference

### Security Checklist
- [ ] Input validation on all endpoints (BE-SEC-001)
- [ ] Authentication and authorization implemented (BE-SEC-002)
- [ ] Environment variables properly configured (BE-SEC-003)
- [ ] Rate limiting on public endpoints (BE-SEC-004)
- [ ] CORS properly configured (BE-SEC-005)
- [ ] Error handling implemented (BE-SEC-006)

### Performance Checklist
- [ ] Async operations used for I/O (BE-PER-001)
- [ ] Database connection pooling configured (BE-PER-002)
- [ ] Caching implemented for expensive operations (BE-PER-003)
- [ ] Database queries optimized (BE-PER-004)
- [ ] Background tasks for heavy processing (BE-PER-005)

### Architecture Checklist
- [ ] Layered architecture followed (BE-ARC-001)
- [ ] Dependency injection used (BE-ARC-002)
- [ ] Repository pattern implemented (BE-ARC-003)
- [ ] Feature-based organization (BE-ARC-004)
- [ ] Pydantic schemas designed (BE-ARC-005)

---

For detailed implementation examples and rationale, please refer to the individual rule files linked above.