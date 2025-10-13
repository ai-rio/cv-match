"""
LGPD Configuration and Integration

This module provides configuration and integration utilities for the
LGPD compliance system, ensuring all components work together
seamlessly for Brazilian market compliance.

Critical for CV-Match Brazilian market deployment.
"""

import logging
from typing import Any

from pydantic import BaseSettings, Field

logger = logging.getLogger(__name__)


class LGPDSettings(BaseSettings):
    """LGPD compliance configuration settings."""

    # PII Detection Settings
    pii_detection_enabled: bool = Field(True, description="Enable PII detection")
    pii_scan_all_requests: bool = Field(True, description="Scan all requests for PII")
    pii_scan_responses: bool = Field(False, description="Scan responses for PII")
    pii_mask_by_default: bool = Field(True, description="Mask PII by default")
    pii_confidence_threshold: float = Field(0.7, description="Minimum confidence for PII detection")

    # Consent Management Settings
    consent_required_for_all_processing: bool = Field(
        True, description="Require consent for all data processing"
    )
    consent_auto_cleanup: bool = Field(True, description="Automatically clean up expired consents")
    consent_retention_years: int = Field(7, description="Years to retain consent records")

    # Data Retention Settings
    retention_auto_cleanup: bool = Field(
        True, description="Enable automatic data retention cleanup"
    )
    retention_cleanup_frequency_hours: int = Field(
        24, description="Hours between retention cleanup runs"
    )
    retention_default_period_days: int = Field(
        1825, description="Default retention period (5 years)"
    )

    # Audit Trail Settings
    audit_all_data_access: bool = Field(True, description="Audit all data access events")
    audit_retention_days: int = Field(730, description="Days to retain audit logs")
    audit_mask_pii: bool = Field(True, description="Mask PII in audit logs")

    # Data Subject Rights Settings
    data_export_enabled: bool = Field(True, description="Enable data export functionality")
    data_deletion_enabled: bool = Field(True, description="Enable data deletion functionality")
    data_access_response_hours: int = Field(
        30, description="Hours to respond to data access requests"
    )
    data_deletion_response_hours: int = Field(
        30, description="Hours to respond to deletion requests"
    )

    # Compliance Monitoring Settings
    compliance_auto_checks: bool = Field(True, description="Enable automatic compliance checks")
    compliance_alert_threshold: int = Field(5, description="Alert threshold for compliance issues")
    compliance_report_frequency_days: int = Field(7, description="Days between compliance reports")

    # Brazilian Market Specific Settings
    lgpd_brazil_compliant: bool = Field(True, description="Ensure LGPD Brazil compliance")
    brazilian_pii_patterns: bool = Field(
        True, description="Enable Brazilian PII patterns (CPF, RG, etc.)"
    )
    portuguese_localization: bool = Field(
        True, description="Enable Portuguese localization for compliance texts"
    )

    # Security Settings
    encrypt_pii_at_rest: bool = Field(True, description="Encrypt PII at rest")
    encrypt_pii_in_transit: bool = Field(True, description="Encrypt PII in transit")
    secure_audit_logging: bool = Field(True, description="Use secure audit logging")

    class Config:
        env_prefix = "LGPD_"
        case_sensitive = False


