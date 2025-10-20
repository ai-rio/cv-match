# Backend Logging Rules

## BE-LOG-001: Structured Logging (Critical)
**Rule**: Implement structured JSON logging with pythonjsonlogger including request IDs, user context, and error details

### Implementation
```python
# ✅ ALWAYS implement structured logging
# core/logging.py
import logging
import sys
import uuid
from typing import Dict, Any, Optional
from pythonjsonlogger import jsonlogger
from contextvars import ContextVar

# Context variables for request tracking
request_id_var: ContextVar[Optional[str]] = ContextVar('request_id', default=None)
user_id_var: ContextVar[Optional[str]] = ContextVar('user_id', default=None)

class StructuredLogger:
    """Structured logger with JSON output and context"""
    
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
        self._setup_logger()
    
    def _setup_logger(self):
        """Setup logger with JSON formatter"""
        logHandler = logging.StreamHandler(sys.stdout)
        formatter = jsonlogger.JsonFormatter(
            fmt='%(asctime)s %(name)s %(levelname)s %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        logHandler.setFormatter(formatter)
        self.logger.addHandler(logHandler)
        self.logger.setLevel(logging.INFO)
    
    def _get_context(self) -> Dict[str, Any]:
        """Get current context variables"""
        return {
            'request_id': request_id_var.get(),
            'user_id': user_id_var.get(),
        }
    
    def info(self, message: str, **kwargs):
        """Log info message with context"""
        extra = {**self._get_context(), **kwargs}
        self.logger.info(message, extra=extra)
    
    def error(self, message: str, **kwargs):
        """Log error message with context"""
        extra = {**self._get_context(), **kwargs}
        self.logger.error(message, extra=extra)
    
    def warning(self, message: str, **kwargs):
        """Log warning message with context"""
        extra = {**self._get_context(), **kwargs}
        self.logger.warning(message, extra=extra)
    
    def debug(self, message: str, **kwargs):
        """Log debug message with context"""
        extra = {**self._get_context(), **kwargs}
        self.logger.debug(message, extra=extra)

# Usage in modules
logger = StructuredLogger(__name__)

# Middleware for request tracking
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware to add request tracking to logs"""
    
    async def dispatch(self, request: Request, call_next):
        # Generate request ID
        request_id = str(uuid.uuid4())
        request_id_var.set(request_id)
        
        # Log request start
        logger.info(
            "Request started",
            method=request.method,
            url=str(request.url),
            client_ip=request.client.host if request.client else None
        )
        
        try:
            response = await call_next(request)
            
            # Log request completion
            logger.info(
                "Request completed",
                status_code=response.status_code,
                duration_ms=None  # Would be calculated with timing
            )
            
            return response
            
        except Exception as e:
            # Log request error
            logger.error(
                "Request failed",
                error=str(e),
                error_type=type(e).__name__
            )
            raise

# Usage in endpoints
@router.post("/cvs")
async def create_cv(cv: CVCreate, db: AsyncSession = Depends(get_db)):
    logger.info(
        "Creating CV",
        candidate_name=cv.candidate_name,
        skills_count=len(cv.skills)
    )
    
    try:
        service = CVService(db)
        result = await service.create(cv)
        
        logger.info(
            "CV created successfully",
            cv_id=result.id,
            candidate_name=result.candidate_name
        )
        
        return result
        
    except Exception as e:
        logger.error(
            "Failed to create CV",
            error=str(e),
            candidate_name=cv.candidate_name,
            error_type=type(e).__name__
        )
        raise
```

### Rationale
Backend logs must be machine-readable for monitoring and debugging in production.

---

## BE-LOG-002: Security Event Logging (High)
**Rule**: Log security events (authentication failures, authorization errors, suspicious activities) separately with alerting

