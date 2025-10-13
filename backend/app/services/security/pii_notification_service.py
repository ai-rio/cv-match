"""
PII Notification Service for LGPD Compliance

This service provides user notification functionality when PII is detected
and masked in their uploaded documents, ensuring transparency and compliance
with LGPD requirements.

Critical for CV-Match Brazilian market deployment - user notification
about PII processing is mandatory under LGPD.
"""

import logging
from dataclasses import dataclass
from datetime import UTC, datetime
from enum import Enum
from typing import Any

from app.services.security.audit_trail import AuditEvent, AuditEventType, audit_trail
from app.services.supabase.database import SupabaseDatabaseService

logger = logging.getLogger(__name__)


class NotificationType(Enum):
    """Types of PII notifications."""

    PII_DETECTED_RESUME = "pii_detected_resume"
    PII_DETECTED_JOB = "pii_detected_job"
    PII_MASKING_COMPLETED = "pii_masking_completed"
    PII_REVIEW_REQUIRED = "pii_review_required"
    LGPD_COMPLIANCE_INFO = "lgpd_compliance_info"


class NotificationPriority(Enum):
    """Priority levels for notifications."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class PIINotification:
    """PII detection notification data structure."""

    user_id: str
    notification_type: NotificationType
    priority: NotificationPriority
    title: str
    message: str
    pii_types_found: list[str]
    document_type: str
    document_id: str
    document_name: str
    confidence_score: float
    scan_duration_ms: float
    characters_masked: int
    requires_action: bool = False
    action_deadline: datetime | None = None
    additional_details: dict[str, Any] | None = None
    created_at: datetime | None = None
    read_at: datetime | None = None


@dataclass
class NotificationPreferences:
    """User notification preferences."""

    user_id: str
    email_notifications: bool = True
    in_app_notifications: bool = True
    pii_notifications: bool = True
    high_priority_only: bool = False
    created_at: datetime | None = None
    updated_at: datetime | None = None


class PIINotificationService:
    """Service for managing PII detection notifications."""

    def __init__(self):
        """Initialize PII notification service."""
        self.notifications_db = SupabaseDatabaseService("pii_notifications", dict)
        self.preferences_db = SupabaseDatabaseService("notification_preferences", dict)

    async def create_notification(self, notification: PIINotification) -> str | None:
        """
        Create and store a PII notification.

        Args:
            notification: PII notification to create

        Returns:
            Notification ID or None if notification was skipped
        """
        try:
            # Check user preferences before creating notification
            preferences = await self.get_user_preferences(notification.user_id)

            # Skip if user has disabled PII notifications
            if not preferences.pii_notifications:
                logger.info(f"User {notification.user_id} has disabled PII notifications")
                return None

            # Skip low priority notifications if user only wants high priority
            if preferences.high_priority_only and notification.priority in [
                NotificationPriority.LOW,
                NotificationPriority.MEDIUM,
            ]:
                logger.info(f"Skipping low priority notification for user {notification.user_id}")
                return None

            # Prepare notification data
            notification_data = {
                "user_id": notification.user_id,
                "notification_type": notification.notification_type.value,
                "priority": notification.priority.value,
                "title": notification.title,
                "message": notification.message,
                "pii_types_found": notification.pii_types_found,
                "document_type": notification.document_type,
                "document_id": notification.document_id,
                "document_name": notification.document_name,
                "confidence_score": notification.confidence_score,
                "scan_duration_ms": notification.scan_duration_ms,
                "characters_masked": notification.characters_masked,
                "requires_action": notification.requires_action,
                "action_deadline": notification.action_deadline.isoformat()
                if notification.action_deadline
                else None,
                "additional_details": notification.additional_details,
                "created_at": notification.created_at or datetime.now(UTC).isoformat(),
                "read_at": None,
            }

            # Store notification
            result = await self.notifications_db.create(notification_data)
            notification_id = result["id"]

            # Log notification creation for audit
            await self._log_notification_created(notification, notification_id)

            # Send notification based on user preferences
            await self._send_notification(notification, notification_id, preferences)

            logger.info(
                f"PII notification {notification_id} created for user {notification.user_id}"
            )
            return notification_id

        except Exception as e:
            logger.error(f"Failed to create PII notification: {e}")
            raise

    async def create_pii_detected_notification(
        self,
        user_id: str,
        document_type: str,
        document_id: str,
        document_name: str,
        pii_types_found: list[str],
        confidence_score: float,
        scan_duration_ms: float,
        characters_masked: int,
    ) -> str | None:
        """
        Create a standardized PII detected notification.

        Args:
            user_id: User ID
            document_type: Type of document (resume/job)
            document_id: Document ID
            document_name: Original document name
            pii_types_found: List of PII types detected
            confidence_score: Detection confidence score
            scan_duration_ms: Scan duration in milliseconds
            characters_masked: Number of characters masked

        Returns:
            Notification ID
        """
        # Determine priority based on PII types and confidence
        critical_pii_types = ["cpf", "email", "phone"]
        has_critical_pii = any(pii in critical_pii_types for pii in pii_types_found)

        if confidence_score > 0.9 and has_critical_pii:
            priority = NotificationPriority.HIGH
            requires_action = True
        elif confidence_score > 0.7:
            priority = NotificationPriority.MEDIUM
            requires_action = False
        else:
            priority = NotificationPriority.LOW
            requires_action = False

        # Create localized messages for Brazilian users
        if document_type == "resume":
            title = "🔒 Informações Pessoais Detectadas no Currículo"
            message = (
                f"Detectamos e protegemos {len(pii_types_found)} tipo(s) de informações pessoais "
                f"no seu currículo '{document_name}'. Para sua segurança e conformidade com a "
                f"Lei LGPD, estes dados foram mascarados automaticamente antes do armazenamento."
            )
        else:  # job
            title = "🔒 Informações Pessoais Detectadas na Vaga"
            message = (
                f"Detectamos e protegemos {len(pii_types_found)} tipo(s) de informações pessoais "
                f"na descrição da vaga. Para conformidade com a Lei LGPD, estes dados foram "
                f"mascarados automaticamente."
            )

        # Add PII details to message
        pii_type_names = {
            "cpf": "CPF",
            "rg": "RG",
            "cnpj": "CNPJ",
            "email": "E-mail",
            "phone": "Telefone",
            "postal_code": "CEP",
            "address": "Endereço",
            "credit_card": "Cartão de Crédito",
            "bank_account": "Conta Bancária",
        }

        detected_pii_names = [pii_type_names.get(pii, pii.upper()) for pii in pii_types_found]
        message += f"\n\n📋 Tipos de dados detectados: {', '.join(detected_pii_names)}"
        message += f"\n🛡️ {characters_masked} caracteres foram protegidos"
        message += f"\n⚡ Tempo de verificação: {scan_duration_ms:.1f}ms"

        if requires_action:
            message += (
                "\n\n⚠️ **Recomendamos revisar o documento** para garantir que as "
                "informações essenciais foram preservadas."
            )

        notification = PIINotification(
            user_id=user_id,
            notification_type=NotificationType.PII_DETECTED_RESUME
            if document_type == "resume"
            else NotificationType.PII_DETECTED_JOB,
            priority=priority,
            title=title,
            message=message,
            pii_types_found=pii_types_found,
            document_type=document_type,
            document_id=document_id,
            document_name=document_name,
            confidence_score=confidence_score,
            scan_duration_ms=scan_duration_ms,
            characters_masked=characters_masked,
            requires_action=requires_action,
            additional_details={
                "pii_display_names": detected_pii_names,
                "detection_summary": {
                    "total_pii_types": len(pii_types_found),
                    "has_critical_pii": has_critical_pii,
                    "confidence_level": "alta"
                    if confidence_score > 0.8
                    else "média"
                    if confidence_score > 0.6
                    else "baixa",
                },
            },
        )

        return await self.create_notification(notification)

    async def get_user_notifications(
        self,
        user_id: str,
        unread_only: bool = False,
        limit: int = 50,
        offset: int = 0,
    ) -> list[dict[str, Any]]:
        """
        Get notifications for a user.

        Args:
            user_id: User ID
            unread_only: Whether to return only unread notifications
            limit: Maximum number of notifications to return
            offset: Number of notifications to skip

        Returns:
            List of notifications
        """
        try:
            filters = {"user_id": user_id}
            if unread_only:
                filters["read_at"] = None

            notifications = await self.notifications_db.list(
                filters=filters,
                order_by="created_at",
                order_desc=True,
                limit=limit,
                offset=offset,
            )

            return notifications

        except Exception as e:
            logger.error(f"Failed to get notifications for user {user_id}: {e}")
            raise

    async def mark_notification_read(self, notification_id: str, user_id: str) -> bool:
        """
        Mark a notification as read.

        Args:
            notification_id: Notification ID
            user_id: User ID (for authorization)

        Returns:
            True if successful, False otherwise
        """
        try:
            # Update notification
            update_data = {
                "read_at": datetime.now(UTC).isoformat(),
            }

            result = await self.notifications_db.update(
                record_id=notification_id,
                data=update_data,
                filters={"user_id": user_id},  # Ensure user owns the notification
            )

            if result:
                await self._log_notification_read(notification_id, user_id)
                logger.info(f"Notification {notification_id} marked as read by user {user_id}")
                return True
            else:
                logger.warning(f"Failed to mark notification {notification_id} as read")
                return False

        except Exception as e:
            logger.error(f"Failed to mark notification {notification_id} as read: {e}")
            return False

    async def get_user_preferences(self, user_id: str) -> NotificationPreferences:
        """
        Get notification preferences for a user.

        Args:
            user_id: User ID

        Returns:
            User notification preferences
        """
        try:
            # Try to get existing preferences
            preferences_data = await self.preferences_db.get(filters={"user_id": user_id})

            if preferences_data:
                return NotificationPreferences(
                    user_id=preferences_data["user_id"],
                    email_notifications=preferences_data.get("email_notifications", True),
                    in_app_notifications=preferences_data.get("in_app_notifications", True),
                    pii_notifications=preferences_data.get("pii_notifications", True),
                    high_priority_only=preferences_data.get("high_priority_only", False),
                    created_at=datetime.fromisoformat(preferences_data["created_at"])
                    if preferences_data.get("created_at")
                    else None,
                    updated_at=datetime.fromisoformat(preferences_data["updated_at"])
                    if preferences_data.get("updated_at")
                    else None,
                )
            else:
                # Create default preferences
                default_preferences = NotificationPreferences(user_id=user_id)
                await self.update_user_preferences(default_preferences)
                return default_preferences

        except Exception as e:
            logger.error(f"Failed to get preferences for user {user_id}: {e}")
            # Return default preferences on error
            return NotificationPreferences(user_id=user_id)

    async def update_user_preferences(self, preferences: NotificationPreferences) -> bool:
        """
        Update notification preferences for a user.

        Args:
            preferences: Updated preferences

        Returns:
            True if successful, False otherwise
        """
        try:
            preferences_data = {
                "user_id": preferences.user_id,
                "email_notifications": preferences.email_notifications,
                "in_app_notifications": preferences.in_app_notifications,
                "pii_notifications": preferences.pii_notifications,
                "high_priority_only": preferences.high_priority_only,
                "updated_at": datetime.now(UTC).isoformat(),
            }

            # Check if preferences exist
            existing = await self.preferences_db.get(filters={"user_id": preferences.user_id})

            if existing:
                # Update existing preferences
                result = await self.preferences_db.update(
                    record_id=existing["id"], data=preferences_data
                )
            else:
                # Create new preferences
                preferences_data["created_at"] = datetime.now(UTC).isoformat()
                result = await self.preferences_db.create(preferences_data)

            if result:
                logger.info(f"Updated notification preferences for user {preferences.user_id}")
                return True
            else:
                logger.warning(f"Failed to update preferences for user {preferences.user_id}")
                return False

        except Exception as e:
            logger.error(f"Failed to update preferences for user {preferences.user_id}: {e}")
            return False

    async def _send_notification(
        self,
        notification: PIINotification,
        notification_id: str,
        preferences: NotificationPreferences,
    ) -> None:
        """
        Send notification to user based on preferences.

        Args:
            notification: Notification to send
            notification_id: Notification ID
            preferences: User preferences
        """
        try:
            # In-app notifications are always enabled for PII (LGPD requirement)
            if preferences.in_app_notifications:
                await self._send_in_app_notification(notification, notification_id)

            # Email notifications if enabled
            if preferences.email_notifications:
                await self._send_email_notification(notification, notification_id)

        except Exception as e:
            logger.error(f"Failed to send notification {notification_id}: {e}")

    async def _send_in_app_notification(
        self, notification: PIINotification, notification_id: str
    ) -> None:
        """
        Send in-app notification.

        Args:
            notification: Notification to send
            notification_id: Notification ID
        """
        # This would integrate with your frontend notification system
        # For now, we just log it
        logger.info(
            f"In-app notification {notification_id} sent to user {notification.user_id}: "
            f"{notification.title}"
        )

    async def _send_email_notification(
        self, notification: PIINotification, notification_id: str
    ) -> None:
        """
        Send email notification.

        Args:
            notification: Notification to send
            notification_id: Notification ID
        """
        # This would integrate with your email service (SendGrid, etc.)
        # For now, we just log it
        logger.info(
            f"Email notification {notification_id} sent to user {notification.user_id}: "
            f"{notification.title}"
        )

    async def _log_notification_created(
        self, notification: PIINotification, notification_id: str
    ) -> None:
        """
        Log notification creation for audit trail.

        Args:
            notification: Notification that was created
            notification_id: Notification ID
        """
        try:
            event = AuditEvent(
                event_type=AuditEventType.CREATE,
                action=f"PII notification created: {notification.notification_type.value}",
                user_id=notification.user_id,
                table_name="pii_notifications",
                record_id=notification_id,
                success=True,
            )
            await audit_trail.log_audit_event(event)
        except Exception as e:
            logger.error(f"Failed to log notification creation: {e}")

    async def _log_notification_read(self, notification_id: str, user_id: str) -> None:
        """
        Log notification read for audit trail.

        Args:
            notification_id: Notification ID
            user_id: User ID
        """
        try:
            event = AuditEvent(
                event_type=AuditEventType.UPDATE,
                action="PII notification marked as read",
                user_id=user_id,
                table_name="pii_notifications",
                record_id=notification_id,
                success=True,
            )
            await audit_trail.log_audit_event(event)
        except Exception as e:
            logger.error(f"Failed to log notification read: {e}")

    async def get_notification_stats(self, user_id: str) -> dict[str, Any]:
        """
        Get notification statistics for a user.

        Args:
            user_id: User ID

        Returns:
            Notification statistics
        """
        try:
            # Get all notifications for user
            all_notifications = await self.notifications_db.list(
                filters={"user_id": user_id},
                order_by="created_at",
                order_desc=True,
            )

            # Calculate statistics
            total_notifications = len(all_notifications)
            unread_notifications = len([n for n in all_notifications if n.get("read_at") is None])

            # Group by type
            by_type: dict[str, int] = {}
            by_priority: dict[str, int] = {}

            for notification in all_notifications:
                notification_type = notification.get("notification_type", "unknown")
                priority = notification.get("priority", "unknown")

                by_type[notification_type] = by_type.get(notification_type, 0) + 1
                by_priority[priority] = by_priority.get(priority, 0) + 1

            return {
                "total_notifications": total_notifications,
                "unread_notifications": unread_notifications,
                "read_notifications": total_notifications - unread_notifications,
                "by_type": by_type,
                "by_priority": by_priority,
                "last_notification": all_notifications[0]["created_at"]
                if all_notifications
                else None,
            }

        except Exception as e:
            logger.error(f"Failed to get notification stats for user {user_id}: {e}")
            return {}


# Global PII notification service instance
pii_notification_service = PIINotificationService()


async def notify_pii_detected(
    user_id: str,
    document_type: str,
    document_id: str,
    document_name: str,
    pii_types_found: list[str],
    confidence_score: float,
    scan_duration_ms: float,
    characters_masked: int,
) -> str | None:
    """
    Convenience function to notify user about PII detection.

    Args:
        user_id: User ID
        document_type: Type of document (resume/job)
        document_id: Document ID
        document_name: Original document name
        pii_types_found: List of PII types detected
        confidence_score: Detection confidence score
        scan_duration_ms: Scan duration in milliseconds
        characters_masked: Number of characters masked

    Returns:
        Notification ID or None if notification was skipped
    """
    return await pii_notification_service.create_pii_detected_notification(
        user_id=user_id,
        document_type=document_type,
        document_id=document_id,
        document_name=document_name,
        pii_types_found=pii_types_found,
        confidence_score=confidence_score,
        scan_duration_ms=scan_duration_ms,
        characters_masked=characters_masked,
    )
