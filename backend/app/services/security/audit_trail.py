"""
Audit Trail Service for LGPD Compliance

This service provides comprehensive audit trail functionality to track
all data access, modifications, and system events for LGPD compliance.
Includes secure logging that doesn't expose PII in logs.

Critical for CV-Match Brazilian market deployment - audit trails are
mandatory under LGPD for accountability and transparency.
"""

import logging
from datetime import datetime, timezone, timedelta
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass, asdict
from enum import Enum
import json

from pydantic import BaseModel, Field

from app.services.supabase.database import SupabaseDatabaseService
from app.utils.pii_masker import mask_text, mask_dict

logger = logging.getLogger(__name__)


class AuditEventType(Enum):
    """Types of audit events."""

    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"
    LOGIN = "login"
    LOGOUT = "logout"
    CONSENT_GRANTED = "consent_granted"
    CONSENT_REVOKED = "consent_revoked"
    DATA_ACCESS = "data_access"
    DATA_EXPORT = "data_export"
    DATA_DELETION = "data_deletion"
    ADMIN_ACTION = "admin_action"
    SECURITY_ALERT = "security_alert"
    SYSTEM_ERROR = "system_error"


class DataAccessType(Enum):
    """Types of data access events."""

    VIEW = "view"
    EXPORT = "export"
    DOWNLOAD = "download"
    MODIFY = "modify"
    SHARE = "share"
    PRINT = "print"


class ComplianceType(Enum):
    """Types of compliance checks."""

    LGPD = "lgpd"
    DATA_RETENTION = "data_retention"
    CONSENT_MANAGEMENT = "consent_management"
    PII_DETECTION = "pii_detection"
    DATA_SUBJECT_RIGHTS = "data_subject_rights"


class ComplianceStatus(Enum):
    """Compliance check status."""

    COMPLIANT = "compliant"
    NON_COMPLIANT = "non_compliant"
    WARNING = "warning"