### Implementation
```python
# ✅ ALWAYS log security events separately
# core/security_logging.py
import logging
from datetime import datetime
from typing import Dict, Any, Optional
from enum import Enum

class SecurityEventType(str, Enum):
    AUTH_FAILURE = "auth_failure"
    AUTH_SUCCESS = "auth_success"
    AUTHZ_FAILURE = "authz_failure"
    SUSPICIOUS_ACTIVITY = "suspicious_activity"
    DATA_ACCESS = "data_access"
    PRIVILEGE_ESCALATION = "privilege_escalation"

class SecurityLogger:
    """Dedicated logger for security events"""
    
    def __init__(self):
        self.logger = logging.getLogger("security")
        self._setup_security_logger()
    
    def _setup_security_logger(self):
        """Setup security logger with separate handler"""
        # Could use different handler for security logs
        handler = logging.StreamHandler(sys.stdout)
        formatter = jsonlogger.JsonFormatter(
            fmt='%(asctime)s %(name)s %(levelname)s %(message)s'
        )
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)
    
    def log_security_event(
        self,
        event_type: SecurityEventType,
        message: str,
        user_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        resource: Optional[str] = None,
        **kwargs
    ):
        """Log security event with standardized fields"""
        security_data = {
            'event_type': event_type.value,
            'timestamp': datetime.utcnow().isoformat(),
            'user_id': user_id,
            'ip_address': ip_address,
            'user_agent': user_agent,
            'resource': resource,
            'severity': self._get_severity(event_type),
            **kwargs
        }
        
        self.logger.warning(message, extra=security_data)
    
    def _get_severity(self, event_type: SecurityEventType) -> str:
        """Get severity level for event type"""
        high_severity = {
            SecurityEventType.AUTHZ_FAILURE,
            SecurityEventType.PRIVILEGE_ESCALATION,
            SecurityEventType.SUSPICIOUS_ACTIVITY
        }
        return "HIGH" if event_type in high_severity else "MEDIUM"

# Global security logger instance
security_logger = SecurityLogger()

# Usage in authentication
async def login_user(credentials: LoginSchema, request: Request):
    try:
        user = await authenticate_user(credentials.email, credentials.password)
        
        if not user:
            security_logger.log_security_event(
                SecurityEventType.AUTH_FAILURE,
                "Authentication failed",
                email=credentials.email,
                ip_address=request.client.host if request.client else None,
                user_agent=request.headers.get("user-agent"),
                reason="Invalid credentials"
            )
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        security_logger.log_security_event(
            SecurityEventType.AUTH_SUCCESS,
            "User authenticated successfully",
            user_id=user.id,
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent")
        )
        
        return user
        
    except Exception as e:
        security_logger.log_security_event(
            SecurityEventType.AUTH_FAILURE,
            "Authentication error",
            email=credentials.email,
            ip_address=request.client.host if request.client else None,
            error=str(e)
        )
        raise

# Usage in authorization
async def check_admin_permission(current_user: User, resource: str):
    if not current_user.is_admin:
        security_logger.log_security_event(
            SecurityEventType.AUTHZ_FAILURE,
            "Unauthorized access attempt",
            user_id=current_user.id,
            resource=resource,
            required_role="admin",
            user_role="user"
        )
        raise HTTPException(status_code=403, detail="Not enough permissions")

# Usage for suspicious activity detection
async def detect_suspicious_activity(request: Request, user_id: str):
    # Example: Detect rapid password reset requests
    recent_requests = await get_recent_password_reset_requests(user_id, hours=1)
    
    if len(recent_requests) > 5:
        security_logger.log_security_event(
            SecurityEventType.SUSPICIOUS_ACTIVITY,
            "Multiple password reset requests detected",
            user_id=user_id,
            ip_address=request.client.host if request.client else None,
            request_count=len(recent_requests),
            time_window="1 hour"
        )
        
        # Could trigger additional security measures
        await lock_user_account_temporarily(user_id)
```

### Rationale
Backend security monitoring requires dedicated logging and alerting.

---

## BE-LOG-003: Log Level Management (Medium)
**Rule**: Use appropriate log levels (DEBUG, INFO, WARNING, ERROR, CRITICAL) consistently across the application

