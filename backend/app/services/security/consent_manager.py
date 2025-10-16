"""
LGPD Consent Management Service

This service provides comprehensive consent management for LGPD compliance
in the Brazilian market. It handles consent recording, validation, and management
with full audit trail capabilities.

Critical for CV-Match Brazilian market deployment - proper consent management
is mandatory under LGPD.
"""

import logging
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, validator

from app.services.security.pii_detection_service import mask_pii
from app.services.supabase.database import SupabaseDatabaseService

logger = logging.getLogger(__name__)


class ConsentType(BaseModel):
    """Consent type definition."""

    id: str
    name: str
    description: str
    category: str
    is_required: bool
    version: int
    is_active: bool


class UserConsent(BaseModel):
    """User consent record."""

    id: str
    user_id: str
    consent_type_id: str
    granted: bool
    granted_at: datetime
    revoked_at: datetime | None = None
    ip_address: str | None = None
    user_agent: str | None = None
    consent_version: int
    legal_basis: str | None = None
    purpose: str | None = None
    created_at: datetime
    updated_at: datetime


class ConsentRequest(BaseModel):
    """Request to record user consent."""

    consent_type_name: str
    granted: bool
    legal_basis: str = "consent"
    purpose: str | None = None
    ip_address: str | None = None
    user_agent: str | None = None

    @validator("legal_basis")
    def validate_legal_basis(cls, v: str) -> str:
        valid_bases = [
            "consent",
            "contract",
            "legal_obligation",
            "vital_interests",
            "public_task",
            "legitimate_interests",
        ]
        if v not in valid_bases:
            raise ValueError(f"Legal basis must be one of: {valid_bases}")
        return v


class ConsentCheckResult(BaseModel):
    """Result of consent validation."""

    has_consent: bool
    consent_type: str
    granted_at: datetime | None = None
    revoked_at: datetime | None = None
    is_required: bool = False
    legal_basis: str | None = None


class UserConsentStatus(BaseModel):
    """Complete user consent status."""

    user_id: str
    has_all_required_consents: bool
    consents: list[dict[str, Any]]
    missing_required_consents: list[str]
    granted_optional_consents: list[str]
    revoked_consents: list[str]
    last_updated: datetime


@dataclass
class ConsentAuditEvent:
    """Audit event for consent changes."""

    user_id: str
    consent_type: str
    action: str  # 'granted', 'revoked', 'updated'
    timestamp: datetime
    ip_address: str | None
    user_agent: str | None
    previous_value: bool | None
    new_value: bool
    reason: str | None