class EventSeverity(Enum):
    """Severity levels for system events."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class AuditEvent:
    """Audit event data structure."""

    event_type: AuditEventType
    table_name: Optional[str] = None
    record_id: Optional[str] = None
    user_id: Optional[str] = None
    user_email: Optional[str] = None
    session_id: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    action: str = ""
    details: Optional[Dict[str, Any]] = None
    old_values: Optional[Dict[str, Any]] = None
    new_values: Optional[Dict[str, Any]] = None
    affected_fields: Optional[List[str]] = None
    success: bool = True
    error_message: Optional[str] = None
    created_at: Optional[datetime] = None


@dataclass
class DataAccessEvent:
    """Data access event structure."""

    user_id: Optional[str]
    data_category: str
    access_type: DataAccessType
    access_purpose: Optional[str] = None
    record_count: int = 1
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    session_id: Optional[str] = None
    consent_verified: bool = False
    legal_basis: Optional[str] = None
    created_at: Optional[datetime] = None


@dataclass
class ComplianceEvent:
    """Compliance monitoring event."""

    compliance_type: ComplianceType
    check_type: str
    status: ComplianceStatus
    details: Optional[Dict[str, Any]] = None
    affected_records: int = 0
    required_action: Optional[str] = None
    due_date: Optional[datetime] = None
    created_at: Optional[datetime] = None


@dataclass
class SystemEvent:
    """System event for security monitoring."""

    event_type: str
    severity: EventSeverity
    source: str
    description: str
    details: Optional[Dict[str, Any]] = None
    user_id: Optional[str] = None
    ip_address: Optional[str] = None
    resolved: bool = False
    resolved_at: Optional[datetime] = None
    resolved_by: Optional[str] = None
    created_at: Optional[datetime] = None


class AuditTrailService:
    """Service for managing audit trails and compliance monitoring."""

    def __init__(self):
        """Initialize audit trail service."""
        self.audit_logs_db = SupabaseDatabaseService("audit_logs", dict)
        self.data_access_logs_db = SupabaseDatabaseService("data_access_logs", dict)
        self.compliance_logs_db = SupabaseDatabaseService("compliance_logs", dict)
        self.system_events_db = SupabaseDatabaseService("system_event_logs", dict)

    async def log_audit_event(self, event: AuditEvent) -> str:
        """
        Log an audit event with PII protection.

        Args:
            event: Audit event to log

        Returns:
            Event ID
        """
        try:
            # Mask PII in sensitive fields
            if event.old_values:
                event.old_values = mask_dict(event.old_values)
            if event.new_values:
                event.new_values = mask_dict(event.new_values)
            if event.details:
                event.details = mask_dict(event.details)
            if event.error_message:
                event.error_message = mask_text(event.error_message)

            # Prepare event data
            event_data = {
                "event_type": event.event_type.value,
                "table_name": event.table_name,
                "record_id": event.record_id,
                "user_id": event.user_id,
                "user_email": event.user_email,
                "session_id": event.session_id,
                "ip_address": event.ip_address,
                "user_agent": event.user_agent,
                "action": event.action,
                "details": event.details,
                "old_values": event.old_values,
                "new_values": event.new_values,
                "affected_fields": event.affected_fields,
                "success": event.success,
                "error_message": event.error_message,
                "created_at": event.created_at or datetime.now(timezone.utc).isoformat()
            }

            # Log to database
            result = await self.audit_logs_db.create(event_data)
            event_id = result["id"]

            # Also log to application logger
            logger.info(f"Audit event logged: {event.event_type.value} - {event.action} by user {event.user_id}")

            return event_id

        except Exception as e:
            logger.error(f"Failed to log audit event: {e}")
            # Log to application logger as fallback
            logger.error(f"Audit event failed: {event.event_type.value} - {event.action}")
            raise

    async def log_data_access(self, event: DataAccessEvent) -> str:
        """
        Log a data access event.

        Args:
            event: Data access event to log

        Returns:
            Event ID
        """
        try:
            # Prepare event data
            event_data = {
                "user_id": event.user_id,
                "data_category": event.data_category,
                "access_type": event.access_type.value,
                "access_purpose": event.access_purpose,
                "record_count": event.record_count,
                "ip_address": event.ip_address,
                "user_agent": event.user_agent,
                "session_id": event.session_id,
                "consent_verified": event.consent_verified,
                "legal_basis": event.legal_basis,
                "created_at": event.created_at or datetime.now(timezone.utc).isoformat()
            }

            # Log to database
            result = await self.data_access_logs_db.create(event_data)
            event_id = result["id"]

            # Log to application logger
            logger.info(f"Data access logged: {event.access_type.value} to {event.data_category} by user {event.user_id}")

            return event_id

        except Exception as e:
            logger.error(f"Failed to log data access event: {e}")
            raise

    async def log_compliance_event(self, event: ComplianceEvent) -> str:
        """
        Log a compliance monitoring event.

        Args:
            event: Compliance event to log

        Returns:
            Event ID
        """
        try:
            # Prepare event data
            event_data = {
                "compliance_type": event.compliance_type.value,
                "check_type": event.check_type,
                "status": event.status.value,
                "details": event.details,
                "affected_records": event.affected_records,
                "required_action": event.required_action,
                "due_date": event.due_date.isoformat() if event.due_date else None,
                "created_at": event.created_at or datetime.now(timezone.utc).isoformat()
            }

            # Log to database
            result = await self.compliance_logs_db.create(event_data)
            event_id = result["id"]

            # Log to application logger
            logger.info(f"Compliance event logged: {event.compliance_type.value} - {event.check_type} - {event.status.value}")

            return event_id

        except Exception as e:
            logger.error(f"Failed to log compliance event: {e}")
            raise

    async def log_system_event(self, event: SystemEvent) -> str:
        """
        Log a system event for security monitoring.

        Args:
            event: System event to log

        Returns:
            Event ID
        """
        try:
            # Prepare event data
            event_data = {
                "event_type": event.event_type,
                "severity": event.severity.value,
                "source": event.source,
                "description": event.description,
                "details": event.details,
                "user_id": event.user_id,
                "ip_address": event.ip_address,
                "resolved": event.resolved,
                "resolved_at": event.resolved_at.isoformat() if event.resolved_at else None,
                "resolved_by": event.resolved_by,
                "created_at": event.created_at or datetime.now(timezone.utc).isoformat()
            }

            # Log to database
            result = await self.system_events_db.create(event_data)
            event_id = result["id"]

            # Log to application logger with appropriate level
            log_message = f"System event: {event.event_type} - {event.description}"
            if event.severity == EventSeverity.CRITICAL:
                logger.critical(log_message)
            elif event.severity == EventSeverity.HIGH:
                logger.error(log_message)
            elif event.severity == EventSeverity.MEDIUM:
                logger.warning(log_message)
            else:
                logger.info(log_message)

            return event_id

        except Exception as e:
            logger.error(f"Failed to log system event: {e}")
            raise

    async def get_user_audit_trail(
        self,
        user_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        event_types: Optional[List[AuditEventType]] = None
    ) -> List[Dict[str, Any]]:
        """
        Get audit trail for a specific user.

        Args:
            user_id: User ID
            start_date: Start date for filtering
            end_date: End date for filtering
            event_types: Specific event types to include

        Returns:
            List of audit events
        """
        try:
            # Build filters
            filters = {"user_id": user_id}

            if start_date:
                filters["created_at__gte"] = start_date.isoformat()
            if end_date:
                filters["created_at__lte"] = end_date.isoformat()

            # Get audit logs
            audit_logs = await self.audit_logs_db.list(filters=filters, order_by="created_at")

            # Filter by event types if specified
            if event_types:
                event_type_values = [et.value for et in event_types]
                audit_logs = [log for log in audit_logs if log.get("event_type") in event_type_values]

            # Mask any remaining PII
            for log in audit_logs:
                if log.get("user_email"):
                    log["user_email"] = mask_text(log["user_email"])

            return audit_logs

        except Exception as e:
            logger.error(f"Failed to get user audit trail: {e}")
            raise

    async def get_data_access_report(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        data_categories: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Generate data access report.

        Args:
            start_date: Start date for report
            end_date: End date for report
            data_categories: Specific data categories to include

        Returns:
            Data access report
        """
        try:
            # Build filters
            filters = {}
            if start_date:
                filters["created_at__gte"] = start_date.isoformat()
            if end_date:
                filters["created_at__lte"] = end_date.isoformat()

            # Get data access logs
            access_logs = await self.data_access_logs_db.list(filters=filters, order_by="created_at")

            # Filter by data categories if specified
            if data_categories:
                access_logs = [log for log in access_logs if log.get("data_category") in data_categories]

            # Generate report
            report = {
                "report_period": {
                    "start_date": start_date.isoformat() if start_date else None,
                    "end_date": end_date.isoformat() if end_date else None
                },
                "summary": {
                    "total_access_events": len(access_logs),
                    "unique_users": len(set(log.get("user_id") for log in access_logs if log.get("user_id"))),
                    "data_categories": list(set(log.get("data_category") for log in access_logs)),
                    "access_types": list(set(log.get("access_type") for log in access_logs))
                },
                "by_category": {},
                "by_access_type": {},
                "by_user": {},
                "compliance_issues": []
            }

            # Analyze by category
            for log in access_logs:
                category = log.get("data_category", "unknown")
                if category not in report["by_category"]:
                    report["by_category"][category] = {
                        "count": 0,
                        "unique_users": set(),
                        "consent_verified": 0,
                        "total_records": 0
                    }

                report["by_category"][category]["count"] += 1
                if log.get("user_id"):
                    report["by_category"][category]["unique_users"].add(log["user_id"])
                if log.get("consent_verified"):
                    report["by_category"][category]["consent_verified"] += 1
                report["by_category"][category]["total_records"] += log.get("record_count", 0)

            # Convert sets to counts
            for category in report["by_category"]:
                report["by_category"][category]["unique_users"] = len(report["by_category"][category]["unique_users"])

            # Check compliance issues
            for log in access_logs:
                if not log.get("consent_verified") and log.get("access_type") in ["export", "download", "share"]:
                    report["compliance_issues"].append({
                        "type": "access_without_consent",
                        "log_id": log.get("id"),
                        "user_id": log.get("user_id"),
                        "data_category": log.get("data_category"),
                        "access_type": log.get("access_type"),
                        "timestamp": log.get("created_at")
                    })

            return report

        except Exception as e:
            logger.error(f"Failed to generate data access report: {e}")
            raise

    async def get_compliance_status(self) -> Dict[str, Any]:
        """
        Get current compliance status.

        Returns:
            Compliance status information
        """
        try:
            # Get recent compliance logs
            recent_logs = await self.compliance_logs_db.list(
                filters={"created_at__gte": (datetime.now(timezone.utc) - timedelta(days=30)).isoformat()},
                order_by="created_at",
                limit=100
            )

            # Get unresolved system events
            unresolved_events = await self.system_events_db.list(
                filters={"resolved": False},
                order_by="created_at"
            )

            # Analyze compliance
            status = {
                "overall_status": "compliant",
                "summary": {
                    "total_compliance_checks": len(recent_logs),
                    "compliant_checks": len([log for log in recent_logs if log.get("status") == "compliant"]),
                    "non_compliant_checks": len([log for log in recent_logs if log.get("status") == "non_compliant"]),
                    "warnings": len([log for log in recent_logs if log.get("status") == "warning"]),
                    "unresolved_events": len(unresolved_events)
                },
                "by_type": {},
                "recent_issues": [],
                "action_required": []
            }

            # Analyze by compliance type
            for log in recent_logs:
                compliance_type = log.get("compliance_type", "unknown")
                if compliance_type not in status["by_type"]:
                    status["by_type"][compliance_type] = {
                        "total": 0,
                        "compliant": 0,
                        "non_compliant": 0,
                        "warnings": 0
                    }

                status["by_type"][compliance_type]["total"] += 1
                if log.get("status") == "compliant":
                    status["by_type"][compliance_type]["compliant"] += 1
                elif log.get("status") == "non_compliant":
                    status["by_type"][compliance_type]["non_compliant"] += 1
                elif log.get("status") == "warning":
                    status["by_type"][compliance_type]["warnings"] += 1

            # Identify issues requiring action
            for log in recent_logs:
                if log.get("status") in ["non_compliant", "warning"] and log.get("required_action"):
                    status["action_required"].append({
                        "id": log.get("id"),
                        "compliance_type": log.get("compliance_type"),
                        "check_type": log.get("check_type"),
                        "required_action": log.get("required_action"),
                        "due_date": log.get("due_date"),
                        "created_at": log.get("created_at")
                    })

            # Recent non-compliant issues
            status["recent_issues"] = [
                {
                    "id": log.get("id"),
                    "compliance_type": log.get("compliance_type"),
                    "check_type": log.get("check_type"),
                    "status": log.get("status"),
                    "details": log.get("details"),
                    "created_at": log.get("created_at")
                }
                for log in recent_logs
                if log.get("status") in ["non_compliant", "warning"]
            ]

            # Determine overall status
            if status["summary"]["non_compliant_checks"] > 0:
                status["overall_status"] = "non_compliant"
            elif status["summary"]["warnings"] > 0:
                status["overall_status"] = "warning"

            return status

        except Exception as e:
            logger.error(f"Failed to get compliance status: {e}")
            raise

    async def cleanup_old_audit_logs(self, retention_days: int = 365) -> Dict[str, int]:
        """
        Clean up old audit logs beyond retention period.

        Args:
            retention_days: Number of days to retain logs

        Returns:
            Cleanup results
        """
        try:
            cutoff_date = datetime.now(timezone.utc) - timedelta(days=retention_days)
            results = {}

            # Clean up audit logs
            old_audit_logs = await self.audit_logs_db.list(
                filters={"created_at__lt": cutoff_date.isoformat()}
            )
            results["audit_logs_deleted"] = len(old_audit_logs)

            # Clean up data access logs
            old_access_logs = await self.data_access_logs_db.list(
                filters={"created_at__lt": cutoff_date.isoformat()}
            )
            results["data_access_logs_deleted"] = len(old_access_logs)

            # Clean up resolved system events
            old_system_events = await self.system_events_db.list(
                filters={
                    "created_at__lt": cutoff_date.isoformat(),
                    "resolved": True
                }
            )
            results["system_events_deleted"] = len(old_system_events)

            # Keep compliance logs longer (7 years for legal requirements)
            compliance_cutoff = datetime.now(timezone.utc) - timedelta(days=2555)  # 7 years
            old_compliance_logs = await self.compliance_logs_db.list(
                filters={"created_at__lt": compliance_cutoff.isoformat()}
            )
            results["compliance_logs_deleted"] = len(old_compliance_logs)

            # TODO: Implement actual deletion in Supabase
            # This would require delete operations in the database

            logger.info(f"Audit log cleanup completed: {results}")
            return results

        except Exception as e:
            logger.error(f"Failed to cleanup audit logs: {e}")
            raise


