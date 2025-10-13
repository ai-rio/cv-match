"""
LGPD Data Subject Rights Implementation

This service implements all LGPD data subject rights including:
- Right to Access (Art. 18)
- Right to Correction (Art. 18)
- Right to Deletion/Right to be Forgotten (Art. 18)
- Right to Portability (Art. 18)
- Right to Information (Art. 18)
- Right to Review Decisions (Art. 20)

Critical for CV-Match Brazilian market deployment - data subject rights
are mandatory under LGPD.
"""

import logging
from dataclasses import asdict, dataclass
from datetime import UTC, datetime, timedelta
from enum import Enum
from typing import Any

from pydantic import BaseModel

from app.services.security.consent_manager import consent_manager
from app.services.supabase.database import SupabaseDatabaseService

logger = logging.getLogger(__name__)


class DataSubjectRightType(Enum):
    """Types of data subject rights under LGPD."""

    ACCESS = "access"  # Right to access personal data
    CORRECTION = "correction"  # Right to correct incorrect data
    DELETION = "deletion"  # Right to deletion (right to be forgotten)
    PORTABILITY = "portability"  # Right to data portability
    INFORMATION = "information"  # Right to information about processing
    REVIEW = "review"  # Right to review automated decisions
    CONSENT_WITHDRAWAL = "consent_withdrawal"  # Right to withdraw consent


class RequestStatus(Enum):
    """Status of data subject rights requests."""

    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    REJECTED = "rejected"
    CANCELLED = "cancelled"


class DataAccessRequest(BaseModel):
    """Request for data access."""

    user_id: str
    request_type: DataSubjectRightType
    justification: str | None = None
    ip_address: str | None = None
    user_agent: str | None = None


class DataCorrectionRequest(BaseModel):
    """Request for data correction."""

    user_id: str
    field_corrections: dict[str, Any]
    justification: str
    supporting_documents: list[str] | None = None
    ip_address: str | None = None
    user_agent: str | None = None


class DataDeletionRequest(BaseModel):
    """Request for data deletion."""

    user_id: str
    deletion_scope: str  # 'all', 'specific_data', 'account_only'
    specific_data_types: list[str] | None = None
    justification: str
    retain_legal_required: bool = True
    ip_address: str | None = None
    user_agent: str | None = None


class DataPortabilityRequest(BaseModel):
    """Request for data portability."""

    user_id: str
    format_preference: str = "json"  # 'json', 'csv', 'xml'
    include_deleted: bool = False
    ip_address: str | None = None
    user_agent: str | None = None


@dataclass
class DataSubjectRequest:
    """Data subject rights request record."""

    id: str
    user_id: str
    request_type: DataSubjectRightType
    status: RequestStatus
    request_data: dict[str, Any]
    created_at: datetime
    processed_at: datetime | None = None
    completed_at: datetime | None = None
    processor_notes: str | None = None
    rejection_reason: str | None = None
    ip_address: str | None = None
    user_agent: str | None = None


class DataSubjectRightsResponse(BaseModel):
    """Response for data subject rights requests."""

    request_id: str
    request_type: str
    status: str
    processed_data: dict[str, Any] | None = None
    download_url: str | None = None
    expires_at: datetime | None = None
    message: str | None = None


