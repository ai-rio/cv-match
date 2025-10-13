"""
Sentry configuration for CV-Match Backend
Configures error tracking and performance monitoring for FastAPI application
"""

import logging

import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.httpx import HttpxIntegration
from sentry_sdk.integrations.logging import LoggingIntegration
from sentry_sdk.integrations.starlette import StarletteIntegration

from app.core.config import settings

logger = logging.getLogger(__name__)


class SentryConfig:
    """Sentry configuration management for CV-Match backend"""

    def __init__(self):
        self.dsn: str | None = None
        self.environment: str | None = None
        self.enabled: bool = False

    def load_config(self):
        """Load Sentry configuration from environment"""
        self.dsn = settings.SENTRY_DSN
        self.environment = settings.ENVIRONMENT
        self.enabled = bool(self.dsn and self.dsn.strip())

        if self.enabled:
            logger.info(f"Sentry enabled for environment: {self.environment}")
        else:
            logger.info("Sentry disabled - no DSN configured")

    def init_sentry(self):
        """Initialize Sentry SDK with Brazilian market context"""
        if not self.enabled:
            logger.info("Skipping Sentry initialization - disabled")
            return

        try:
            # Configure logging integration
            logging_integration = LoggingIntegration(
                level=logging.INFO,  # Capture info and above as breadcrumbs
                event_level=logging.ERROR,  # Send errors as events
            )

            sentry_sdk.init(
                dsn=self.dsn,
                environment=self.environment,
                # Set traces_sample_rate to 1.0 to capture 100%
                # of transactions for performance monitoring.
                traces_sample_rate=1.0,
                # Configure profiles_sample_rate to capture performance profiles
                profiles_sample_rate=1.0,
                # Integrations for FastAPI ecosystem
                integrations=[
                    FastApiIntegration(transaction_style="endpoint"),
                    StarletteIntegration(transaction_style="url"),
                    logging_integration,
                    HttpxIntegration(),
                ],
                # Brazilian market context
                before_send=self._add_brazilian_context,
                before_breadcrumb=self._add_brazilian_breadcrumb_context,
                # Custom tags for Brazilian SaaS context
                release=self._get_release_version(),
                # Performance monitoring settings
                send_default_pii=False,  # Privacy compliance for LGPD
                # Debug mode for development
                debug=self.environment == "development",
                # Maximum number of breadcrumbs to capture
                max_breadcrumbs=50,
                # Error sampling rate
                sample_rate=1.0,
            )

            logger.info("Sentry initialized successfully for CV-Match backend")

        except Exception as e:
            logger.error(f"Failed to initialize Sentry: {e}")

    def _add_brazilian_context(self, event, hint):
        """Add Brazilian market context to Sentry events"""
        if event is None:
            return event

        # Add Brazilian market tags
        event.setdefault("tags", {}).update(
            {
                "market": "brazil",
                "currency": "BRL",
                "locale": "pt-BR",
                "region": "latam",
                "saas_type": "resume-matching",
                "compliance": "LGPD",
            }
        )

        # Add custom context for Brazilian business logic
        event.setdefault("extra", {}).update(
            {
                "market_context": {
                    "country": "BR",
                    "currency": "BRL",
                    "language": "pt-BR",
                    "timezone": "America/Sao_Paulo",
                    "business_model": "SaaS",
                    "industry": "HR_Tech",
                }
            }
        )

        # Localize error messages for development
        if self.environment == "development" and "exception" in event:
            exception = event["exception"]
            if exception and "values" in exception:
                for exc_value in exception["values"]:
                    if exc_value.get("type") == "ValidationError":
                        # Portuguese validation error messages
                        if "email" in str(exc_value.get("value", "")).lower():
                            exc_value["value"] = "Erro de validação: formato de e-mail inválido"
                        elif "cpf" in str(exc_value.get("value", "")).lower():
                            exc_value["value"] = "Erro de validação: formato de CPF inválido"
                        elif "cnpj" in str(exc_value.get("value", "")).lower():
                            exc_value["value"] = "Erro de validação: formato de CNPJ inválido"

        return event

    def _add_brazilian_breadcrumb_context(self, breadcrumb, hint):
        """Add Brazilian context to breadcrumbs"""
        if breadcrumb is None:
            return breadcrumb

        # Add market context to breadcrumbs
        breadcrumb.setdefault("data", {}).update({"market": "brazil", "locale": "pt-BR"})

        return breadcrumb

    def _get_release_version(self) -> str:
        """Get release version from environment or default"""
        import os

        return os.getenv("APP_VERSION", "cv-match@1.0.0")

    def set_user_context(self, user_id: str, email: str = None, **kwargs):
        """Set user context for Brazilian users"""
        if not self.enabled:
            return

        user_data = {"id": user_id, "locale": "pt-BR", "market": "brazil"}

        if email:
            user_data["email"] = email

        # Add Brazilian-specific user context
        brazilian_context = {"currency": "BRL", "country": "BR", "timezone": "America/Sao_Paulo"}
        user_data.update(brazilian_context)
        user_data.update(kwargs)

        sentry_sdk.set_user(user_data)

    def set_transaction_name(self, name: str):
        """Set transaction name with Brazilian context"""
        if self.enabled:
            # Note: set_transaction is deprecated in newer Sentry versions
            # Transaction naming is handled automatically by FastAPI integration
            pass

    def add_breadcrumb(self, message: str, category: str = "default", level: str = "info"):
        """Add breadcrumb with Brazilian context"""
        if self.enabled:
            sentry_sdk.add_breadcrumb(
                message=message,
                category=category,
                level=level,
                data={"market": "brazil", "locale": "pt-BR"},
            )

    def capture_exception(self, exception: Exception, context: dict = None):
        """Capture exception with Brazilian context"""
        if not self.enabled:
            return

        extra_data = {"market": "brazil", "locale": "pt-BR", "application": "cv-match-backend"}

        if context:
            extra_data.update(context)

        sentry_sdk.capture_exception(exception, extra=extra_data)

    def capture_message(self, message: str, level: str = "info", context: dict = None):
        """Capture message with Brazilian context"""
        if not self.enabled:
            return

        extra_data = {"market": "brazil", "locale": "pt-BR", "application": "cv-match-backend"}

        if context:
            extra_data.update(context)

        sentry_sdk.capture_message(message, level=level, extra=extra_data)


# Global Sentry configuration instance
sentry_config = SentryConfig()


def init_sentry():
    """Initialize Sentry for the FastAPI application"""
    sentry_config.load_config()
    sentry_config.init_sentry()


def get_sentry_config() -> SentryConfig:
    """Get the global Sentry configuration instance"""
    return sentry_config