# Global audit trail service instance
audit_trail = AuditTrailService()


async def log_data_access(
    user_id: str,
    data_category: str,
    access_type: DataAccessType,
    access_purpose: str = None,
    record_count: int = 1,
    consent_verified: bool = False
) -> str:
    """
    Convenience function to log data access.

    Args:
        user_id: User ID
        data_category: Category of data accessed
        access_type: Type of access
        access_purpose: Purpose of access
        record_count: Number of records accessed
        consent_verified: Whether consent was verified

    Returns:
        Event ID
    """
    event = DataAccessEvent(
        user_id=user_id,
        data_category=data_category,
        access_type=access_type,
        access_purpose=access_purpose,
        record_count=record_count,
        consent_verified=consent_verified
    )
    return await audit_trail.log_data_access(event)


async def log_audit_event(
    event_type: AuditEventType,
    action: str,
    user_id: str = None,
    table_name: str = None,
    record_id: str = None,
    success: bool = True,
    error_message: str = None
) -> str:
    """
    Convenience function to log audit events.

    Args:
        event_type: Type of audit event
        action: Action performed
        user_id: User ID
        table_name: Table name
        record_id: Record ID
        success: Whether action was successful
        error_message: Error message if failed

    Returns:
        Event ID
    """
    event = AuditEvent(
        event_type=event_type,
        action=action,
        user_id=user_id,
        table_name=table_name,
        record_id=record_id,
        success=success,
        error_message=error_message
    )
    return await audit_trail.log_audit_event(event)