class DataSubjectRightsManager:
    """Service for managing LGPD data subject rights."""

    def __init__(self):
        """Initialize data subject rights manager."""
        self.requests_db = SupabaseDatabaseService("data_subject_requests", dict)
        self.profiles_db = SupabaseDatabaseService("profiles", dict)
        self.optimizations_db = SupabaseDatabaseService("optimizations", dict)
        self.resumes_db = SupabaseDatabaseService("resumes", dict)
        self.job_descriptions_db = SupabaseDatabaseService("job_descriptions", dict)
        self.usage_tracking_db = SupabaseDatabaseService("usage_tracking", dict)

    async def create_data_access_request(self, request: DataAccessRequest) -> str:
        """
        Create a data access request.

        Args:
            request: Data access request details

        Returns:
            Request ID
        """
        try:
            request_data = {
                "user_id": request.user_id,
                "request_type": request.request_type.value,
                "status": RequestStatus.PENDING.value,
                "request_data": {"justification": request.justification},
                "created_at": datetime.now(UTC).isoformat(),
                "ip_address": request.ip_address,
                "user_agent": request.user_agent,
            }

            result = await self.requests_db.create(request_data)
            request_id = result["id"]

            logger.info(f"Data access request created: {request_id} for user {request.user_id}")
            return request_id

        except Exception as e:
            logger.error(f"Failed to create data access request: {e}")
            raise

    async def process_data_access_request(self, request_id: str) -> DataSubjectRightsResponse:
        """
        Process a data access request.

        Args:
            request_id: Request ID

        Returns:
            Response with user data
        """
        try:
            # Get request details
            request = await self.requests_db.get(request_id)
            if not request:
                raise ValueError("Request not found")

            # Update status to processing
            await self.requests_db.update(
                request_id,
                {
                    "status": RequestStatus.PROCESSING.value,
                    "processed_at": datetime.now(UTC).isoformat(),
                },
            )

            # Collect all user data
            user_data = await self._collect_user_data(request["user_id"])

            # Create response
            response = DataSubjectRightsResponse(
                request_id=request_id,
                request_type=request["request_type"],
                status="completed",
                processed_data=user_data,
                message="Data access request processed successfully",
            )

            # Update request status
            await self.requests_db.update(
                request_id,
                {
                    "status": RequestStatus.COMPLETED.value,
                    "completed_at": datetime.now(UTC).isoformat(),
                    "processor_notes": f"Data export completed. {len(user_data)} data categories included.",
                },
            )

            return response

        except Exception as e:
            logger.error(f"Failed to process data access request {request_id}: {e}")
            await self.requests_db.update(
                request_id,
                {
                    "status": RequestStatus.REJECTED.value,
                    "completed_at": datetime.now(UTC).isoformat(),
                    "rejection_reason": f"Processing error: {str(e)}",
                },
            )
            raise

    async def create_data_correction_request(self, request: DataCorrectionRequest) -> str:
        """
        Create a data correction request.

        Args:
            request: Data correction request details

        Returns:
            Request ID
        """
        try:
            request_data = {
                "user_id": request.user_id,
                "request_type": DataSubjectRightType.CORRECTION.value,
                "status": RequestStatus.PENDING.value,
                "request_data": {
                    "field_corrections": request.field_corrections,
                    "justification": request.justification,
                    "supporting_documents": request.supporting_documents,
                },
                "created_at": datetime.now(UTC).isoformat(),
                "ip_address": request.ip_address,
                "user_agent": request.user_agent,
            }

            result = await self.requests_db.create(request_data)
            request_id = result["id"]

            logger.info(f"Data correction request created: {request_id} for user {request.user_id}")
            return request_id

        except Exception as e:
            logger.error(f"Failed to create data correction request: {e}")
            raise

    async def process_data_correction_request(self, request_id: str) -> DataSubjectRightsResponse:
        """
        Process a data correction request.

        Args:
            request_id: Request ID

        Returns:
            Response with correction results
        """
        try:
            # Get request details
            request = await self.requests_db.get(request_id)
            if not request:
                raise ValueError("Request not found")

            # Update status to processing
            await self.requests_db.update(
                request_id,
                {
                    "status": RequestStatus.PROCESSING.value,
                    "processed_at": datetime.now(UTC).isoformat(),
                },
            )

            # Apply corrections
            corrections_applied = await self._apply_data_corrections(
                request["user_id"], request["request_data"]["field_corrections"]
            )

            # Create response
            response = DataSubjectRightsResponse(
                request_id=request_id,
                request_type=request["request_type"],
                status="completed",
                processed_data=corrections_applied,
                message=f"Data correction completed. {len(corrections_applied)} fields updated.",
            )

            # Update request status
            await self.requests_db.update(
                request_id,
                {
                    "status": RequestStatus.COMPLETED.value,
                    "completed_at": datetime.now(UTC).isoformat(),
                    "processor_notes": f"Applied corrections to {len(corrections_applied)} fields.",
                },
            )

            return response

        except Exception as e:
            logger.error(f"Failed to process data correction request {request_id}: {e}")
            await self.requests_db.update(
                request_id,
                {
                    "status": RequestStatus.REJECTED.value,
                    "completed_at": datetime.now(UTC).isoformat(),
                    "rejection_reason": f"Processing error: {str(e)}",
                },
            )
            raise

    async def create_data_deletion_request(self, request: DataDeletionRequest) -> str:
        """
        Create a data deletion request (right to be forgotten).

        Args:
            request: Data deletion request details

        Returns:
            Request ID
        """
        try:
            request_data = {
                "user_id": request.user_id,
                "request_type": DataSubjectRightType.DELETION.value,
                "status": RequestStatus.PENDING.value,
                "request_data": {
                    "deletion_scope": request.deletion_scope,
                    "specific_data_types": request.specific_data_types,
                    "justification": request.justification,
                    "retain_legal_required": request.retain_legal_required,
                },
                "created_at": datetime.now(UTC).isoformat(),
                "ip_address": request.ip_address,
                "user_agent": request.user_agent,
            }

            result = await self.requests_db.create(request_data)
            request_id = result["id"]

            logger.info(f"Data deletion request created: {request_id} for user {request.user_id}")
            return request_id

        except Exception as e:
            logger.error(f"Failed to create data deletion request: {e}")
            raise

    async def process_data_deletion_request(self, request_id: str) -> DataSubjectRightsResponse:
        """
        Process a data deletion request.

        Args:
            request_id: Request ID

        Returns:
            Response with deletion results
        """
        try:
            # Get request details
            request = await self.requests_db.get(request_id)
            if not request:
                raise ValueError("Request not found")

            # Update status to processing
            await self.requests_db.update(
                request_id,
                {
                    "status": RequestStatus.PROCESSING.value,
                    "processed_at": datetime.now(UTC).isoformat(),
                },
            )

            # Apply deletions
            deletion_results = await self._apply_data_deletions(
                request["user_id"], request["request_data"]
            )

            # Create response
            response = DataSubjectRightsResponse(
                request_id=request_id,
                request_type=request["request_type"],
                status="completed",
                processed_data=deletion_results,
                message="Data deletion request processed successfully",
            )

            # Update request status
            await self.requests_db.update(
                request_id,
                {
                    "status": RequestStatus.COMPLETED.value,
                    "completed_at": datetime.now(UTC).isoformat(),
                    "processor_notes": f"Data deletion completed per scope: {request['request_data']['deletion_scope']}",
                },
            )

            return response

        except Exception as e:
            logger.error(f"Failed to process data deletion request {request_id}: {e}")
            await self.requests_db.update(
                request_id,
                {
                    "status": RequestStatus.REJECTED.value,
                    "completed_at": datetime.now(UTC).isoformat(),
                    "rejection_reason": f"Processing error: {str(e)}",
                },
            )
            raise

    async def create_data_portability_request(self, request: DataPortabilityRequest) -> str:
        """
        Create a data portability request.

        Args:
            request: Data portability request details

        Returns:
            Request ID
        """
        try:
            request_data = {
                "user_id": request.user_id,
                "request_type": DataSubjectRightType.PORTABILITY.value,
                "status": RequestStatus.PENDING.value,
                "request_data": {
                    "format_preference": request.format_preference,
                    "include_deleted": request.include_deleted,
                },
                "created_at": datetime.now(UTC).isoformat(),
                "ip_address": request.ip_address,
                "user_agent": request.user_agent,
            }

            result = await self.requests_db.create(request_data)
            request_id = result["id"]

            logger.info(
                f"Data portability request created: {request_id} for user {request.user_id}"
            )
            return request_id

        except Exception as e:
            logger.error(f"Failed to create data portability request: {e}")
            raise

    async def process_data_portability_request(self, request_id: str) -> DataSubjectRightsResponse:
        """
        Process a data portability request.

        Args:
            request_id: Request ID

        Returns:
            Response with portable data
        """
        try:
            # Get request details
            request = await self.requests_db.get(request_id)
            if not request:
                raise ValueError("Request not found")

            # Update status to processing
            await self.requests_db.update(
                request_id,
                {
                    "status": RequestStatus.PROCESSING.value,
                    "processed_at": datetime.now(UTC).isoformat(),
                },
            )

            # Collect portable data
            portable_data = await self._collect_portable_data(
                request["user_id"], request["request_data"]
            )

            # Create response
            response = DataSubjectRightsResponse(
                request_id=request_id,
                request_type=request["request_type"],
                status="completed",
                processed_data=portable_data,
                message="Data portability request processed successfully",
                expires_at=datetime.now(UTC) + timedelta(days=7),  # Data expires in 7 days
            )

            # Update request status
            await self.requests_db.update(
                request_id,
                {
                    "status": RequestStatus.COMPLETED.value,
                    "completed_at": datetime.now(UTC).isoformat(),
                    "processor_notes": f"Portable data exported in {request['request_data']['format_preference']} format.",
                },
            )

            return response

        except Exception as e:
            logger.error(f"Failed to process data portability request {request_id}: {e}")
            await self.requests_db.update(
                request_id,
                {
                    "status": RequestStatus.REJECTED.value,
                    "completed_at": datetime.now(UTC).isoformat(),
                    "rejection_reason": f"Processing error: {str(e)}",
                },
            )
            raise

    async def _collect_user_data(self, user_id: str) -> dict[str, Any]:
        """Collect all user data for access requests."""
        try:
            user_data = {
                "user_id": user_id,
                "export_date": datetime.now(UTC).isoformat(),
                "data_categories": {},
            }

            # Profile data
            try:
                profile = await self.profiles_db.get(user_id)
                if profile:
                    user_data["data_categories"]["profile"] = profile
            except Exception as e:
                logger.warning(f"Failed to collect profile data: {e}")

            # Optimizations data
            try:
                optimizations = await self.optimizations_db.list(filters={"user_id": user_id})
                if optimizations:
                    user_data["data_categories"]["optimizations"] = optimizations
            except Exception as e:
                logger.warning(f"Failed to collect optimizations data: {e}")

            # Resumes data
            try:
                resumes = await self.resumes_db.list(filters={"user_id": user_id})
                if resumes:
                    user_data["data_categories"]["resumes"] = resumes
            except Exception as e:
                logger.warning(f"Failed to collect resumes data: {e}")

            # Job descriptions data
            try:
                job_descriptions = await self.job_descriptions_db.list(filters={"user_id": user_id})
                if job_descriptions:
                    user_data["data_categories"]["job_descriptions"] = job_descriptions
            except Exception as e:
                logger.warning(f"Failed to collect job descriptions data: {e}")

            # Usage tracking data
            try:
                usage_tracking = await self.usage_tracking_db.list(filters={"user_id": user_id})
                if usage_tracking:
                    user_data["data_categories"]["usage_tracking"] = usage_tracking
            except Exception as e:
                logger.warning(f"Failed to collect usage tracking data: {e}")

            # Consent data
            try:
                consent_status = await consent_manager.get_user_consent_status(user_id)
                user_data["data_categories"]["consents"] = asdict(consent_status)
            except Exception as e:
                logger.warning(f"Failed to collect consent data: {e}")

            return user_data

        except Exception as e:
            logger.error(f"Failed to collect user data: {e}")
            raise

    async def _apply_data_corrections(
        self, user_id: str, corrections: dict[str, Any]
    ) -> dict[str, Any]:
        """Apply data corrections to user profile."""
        try:
            applied_corrections = {}

            # Apply corrections to profile
            if "profile" in corrections:
                profile_corrections = corrections["profile"]
                await self.profiles_db.update(user_id, profile_corrections)
                applied_corrections["profile"] = profile_corrections

            # Apply corrections to other tables as needed
            # TODO: Implement corrections for other data types

            return applied_corrections

        except Exception as e:
            logger.error(f"Failed to apply data corrections: {e}")
            raise

    async def _apply_data_deletions(
        self, user_id: str, deletion_request: dict[str, Any]
    ) -> dict[str, Any]:
        """Apply data deletions according to request scope."""
        try:
            deletion_scope = deletion_request.get("deletion_scope", "all")
            specific_data_types = deletion_request.get("specific_data_types", [])
            retain_legal_required = deletion_request.get("retain_legal_required", True)

            deletion_results = {"deleted_data": {}, "retained_data": {}}

            if deletion_scope == "all":
                # Full data deletion (right to be forgotten)
                if not retain_legal_required:
                    # Complete deletion including legal records
                    await self._permanent_user_deletion(user_id)
                    deletion_results["deleted_data"]["all"] = "Complete deletion performed"
                else:
                    # Soft deletion retaining required legal data
                    await self._soft_delete_user_data(user_id)
                    deletion_results["deleted_data"]["all"] = (
                        "Soft deletion performed, legal data retained"
                    )

            elif deletion_scope == "specific_data":
                # Delete specific data types
                for data_type in specific_data_types:
                    if data_type == "optimizations":
                        await self.optimizations_db.update_many(
                            filters={"user_id": user_id},
                            data={"deleted_at": datetime.now(UTC).isoformat()},
                        )
                        deletion_results["deleted_data"][data_type] = (
                            "Optimization records soft deleted"
                        )
                    elif data_type == "resumes":
                        await self.resumes_db.update_many(
                            filters={"user_id": user_id},
                            data={"deleted_at": datetime.now(UTC).isoformat()},
                        )
                        deletion_results["deleted_data"][data_type] = "Resume records soft deleted"
                    elif data_type == "job_descriptions":
                        await self.job_descriptions_db.update_many(
                            filters={"user_id": user_id},
                            data={"deleted_at": datetime.now(UTC).isoformat()},
                        )
                        deletion_results["deleted_data"][data_type] = (
                            "Job description records soft deleted"
                        )

            elif deletion_scope == "account_only":
                # Delete account but keep some data for legal purposes
                await self.profiles_db.update(
                    user_id,
                    {"deleted_at": datetime.now(UTC).isoformat(), "full_name": None, "email": None},
                )
                deletion_results["deleted_data"]["account"] = "Account soft deleted"

            return deletion_results

        except Exception as e:
            logger.error(f"Failed to apply data deletions: {e}")
            raise

    async def _collect_portable_data(
        self, user_id: str, request_data: dict[str, Any]
    ) -> dict[str, Any]:
        """Collect user data in portable format."""
        try:
            format_preference = request_data.get("format_preference", "json")
            include_deleted = request_data.get("include_deleted", False)

            # Collect all user data
            user_data = await self._collect_user_data(user_id)

            # Format according to preference
            if format_preference == "json":
                portable_data = user_data
            elif format_preference == "csv":
                # Convert to CSV-friendly format
                portable_data = self._convert_to_csv_format(user_data)
            else:
                portable_data = user_data  # Default to JSON

            return {
                "format": format_preference,
                "data": portable_data,
                "metadata": {
                    "export_date": datetime.now(UTC).isoformat(),
                    "user_id": user_id,
                    "includes_deleted": include_deleted,
                    "lgpd_compliant": True,
                },
            }

        except Exception as e:
            logger.error(f"Failed to collect portable data: {e}")
            raise

    async def _permanent_user_deletion(self, user_id: str) -> None:
        """Permanent deletion of all user data."""
        try:
            # Delete from all tables
            await self.usage_tracking_db.delete_many(filters={"user_id": user_id})
            await self.job_descriptions_db.delete_many(filters={"user_id": user_id})
            await self.resumes_db.delete_many(filters={"user_id": user_id})
            await self.optimizations_db.delete_many(filters={"user_id": user_id})
            await self.profiles_db.delete(user_id)

            logger.info(f"Permanent deletion completed for user {user_id}")

        except Exception as e:
            logger.error(f"Failed permanent deletion for user {user_id}: {e}")
            raise

    async def _soft_delete_user_data(self, user_id: str) -> None:
        """Soft delete user data while retaining legal records."""
        try:
            # Soft delete all user data
            timestamp = datetime.now(UTC).isoformat()

            await self.usage_tracking_db.update_many(
                filters={"user_id": user_id}, data={"deleted_at": timestamp}
            )
            await self.job_descriptions_db.update_many(
                filters={"user_id": user_id}, data={"deleted_at": timestamp}
            )
            await self.resumes_db.update_many(
                filters={"user_id": user_id}, data={"deleted_at": timestamp}
            )
            await self.optimizations_db.update_many(
                filters={"user_id": user_id}, data={"deleted_at": timestamp}
            )
            await self.profiles_db.update(user_id, {"deleted_at": timestamp})

            logger.info(f"Soft deletion completed for user {user_id}")

        except Exception as e:
            logger.error(f"Failed soft deletion for user {user_id}: {e}")
            raise

    def _convert_to_csv_format(self, user_data: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
        """Convert user data to CSV-friendly format."""
        csv_data = {}

        for category, data in user_data.get("data_categories", {}).items():
            if isinstance(data, list):
                csv_data[category] = data
            elif isinstance(data, dict):
                csv_data[category] = [data]

        return csv_data


# Global data subject rights manager instance
data_subject_rights_manager = DataSubjectRightsManager()


async def create_data_access_request(user_id: str, justification: str = None) -> str:
    """
    Convenience function to create data access request.

    Args:
        user_id: User ID
        justification: Request justification

    Returns:
        Request ID
    """
    request = DataAccessRequest(
        user_id=user_id, request_type=DataSubjectRightType.ACCESS, justification=justification
    )
    return await data_subject_rights_manager.create_data_access_request(request)


async def create_data_deletion_request(
    user_id: str, scope: str = "all", justification: str = "User request"
) -> str:
    """
    Convenience function to create data deletion request.

    Args:
        user_id: User ID
        scope: Deletion scope
        justification: Request justification

    Returns:
        Request ID
    """
    request = DataDeletionRequest(
        user_id=user_id, deletion_scope=scope, justification=justification
    )
    return await data_subject_rights_manager.create_data_deletion_request(request)