class ConsentManager:
    """Service for managing user consents under LGPD."""

    def __init__(self) -> None:
        """Initialize consent manager."""
        self.consent_types_db = SupabaseDatabaseService("consent_types", ConsentType)
        self.user_consents_db = SupabaseDatabaseService("user_consents", UserConsent)
        self.history_db = SupabaseDatabaseService("consent_history", dict)

    async def get_available_consent_types(self) -> list[ConsentType]:
        """
        Get all available consent types.

        Returns:
            List of available consent types
        """
        try:
            result = await self.consent_types_db.list(filters={"is_active": True})
            return [
                ConsentType(**asdict(item))
                if isinstance(item, ConsentType)
                else ConsentType(**item)
                for item in result
            ]
        except Exception as e:
            logger.error(f"Failed to get consent types: {e}")
            raise

    async def record_user_consent(
        self, user_id: str, consent_request: ConsentRequest
    ) -> UserConsent | None:
        """
        Record user consent with audit trail.

        Args:
            user_id: User ID
            consent_request: Consent details

        Returns:
            Created consent record or None if consent was revoked
        """
        try:
            # Get consent type details
            consent_types = await self.get_available_consent_types()
            consent_type = None

            for ct in consent_types:
                if ct.name == consent_request.consent_type_name:
                    consent_type = ct
                    break

            if not consent_type:
                raise ValueError(f"Consent type '{consent_request.consent_type_name}' not found")

            # Check if this is a required consent and user is revoking it
            if consent_type.is_required and not consent_request.granted:
                raise ValueError(f"Cannot revoke required consent '{consent_type.name}'")

            # Revoke any existing consent first
            await self._revoke_existing_consent(user_id, consent_type.id)

            # Record new consent if granted
            if consent_request.granted:
                consent_data = {
                    "user_id": user_id,
                    "consent_type_id": consent_type.id,
                    "granted": True,
                    "granted_at": datetime.now(UTC).isoformat(),
                    "ip_address": consent_request.ip_address,
                    "user_agent": consent_request.user_agent,
                    "consent_version": consent_type.version,
                    "legal_basis": consent_request.legal_basis,
                    "purpose": consent_request.purpose,
                    "created_at": datetime.now(UTC).isoformat(),
                    "updated_at": datetime.now(UTC).isoformat(),
                }

                # Create consent record
                result = await self.user_consents_db.create(consent_data)
                consent_record = UserConsent(
                    **asdict(result) if isinstance(result, UserConsent) else result
                )

                # Log audit event
                await self._log_consent_event(
                    user_id=user_id,
                    consent_type_name=consent_type.name,
                    action="granted",
                    new_value=True,
                    ip_address=consent_request.ip_address,
                    user_agent=consent_request.user_agent,
                    reason=consent_request.purpose,
                )

                logger.info(f"Consent granted for user {user_id}: {consent_type.name}")
                return consent_record

            return None

        except Exception as e:
            logger.error(f"Failed to record consent for user {user_id}: {e}")
            raise

    async def _revoke_existing_consent(self, user_id: str, consent_type_id: str) -> None:
        """Revoke existing consent for the same type."""
        try:
            # Find existing active consent
            existing_consents = await self.user_consents_db.list(
                filters={"user_id": user_id, "consent_type_id": consent_type_id, "granted": True}
            )

            for consent in existing_consents:
                consent_dict = asdict(consent) if isinstance(consent, UserConsent) else consent
                if consent_dict.get("revoked_at") is None:
                    # Revoke the consent
                    await self.user_consents_db.update(
                        consent_dict["id"], {"revoked_at": datetime.now(UTC).isoformat()}
                    )

                    # Log audit event
                    consent_type_name = await self._get_consent_type_name(consent_type_id)
                    await self._log_consent_event(
                        user_id=user_id,
                        consent_type_name=consent_type_name,
                        action="revoked",
                        previous_value=True,
                        new_value=False,
                        reason="New consent provided",
                    )

        except Exception as e:
            logger.error(f"Failed to revoke existing consent: {e}")

    async def _get_consent_type_name(self, consent_type_id: str) -> str:
        """Get consent type name by ID."""
        try:
            consent_type = await self.consent_types_db.get(consent_type_id)
            if isinstance(consent_type, ConsentType):
                return consent_type.name
            return consent_type.get("name", "unknown") if consent_type else "unknown"
        except Exception:
            return "unknown"

    async def check_user_consent(self, user_id: str, consent_type_name: str) -> ConsentCheckResult:
        """
        Check if user has valid consent for a specific type.

        Args:
            user_id: User ID
            consent_type_name: Name of consent type to check

        Returns:
            Consent check result
        """
        try:
            # Get consent type
            consent_types = await self.get_available_consent_types()
            consent_type = None

            for ct in consent_types:
                if ct.name == consent_type_name:
                    consent_type = ct
                    break

            if not consent_type:
                raise ValueError(f"Consent type '{consent_type_name}' not found")

            # Check for active consent
            user_consents = await self.user_consents_db.list(
                filters={"user_id": user_id, "consent_type_id": consent_type.id, "granted": True}
            )

            active_consent = None
            for consent in user_consents:
                consent_dict = asdict(consent) if isinstance(consent, UserConsent) else consent
                if consent_dict.get("revoked_at") is None:
                    active_consent = consent_dict
                    break

            has_consent = active_consent is not None

            return ConsentCheckResult(
                has_consent=has_consent,
                consent_type=consent_type_name,
                granted_at=datetime.fromisoformat(active_consent["granted_at"]).replace(tzinfo=UTC)
                if active_consent
                else None,
                revoked_at=datetime.fromisoformat(active_consent["revoked_at"]).replace(tzinfo=UTC)
                if active_consent and active_consent.get("revoked_at")
                else None,
                is_required=consent_type.is_required,
                legal_basis=active_consent.get("legal_basis") if active_consent else None,
            )

        except Exception as e:
            logger.error(f"Failed to check consent for user {user_id}: {e}")
            raise

    async def get_user_consent_status(self, user_id: str) -> UserConsentStatus:
        """
        Get complete consent status for a user.

        Args:
            user_id: User ID

        Returns:
            Complete user consent status
        """
        try:
            # Get all available consent types
            consent_types = await self.get_available_consent_types()

            # Get user consents
            user_consents = await self.user_consents_db.list(filters={"user_id": user_id})

            # Build consent status
            granted_consents = []
            revoked_consents = []
            consent_lookup = {}

            for consent in user_consents:
                consent_dict = asdict(consent) if isinstance(consent, UserConsent) else consent
                consent_name = await self._get_consent_type_name(consent_dict["consent_type_id"])
                consent_lookup[consent_name] = consent_dict

                if consent_dict.get("revoked_at") is None and consent_dict["granted"]:
                    granted_consents.append(consent_name)
                else:
                    revoked_consents.append(consent_name)

            # Check required consents
            required_consents = [ct.name for ct in consent_types if ct.is_required]
            missing_required = [rc for rc in required_consents if rc not in granted_consents]

            # Get optional consents
            optional_consents = [ct.name for ct in consent_types if not ct.is_required]
            granted_optional = [oc for oc in optional_consents if oc in granted_consents]

            # Build consent details
            consent_details = []
            for consent_type in consent_types:
                user_consent = consent_lookup.get(consent_type.name)
                consent_details.append(
                    {
                        "name": consent_type.name,
                        "description": consent_type.description,
                        "category": consent_type.category,
                        "is_required": consent_type.is_required,
                        "granted": user_consent is not None
                        and user_consent.get("revoked_at") is None
                        and user_consent["granted"],
                        "granted_at": user_consent.get("granted_at") if user_consent else None,
                        "revoked_at": user_consent.get("revoked_at") if user_consent else None,
                        "legal_basis": user_consent.get("legal_basis") if user_consent else None,
                    }
                )

            return UserConsentStatus(
                user_id=user_id,
                has_all_required_consents=len(missing_required) == 0,
                consents=consent_details,
                missing_required_consents=missing_required,
                granted_optional_consents=granted_optional,
                revoked_consents=revoked_consents,
                last_updated=datetime.now(UTC),
            )

        except Exception as e:
            logger.error(f"Failed to get consent status for user {user_id}: {e}")
            raise

    async def revoke_all_consents(self, user_id: str, reason: str = "User request") -> None:
        """
        Revoke all user consents (right to withdrawal).

        Args:
            user_id: User ID
            reason: Reason for revocation
        """
        try:
            user_consents = await self.user_consents_db.list(
                filters={"user_id": user_id, "granted": True}
            )

            for consent in user_consents:
                consent_dict = asdict(consent) if isinstance(consent, UserConsent) else consent
                if consent_dict.get("revoked_at") is None:
                    await self.user_consents_db.update(
                        consent_dict["id"], {"revoked_at": datetime.now(UTC).isoformat()}
                    )

                    # Log audit event
                    consent_type_name = await self._get_consent_type_name(
                        consent_dict["consent_type_id"]
                    )
                    await self._log_consent_event(
                        user_id=user_id,
                        consent_type_name=consent_type_name,
                        action="revoked",
                        previous_value=True,
                        new_value=False,
                        reason=reason,
                    )

            logger.info(f"All consents revoked for user {user_id}: {reason}")

        except Exception as e:
            logger.error(f"Failed to revoke all consents for user {user_id}: {e}")
            raise

    async def _log_consent_event(
        self,
        user_id: str,
        consent_type_name: str,
        action: str,
        new_value: bool,
        ip_address: str | None = None,
        user_agent: str | None = None,
        previous_value: bool | None = None,
        reason: str | None = None,
    ) -> None:
        """Log consent audit event."""
        try:
            audit_data = {
                "user_consent_id": f"{user_id}_{consent_type_name}",  # Simplified for now
                "action": action,
                "previous_value": previous_value,
                "new_value": new_value,
                "changed_at": datetime.now(UTC).isoformat(),
                "changed_by": user_id,
                "ip_address": ip_address,
                "user_agent": user_agent,
                "reason": reason,
                "created_at": datetime.now(UTC).isoformat(),
            }

            await self.history_db.create(audit_data)

        except Exception as e:
            logger.error(f"Failed to log consent event: {e}")

    async def export_user_consents(self, user_id: str) -> dict[str, Any]:
        """
        Export user consent data for LGPD data portability.

        Args:
            user_id: User ID

        Returns:
            User consent data export
        """
        try:
            consent_status = await self.get_user_consent_status(user_id)

            # Get consent history
            history_records = await self.history_db.list(filters={"changed_by": user_id})

            export_data = {
                "user_id": user_id,
                "export_date": datetime.now(UTC).isoformat(),
                "consent_status": asdict(consent_status),
                "consent_history": history_records,
                "data_processing_activities": [],  # TODO: Implement when needed
            }

            # Mask any PII in the export
            export_json = str(export_data)
            masked_export = mask_pii(export_json)

            return {
                "export_data": export_data,
                "masked_export": masked_export,
                "contains_pii": export_json != masked_export,
            }

        except Exception as e:
            logger.error(f"Failed to export consents for user {user_id}: {e}")
            raise

    async def validate_processing_activity(self, user_id: str, activity_type: str) -> bool:
        """
        Validate if user has consent for a specific processing activity.

        Args:
            user_id: User ID
            activity_type: Type of processing activity

        Returns:
            True if processing is allowed, False otherwise
        """
        try:
            # Map activity types to required consents
            activity_consent_map = {
                "resume_analysis": ["data_processing", "ai_processing"],
                "marketing": ["marketing"],
                "analytics": ["analytics"],
                "account_management": ["data_processing"],
                "data_sharing": ["data_sharing"],
            }

            required_consents = activity_consent_map.get(activity_type, [])

            if not required_consents:
                return True  # No specific consent required

            # Check each required consent
            for consent_name in required_consents:
                consent_check = await self.check_user_consent(user_id, consent_name)
                if not consent_check.has_consent:
                    logger.warning(f"Missing consent for user {user_id}: {consent_name}")
                    return False

            return True

        except Exception as e:
            logger.error(f"Failed to validate processing activity: {e}")
            return False


# Global consent manager instance
consent_manager = ConsentManager()


async def record_user_consent(user_id: str, consent_request: ConsentRequest) -> UserConsent | None:
    """
    Convenience function to record user consent.

    Args:
        user_id: User ID
        consent_request: Consent details

    Returns:
        Created consent record
    """
    return await consent_manager.record_user_consent(user_id, consent_request)


async def check_user_consent(user_id: str, consent_type_name: str) -> ConsentCheckResult:
    """
    Convenience function to check user consent.

    Args:
        user_id: User ID
        consent_type_name: Name of consent type

    Returns:
        Consent check result
    """
    return await consent_manager.check_user_consent(user_id, consent_type_name)


async def get_user_consent_status(user_id: str) -> UserConsentStatus:
    """
    Convenience function to get user consent status.

    Args:
        user_id: User ID

    Returns:
        User consent status
    """
    return await consent_manager.get_user_consent_status(user_id)