class LGPDConfigManager:
    """Manager for LGPD configuration and validation."""

    def __init__(self, settings: LGPDSettings | None = None):
        """
        Initialize LGPD configuration manager.

        Args:
            settings: LGPD settings instance
        """
        self.settings = settings or LGPDSettings()
        self._validate_settings()

    def _validate_settings(self) -> None:
        """Validate LGPD configuration settings."""
        validation_errors = []

        # Validate confidence threshold
        if not 0.0 <= self.settings.pii_confidence_threshold <= 1.0:
            validation_errors.append("PII confidence threshold must be between 0.0 and 1.0")

        # Validate retention periods
        if self.settings.retention_default_period_days < 30:
            validation_errors.append("Default retention period must be at least 30 days")

        if self.settings.consent_retention_years < 1:
            validation_errors.append("Consent retention period must be at least 1 year")

        # Validate response times
        if self.settings.data_access_response_hours < 1:
            validation_errors.append("Data access response time must be at least 1 hour")

        if self.settings.data_deletion_response_hours < 1:
            validation_errors.append("Data deletion response time must be at least 1 hour")

        # Validate Brazilian market settings
        if self.settings.lgpd_brazil_compliant and not self.settings.brazilian_pii_patterns:
            validation_errors.append(
                "Brazilian PII patterns must be enabled for LGPD Brazil compliance"
            )

        if validation_errors:
            error_msg = "LGPD Configuration validation failed: " + "; ".join(validation_errors)
            logger.error(error_msg)
            raise ValueError(error_msg)

        logger.info("LGPD configuration validation passed")

    def get_config_dict(self) -> dict[str, Any]:
        """
        Get configuration as dictionary.

        Returns:
            Configuration dictionary
        """
        return self.settings.dict()

    def is_feature_enabled(self, feature: str) -> bool:
        """
        Check if a specific LGPD feature is enabled.

        Args:
            feature: Feature name

        Returns:
            True if feature is enabled
        """
        feature_mapping = {
            "pii_detection": self.settings.pii_detection_enabled,
            "consent_management": self.settings.consent_required_for_all_processing,
            "data_retention": self.settings.retention_auto_cleanup,
            "audit_trail": self.settings.audit_all_data_access,
            "data_subject_rights": self.settings.data_export_enabled
            and self.settings.data_deletion_enabled,
            "compliance_monitoring": self.settings.compliance_auto_checks,
            "brazilian_compliance": self.settings.lgpd_brazil_compliant,
        }

        return feature_mapping.get(feature, False)

    def get_brazilian_pii_config(self) -> dict[str, Any]:
        """
        Get Brazilian PII configuration.

        Returns:
            Brazilian PII configuration dictionary
        """
        return {
            "enabled": self.settings.brazilian_pii_patterns,
            "patterns": {
                "cpf": {
                    "pattern": r"\b\d{3}\.?\d{3}\.?\d{3}-?\d{2}\b",
                    "description": "Brazilian CPF",
                    "confidence": 0.95,
                },
                "rg": {
                    "pattern": r"\b\d{1,2}\.?\d{3}\.?\d{3}-?[A-Z0-9]?\b",
                    "description": "Brazilian RG",
                    "confidence": 0.85,
                },
                "cnpj": {
                    "pattern": r"\b\d{2}\.?\d{3}\.?\d{3}/?\d{4}-?\d{2}\b",
                    "description": "Brazilian CNPJ",
                    "confidence": 0.95,
                },
                "cep": {
                    "pattern": r"\b\d{5}-?\d{3}\b",
                    "description": "Brazilian CEP",
                    "confidence": 0.90,
                },
            },
            "masking_level": "partial" if self.settings.pii_mask_by_default else "none",
        }

    def get_retention_config(self) -> dict[str, Any]:
        """
        Get data retention configuration.

        Returns:
            Data retention configuration dictionary
        """
        return {
            "auto_cleanup": self.settings.retention_auto_cleanup,
            "cleanup_frequency_hours": self.settings.retention_cleanup_frequency_hours,
            "default_period_days": self.settings.retention_default_period_days,
            "categories": {
                "user_profile": self.settings.retention_default_period_days,
                "resume_data": 730,  # 2 years
                "job_descriptions": 365,  # 1 year
                "optimization_results": 730,  # 2 years
                "usage_analytics": 365,  # 1 year
                "consent_records": self.settings.consent_retention_years * 365,
                "audit_logs": self.settings.audit_retention_days,
            },
        }

    def get_compliance_config(self) -> dict[str, Any]:
        """
        Get compliance monitoring configuration.

        Returns:
            Compliance monitoring configuration dictionary
        """
        return {
            "auto_checks": self.settings.compliance_auto_checks,
            "alert_threshold": self.settings.compliance_alert_threshold,
            "report_frequency_days": self.settings.compliance_report_frequency_days,
            "lgpd_brazil": self.settings.lgpd_brazil_compliant,
            "portuguese_localization": self.settings.portuguese_localization,
            "required_consents": ["data_processing", "ai_processing", "cookies"],
            "optional_consents": ["marketing", "analytics", "data_sharing"],
        }


# Global configuration instance
lgpd_settings = LGPDSettings()
lgpd_config = LGPDConfigManager(lgpd_settings)


def get_lgpd_settings() -> LGPDSettings:
    """
    Get LGPD settings instance.

    Returns:
        LGPD settings
    """
    return lgpd_settings


def get_lgpd_config() -> LGPDConfigManager:
    """
    Get LGPD configuration manager.

    Returns:
        LGPD configuration manager
    """
    return lgpd_config


def is_lgpd_feature_enabled(feature: str) -> bool:
    """
    Check if LGPD feature is enabled.

    Args:
        feature: Feature name

    Returns:
        True if feature is enabled
    """
    return lgpd_config.is_feature_enabled(feature)


# Configuration validation function
def validate_lgpd_configuration() -> bool:
    """
    Validate LGPD configuration.

    Returns:
        True if configuration is valid
    """
    try:
        lgpd_config._validate_settings()
        return True
    except Exception as e:
        logger.error(f"LGPD configuration validation failed: {e}")
        return False


# Startup configuration check
def initialize_lgpd_system() -> dict[str, Any]:
    """
    Initialize LGPD compliance system.

    Returns:
        Initialization status
    """
    try:
        logger.info("Initializing LGPD compliance system...")

        # Validate configuration
        if not validate_lgpd_configuration():
            return {"status": "error", "message": "Configuration validation failed"}

        # Check required features for Brazilian market
        required_features = [
            "pii_detection",
            "consent_management",
            "audit_trail",
            "brazilian_compliance",
        ]
        missing_features = []

        for feature in required_features:
            if not is_lgpd_feature_enabled(feature):
                missing_features.append(feature)

        if missing_features:
            logger.error(f"Missing required LGPD features: {missing_features}")
            return {
                "status": "error",
                "message": f"Missing required features: {', '.join(missing_features)}",
            }

        # Log successful initialization
        logger.info("LGPD compliance system initialized successfully")
        logger.info(f"Brazilian market compliance: {lgpd_settings.lgpd_brazil_compliant}")
        logger.info(f"PII detection enabled: {lgpd_settings.pii_detection_enabled}")
        logger.info(f"Brazilian PII patterns: {lgpd_settings.brazilian_pii_patterns}")

        return {
            "status": "success",
            "message": "LGPD compliance system initialized successfully",
            "brazilian_compliant": lgpd_settings.lgpd_brazil_compliant,
            "enabled_features": [
                feature
                for feature in [
                    "pii_detection",
                    "consent_management",
                    "data_retention",
                    "audit_trail",
                    "data_subject_rights",
                    "compliance_monitoring",
                ]
                if is_lgpd_feature_enabled(feature)
            ],
        }

    except Exception as e:
        logger.error(f"Failed to initialize LGPD system: {e}")
        return {"status": "error", "message": f"Initialization failed: {str(e)}"}