### Implementation
```python
# ✅ ALWAYS use consistent log levels
# core/log_levels.py
import logging
from typing import Any, Dict
from enum import Enum

class LogCategory(str, Enum):
    BUSINESS = "business"
    SECURITY = "security"
    PERFORMANCE = "performance"
    SYSTEM = "system"
    DATABASE = "database"

class LogLevels:
    """Standardized log level usage"""
    
    # DEBUG: Detailed information for debugging
    @staticmethod
    def debug(message: str, category: LogCategory, **kwargs):
        """Use for detailed debugging information"""
        logger.debug(
            message,
            category=category.value,
            **kwargs
        )
    
    # INFO: General information about application flow
    @staticmethod
    def info(message: str, category: LogCategory, **kwargs):
        """Use for general application events"""
        logger.info(
            message,
            category=category.value,
            **kwargs
        )
    
    # WARNING: Something unexpected happened, but application continues
    @staticmethod
    def warning(message: str, category: LogCategory, **kwargs):
        """Use for potential issues that don't stop execution"""
        logger.warning(
            message,
            category=category.value,
            **kwargs
        )
    
    # ERROR: Error occurred, but application can continue
    @staticmethod
    def error(message: str, category: LogCategory, **kwargs):
        """Use for errors that don't crash the application"""
        logger.error(
            message,
            category=category.value,
            **kwargs
        )
    
    # CRITICAL: Serious error, application may not continue
    @staticmethod
    def critical(message: str, category: LogCategory, **kwargs):
        """Use for critical errors that may crash the application"""
        logger.critical(
            message,
            category=category.value,
            **kwargs
        )

# Usage examples in different contexts
class CVService:
    async def create_cv(self, cv_data: CVCreate, user_id: str):
        # Business logic logging
        LogLevels.info(
            "Creating new CV",
            LogCategory.BUSINESS,
            user_id=user_id,
            candidate_name=cv_data.candidate_name
        )
        
        try:
            # Database operation logging
            LogLevels.debug(
                "Executing database insert",
                LogCategory.DATABASE,
                table="cvs",
                operation="insert"
            )
            
            cv = await self.repository.create(cv_data)
            
            LogLevels.info(
                "CV created successfully",
                LogCategory.BUSINESS,
                cv_id=cv.id,
                user_id=user_id
            )
            
            return cv
            
        except DatabaseError as e:
            LogLevels.error(
                "Database error while creating CV",
                LogCategory.DATABASE,
                error=str(e),
                user_id=user_id
            )
            raise
            
        except Exception as e:
            LogLevels.error(
                "Unexpected error creating CV",
                LogCategory.SYSTEM,
                error=str(e),
                error_type=type(e).__name__,
                user_id=user_id
            )
            raise

class PerformanceMonitor:
    async def monitor_response_time(self, endpoint: str, duration_ms: int):
        # Performance logging
        if duration_ms > 5000:  # 5 seconds
            LogLevels.warning(
                "Slow response time detected",
                LogCategory.PERFORMANCE,
                endpoint=endpoint,
                duration_ms=duration_ms,
                threshold_ms=5000
            )
        else:
            LogLevels.debug(
                "Response time recorded",
                LogCategory.PERFORMANCE,
                endpoint=endpoint,
                duration_ms=duration_ms
            )

class HealthCheckService:
    async def check_database_health(self):
        try:
            # System health check
            await self.db.execute("SELECT 1")
            LogLevels.debug(
                "Database health check passed",
                LogCategory.SYSTEM
            )
            return True
            
        except Exception as e:
            LogLevels.critical(
                "Database health check failed",
                LogCategory.SYSTEM,
                error=str(e),
                service="database"
            )
            return False

# Configuration for log levels by environment
class LogConfig:
    @staticmethod
    def get_log_level(environment: str) -> int:
        """Get appropriate log level for environment"""
        if environment == "development":
            return logging.DEBUG
        elif environment == "testing":
            return logging.WARNING
        elif environment == "staging":
            return logging.INFO
        else:  # production
            return logging.INFO
    
    @staticmethod
    def setup_logging(environment: str):
        """Setup logging with appropriate level"""
        level = LogConfig.get_log_level(environment)
        
        # Configure root logger
        logging.getLogger().setLevel(level)
        
        # Configure specific loggers
        logging.getLogger("uvicorn").setLevel(logging.INFO)
        logging.getLogger("sqlalchemy.engine").setLevel(
            logging.DEBUG if environment == "development" else logging.WARNING
        )
```

### Rationale
Backend logs should provide clear hierarchy of information severity.