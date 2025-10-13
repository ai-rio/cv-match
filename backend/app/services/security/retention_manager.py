"""
Data Retention Management Service for LGPD Compliance

This service implements automated data retention policies to ensure that
personal data is not kept longer than necessary under LGPD requirements.
Includes retention scheduling, automated cleanup, and compliance monitoring.

Critical for CV-Match Brazilian market deployment - proper data retention
is mandatory under LGPD Article 15.
"""

import logging
from dataclasses import asdict, dataclass
from datetime import UTC, datetime, timedelta
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field, validator

from app.services.supabase.database import SupabaseDatabaseService

logger = logging.getLogger(__name__)


class RetentionPeriod(Enum):
    """Standard retention periods for different data types."""

    IMMEDIATE = "immediate"  # Delete immediately
    THIRTY_DAYS = "30_days"  # 30 days
    NINETY_DAYS = "90_days"  # 90 days
    SIX_MONTHS = "6_months"  # 6 months
    ONE_YEAR = "1_year"  # 1 year
    TWO_YEARS = "2_years"  # 2 years
    FIVE_YEARS = "5_years"  # 5 years (LGPD default)
    SEVEN_YEARS = "7_years"  # 7 years (financial records)
    TEN_YEARS = "10_years"  # 10 years


class DataCategory(Enum):
    """Categories of data with different retention requirements."""

    USER_PROFILE = "user_profile"
    RESUME_DATA = "resume_data"
    JOB_DESCRIPTIONS = "job_descriptions"
    OPTIMIZATION_RESULTS = "optimization_results"
    USAGE_ANALYTICS = "usage_analytics"
    CONSENT_RECORDS = "consent_records"
    PAYMENT_RECORDS = "payment_records"
    SUPPORT_TICKETS = "support_tickets"
    AUDIT_LOGS = "audit_logs"
    COMMUNICATION_LOGS = "communication_logs"


class RetentionPolicy(BaseModel):
    """Data retention policy definition."""

    data_category: DataCategory
    retention_period: RetentionPeriod
    retention_days: int
    legal_basis: str
    deletion_method: str = "soft_delete"  # "soft_delete", "permanent_delete", "anonymize"
    requires_user_consent: bool = False
    auto_cleanup: bool = True
    exceptions: list[str] = Field(default_factory=list)

    @validator("retention_days")
    def validate_retention_days(cls, v, values):
        if v <= 0:
            raise ValueError("Retention days must be positive")
        return v


@dataclass
class RetentionTask:
    """Automated retention cleanup task."""

    id: str
    data_category: DataCategory
    scheduled_date: datetime
    completed_date: datetime | None = None
    status: str = "pending"  # "pending", "running", "completed", "failed"
    records_processed: int = 0
    records_deleted: int = 0
    errors: list[str] = None

    def __post_init__(self):
        if self.errors is None:
            self.errors = []


class RetentionCleanupResult(BaseModel):
    """Result of a retention cleanup operation."""

    data_category: str
    retention_policy: str
    records_scanned: int
    records_deleted: int
    records_retained: int
    errors_encountered: int
    duration_seconds: float
    cleanup_date: datetime
    next_cleanup_date: datetime | None = None


class RetentionManager:
    """Service for managing data retention policies and cleanup."""

    def __init__(self):
        """Initialize retention manager."""
        self.policies_db = SupabaseDatabaseService("retention_policies", dict)
        self.tasks_db = SupabaseDatabaseService("retention_tasks", dict)
        self.results_db = SupabaseDatabaseService("retention_results", dict)

        self.profiles_db = SupabaseDatabaseService("profiles", dict)
        self.optimizations_db = SupabaseDatabaseService("optimizations", dict)
        self.resumes_db = SupabaseDatabaseService("resumes", dict)
        self.job_descriptions_db = SupabaseDatabaseService("job_descriptions", dict)
        self.usage_tracking_db = SupabaseDatabaseService("usage_tracking", dict)

        self._init_default_policies()

    def _init_default_policies(self) -> None:
        """Initialize default retention policies for LGPD compliance."""
        self.default_policies = [
            RetentionPolicy(
                data_category=DataCategory.USER_PROFILE,
                retention_period=RetentionPeriod.FIVE_YEARS,
                retention_days=1825,  # 5 years
                legal_basis="LGPD Art. 15 - Standard retention period",
                deletion_method="soft_delete",
                requires_user_consent=False,
                auto_cleanup=True,
            ),
            RetentionPolicy(
                data_category=DataCategory.RESUME_DATA,
                retention_period=RetentionPeriod.TWO_YEARS,
                retention_days=730,  # 2 years
                legal_basis="User consent and service necessity",
                deletion_method="soft_delete",
                requires_user_consent=True,
                auto_cleanup=True,
            ),
            RetentionPolicy(
                data_category=DataCategory.JOB_DESCRIPTIONS,
                retention_period=RetentionPeriod.ONE_YEAR,
                retention_days=365,  # 1 year
                legal_basis="Service usage pattern",
                deletion_method="soft_delete",
                requires_user_consent=False,
                auto_cleanup=True,
            ),
            RetentionPolicy(
                data_category=DataCategory.OPTIMIZATION_RESULTS,
                retention_period=RetentionPeriod.TWO_YEARS,
                retention_days=730,  # 2 years
                legal_basis="Service delivery records",
                deletion_method="soft_delete",
                requires_user_consent=True,
                auto_cleanup=True,
            ),
            RetentionPolicy(
                data_category=DataCategory.USAGE_ANALYTICS,
                retention_period=RetentionPeriod.ONE_YEAR,
                retention_days=365,  # 1 year
                legal_basis="Legitimate interest for service improvement",
                deletion_method="anonymize",
                requires_user_consent=False,
                auto_cleanup=True,
            ),
            RetentionPolicy(
                data_category=DataCategory.CONSENT_RECORDS,
                retention_period=RetentionPeriod.SEVEN_YEARS,
                retention_days=2555,  # 7 years
                legal_basis="Legal requirement for consent records",
                deletion_method="permanent_delete",
                requires_user_consent=False,
                auto_cleanup=False,  # Manual review required
            ),
            RetentionPolicy(
                data_category=DataCategory.PAYMENT_RECORDS,
                retention_period=RetentionPeriod.SEVEN_YEARS,
                retention_days=2555,  # 7 years
                legal_basis="Tax and legal requirements",
                deletion_method="permanent_delete",
                requires_user_consent=False,
                auto_cleanup=False,  # Manual review required
            ),
            RetentionPolicy(
                data_category=DataCategory.AUDIT_LOGS,
                retention_period=RetentionPeriod.TWO_YEARS,
                retention_days=730,  # 2 years
                legal_basis="Security and compliance monitoring",
                deletion_method="permanent_delete",
                requires_user_consent=False,
                auto_cleanup=True,
            ),
        ]

    async def create_retention_policy(self, policy: RetentionPolicy) -> str:
        """
        Create a new retention policy.

        Args:
            policy: Retention policy details

        Returns:
            Policy ID
        """
        try:
            policy_data = asdict(policy)
            policy_data["created_at"] = datetime.now(UTC).isoformat()

            result = await self.policies_db.create(policy_data)
            policy_id = result["id"]

            logger.info(f"Retention policy created: {policy_id} for {policy.data_category.value}")
            return policy_id

        except Exception as e:
            logger.error(f"Failed to create retention policy: {e}")
            raise

    async def get_retention_policies(self) -> list[RetentionPolicy]:
        """
        Get all active retention policies.

        Returns:
            List of retention policies
        """
        try:
            # Get policies from database
            db_policies = await self.policies_db.list(filters={"is_active": True})

            # Convert to RetentionPolicy objects
            policies = []
            for policy_data in db_policies:
                try:
                    policy = RetentionPolicy(**policy_data)
                    policies.append(policy)
                except Exception as e:
                    logger.warning(f"Invalid retention policy in database: {e}")

            # Add default policies if none exist
            if not policies:
                policies = self.default_policies
                # Store default policies in database
                for policy in policies:
                    await self.create_retention_policy(policy)

            return policies

        except Exception as e:
            logger.error(f"Failed to get retention policies: {e}")
            return self.default_policies

    async def schedule_retention_cleanup(self, data_category: DataCategory) -> str:
        """
        Schedule a retention cleanup task.

        Args:
            data_category: Data category to clean up

        Returns:
            Task ID
        """
        try:
            # Get retention policy for this category
            policies = await self.get_retention_policies()
            policy = None

            for p in policies:
                if p.data_category == data_category:
                    policy = p
                    break

            if not policy:
                raise ValueError(f"No retention policy found for {data_category.value}")

            # Schedule cleanup
            task_data = {
                "data_category": data_category.value,
                "scheduled_date": datetime.now(UTC).isoformat(),
                "status": "pending",
                "retention_policy": asdict(policy),
                "created_at": datetime.now(UTC).isoformat(),
            }

            result = await self.tasks_db.create(task_data)
            task_id = result["id"]

            logger.info(f"Retention cleanup scheduled: {task_id} for {data_category.value}")
            return task_id

        except Exception as e:
            logger.error(f"Failed to schedule retention cleanup: {e}")
            raise

    async def execute_retention_cleanup(self, task_id: str) -> RetentionCleanupResult:
        """
        Execute a scheduled retention cleanup task.

        Args:
            task_id: Task ID to execute

        Returns:
            Cleanup result
        """
        try:
            # Get task details
            task = await self.tasks_db.get(task_id)
            if not task:
                raise ValueError("Task not found")

            # Update task status
            await self.tasks_db.update(
                task_id, {"status": "running", "started_at": datetime.now(UTC).isoformat()}
            )

            # Execute cleanup based on data category
            data_category = DataCategory(task["data_category"])
            policy = RetentionPolicy(**task["retention_policy"])

            start_time = datetime.now(UTC)
            result = await self._execute_cleanup_for_category(data_category, policy)
            end_time = datetime.now(UTC)

            # Create cleanup result
            cleanup_result = RetentionCleanupResult(
                data_category=data_category.value,
                retention_policy=f"{policy.retention_period.value} ({policy.retention_days} days)",
                records_scanned=result["scanned"],
                records_deleted=result["deleted"],
                records_retained=result["retained"],
                errors_encountered=len(result.get("errors", [])),
                duration_seconds=(end_time - start_time).total_seconds(),
                cleanup_date=end_time,
                next_cleanup_date=end_time + timedelta(days=30),  # Schedule next cleanup
            )

            # Store result
            result_data = cleanup_result.dict()
            result_data["task_id"] = task_id
            result_data["created_at"] = datetime.now(UTC).isoformat()
            await self.results_db.create(result_data)

            # Update task status
            await self.tasks_db.update(
                task_id,
                {
                    "status": "completed",
                    "completed_date": datetime.now(UTC).isoformat(),
                    "records_processed": result["scanned"],
                    "records_deleted": result["deleted"],
                    "errors": result.get("errors", []),
                },
            )

            logger.info(
                f"Retention cleanup completed: {task_id} - {result['deleted']} records deleted"
            )
            return cleanup_result

        except Exception as e:
            logger.error(f"Failed to execute retention cleanup {task_id}: {e}")
            await self.tasks_db.update(
                task_id,
                {
                    "status": "failed",
                    "completed_date": datetime.now(UTC).isoformat(),
                    "errors": [str(e)],
                },
            )
            raise

    async def _execute_cleanup_for_category(
        self, data_category: DataCategory, policy: RetentionPolicy
    ) -> dict[str, Any]:
        """Execute cleanup for a specific data category."""
        try:
            cutoff_date = datetime.now(UTC) - timedelta(days=policy.retention_days)

            if data_category == DataCategory.USER_PROFILE:
                result = await self._cleanup_profiles(cutoff_date, policy)
            elif data_category == DataCategory.RESUME_DATA:
                result = await self._cleanup_resumes(cutoff_date, policy)
            elif data_category == DataCategory.JOB_DESCRIPTIONS:
                result = await self._cleanup_job_descriptions(cutoff_date, policy)
            elif data_category == DataCategory.OPTIMIZATION_RESULTS:
                result = await self._cleanup_optimizations(cutoff_date, policy)
            elif data_category == DataCategory.USAGE_ANALYTICS:
                result = await self._cleanup_usage_analytics(cutoff_date, policy)
            else:
                result = {
                    "scanned": 0,
                    "deleted": 0,
                    "retained": 0,
                    "errors": ["Unsupported data category"],
                }

            return result

        except Exception as e:
            logger.error(f"Cleanup failed for {data_category.value}: {e}")
            return {"scanned": 0, "deleted": 0, "retained": 0, "errors": [str(e)]}

    async def _cleanup_profiles(
        self, cutoff_date: datetime, policy: RetentionPolicy
    ) -> dict[str, Any]:
        """Cleanup user profiles past retention period."""
        try:
            # Get profiles past retention date
            profiles_to_delete = await self.profiles_db.list(
                filters={
                    "created_at__lt": cutoff_date.isoformat(),
                    "deleted_at": "null",  # Only active profiles
                }
            )

            deleted_count = 0
            errors = []

            for profile in profiles_to_delete:
                try:
                    if policy.deletion_method == "soft_delete":
                        await self.profiles_db.update(
                            profile["id"], {"deleted_at": datetime.now(UTC).isoformat()}
                        )
                    elif policy.deletion_method == "permanent_delete":
                        await self.profiles_db.delete(profile["id"])

                    deleted_count += 1

                except Exception as e:
                    errors.append(f"Failed to delete profile {profile['id']}: {e}")

            return {
                "scanned": len(profiles_to_delete),
                "deleted": deleted_count,
                "retained": len(profiles_to_delete) - deleted_count,
                "errors": errors,
            }

        except Exception as e:
            logger.error(f"Profile cleanup failed: {e}")
            return {"scanned": 0, "deleted": 0, "retained": 0, "errors": [str(e)]}

    async def _cleanup_resumes(
        self, cutoff_date: datetime, policy: RetentionPolicy
    ) -> dict[str, Any]:
        """Cleanup resume data past retention period."""
        try:
            # Get resumes past retention date
            resumes_to_delete = await self.resumes_db.list(
                filters={"created_at__lt": cutoff_date.isoformat(), "deleted_at": "null"}
            )

            deleted_count = 0
            errors = []

            for resume in resumes_to_delete:
                try:
                    if policy.deletion_method == "soft_delete":
                        await self.resumes_db.update(
                            resume["id"], {"deleted_at": datetime.now(UTC).isoformat()}
                        )
                    elif policy.deletion_method == "permanent_delete":
                        await self.resumes_db.delete(resume["id"])

                    deleted_count += 1

                except Exception as e:
                    errors.append(f"Failed to delete resume {resume['id']}: {e}")

            return {
                "scanned": len(resumes_to_delete),
                "deleted": deleted_count,
                "retained": len(resumes_to_delete) - deleted_count,
                "errors": errors,
            }

        except Exception as e:
            logger.error(f"Resume cleanup failed: {e}")
            return {"scanned": 0, "deleted": 0, "retained": 0, "errors": [str(e)]}

    async def _cleanup_job_descriptions(
        self, cutoff_date: datetime, policy: RetentionPolicy
    ) -> dict[str, Any]:
        """Cleanup job descriptions past retention period."""
        try:
            job_descriptions_to_delete = await self.job_descriptions_db.list(
                filters={"created_at__lt": cutoff_date.isoformat(), "deleted_at": "null"}
            )

            deleted_count = 0
            errors = []

            for job_desc in job_descriptions_to_delete:
                try:
                    if policy.deletion_method == "soft_delete":
                        await self.job_descriptions_db.update(
                            job_desc["id"], {"deleted_at": datetime.now(UTC).isoformat()}
                        )
                    elif policy.deletion_method == "permanent_delete":
                        await self.job_descriptions_db.delete(job_desc["id"])

                    deleted_count += 1

                except Exception as e:
                    errors.append(f"Failed to delete job description {job_desc['id']}: {e}")

            return {
                "scanned": len(job_descriptions_to_delete),
                "deleted": deleted_count,
                "retained": len(job_descriptions_to_delete) - deleted_count,
                "errors": errors,
            }

        except Exception as e:
            logger.error(f"Job description cleanup failed: {e}")
            return {"scanned": 0, "deleted": 0, "retained": 0, "errors": [str(e)]}

    async def _cleanup_optimizations(
        self, cutoff_date: datetime, policy: RetentionPolicy
    ) -> dict[str, Any]:
        """Cleanup optimization results past retention period."""
        try:
            optimizations_to_delete = await self.optimizations_db.list(
                filters={"created_at__lt": cutoff_date.isoformat(), "deleted_at": "null"}
            )

            deleted_count = 0
            errors = []

            for optimization in optimizations_to_delete:
                try:
                    if policy.deletion_method == "soft_delete":
                        await self.optimizations_db.update(
                            optimization["id"], {"deleted_at": datetime.now(UTC).isoformat()}
                        )
                    elif policy.deletion_method == "permanent_delete":
                        await self.optimizations_db.delete(optimization["id"])

                    deleted_count += 1

                except Exception as e:
                    errors.append(f"Failed to delete optimization {optimization['id']}: {e}")

            return {
                "scanned": len(optimizations_to_delete),
                "deleted": deleted_count,
                "retained": len(optimizations_to_delete) - deleted_count,
                "errors": errors,
            }

        except Exception as e:
            logger.error(f"Optimization cleanup failed: {e}")
            return {"scanned": 0, "deleted": 0, "retained": 0, "errors": [str(e)]}

    async def _cleanup_usage_analytics(
        self, cutoff_date: datetime, policy: RetentionPolicy
    ) -> dict[str, Any]:
        """Cleanup usage analytics past retention period."""
        try:
            analytics_to_delete = await self.usage_tracking_db.list(
                filters={"created_at__lt": cutoff_date.isoformat()}
            )

            deleted_count = 0
            errors = []

            for analytics in analytics_to_delete:
                try:
                    if policy.deletion_method == "anonymize":
                        # Anonymize user data
                        await self.usage_tracking_db.update(
                            analytics["id"], {"user_id": "anonymized"}
                        )
                        deleted_count += 1
                    elif policy.deletion_method == "soft_delete":
                        await self.usage_tracking_db.update(
                            analytics["id"], {"deleted_at": datetime.now(UTC).isoformat()}
                        )
                        deleted_count += 1
                    elif policy.deletion_method == "permanent_delete":
                        await self.usage_tracking_db.delete(analytics["id"])
                        deleted_count += 1

                except Exception as e:
                    errors.append(f"Failed to process analytics {analytics['id']}: {e}")

            return {
                "scanned": len(analytics_to_delete),
                "deleted": deleted_count,
                "retained": len(analytics_to_delete) - deleted_count,
                "errors": errors,
            }

        except Exception as e:
            logger.error(f"Usage analytics cleanup failed: {e}")
            return {"scanned": 0, "deleted": 0, "retained": 0, "errors": [str(e)]}

    async def get_retention_status(self) -> dict[str, Any]:
        """
        Get comprehensive retention status.

        Returns:
            Retention status information
        """
        try:
            policies = await self.get_retention_policies()
            status = {
                "total_policies": len(policies),
                "policies_by_category": {},
                "recent_cleanup_results": [],
                "scheduled_tasks": [],
                "compliance_status": "compliant",
            }

            # Get policy breakdown
            for policy in policies:
                category = policy.data_category.value
                if category not in status["policies_by_category"]:
                    status["policies_by_category"][category] = []

                status["policies_by_category"][category].append(
                    {
                        "retention_period": policy.retention_period.value,
                        "retention_days": policy.retention_days,
                        "auto_cleanup": policy.auto_cleanup,
                        "deletion_method": policy.deletion_method,
                    }
                )

            # Get recent cleanup results
            try:
                recent_results = await self.results_db.list(
                    filters={}, order_by="created_at", limit=10
                )
                status["recent_cleanup_results"] = recent_results
            except Exception:
                status["recent_cleanup_results"] = []

            # Get scheduled tasks
            try:
                scheduled_tasks = await self.tasks_db.list(
                    filters={"status": "pending"}, order_by="scheduled_date"
                )
                status["scheduled_tasks"] = scheduled_tasks
            except Exception:
                status["scheduled_tasks"] = []

            return status

        except Exception as e:
            logger.error(f"Failed to get retention status: {e}")
            return {"error": str(e)}

    async def run_automatic_cleanup(self) -> list[RetentionCleanupResult]:
        """
        Run automatic cleanup for all policies with auto_cleanup enabled.

        Returns:
            List of cleanup results
        """
        try:
            policies = await self.get_retention_policies()
            results = []

            for policy in policies:
                if policy.auto_cleanup:
                    try:
                        task_id = await self.schedule_retention_cleanup(policy.data_category)
                        result = await self.execute_retention_cleanup(task_id)
                        results.append(result)
                    except Exception as e:
                        logger.error(
                            f"Automatic cleanup failed for {policy.data_category.value}: {e}"
                        )

            return results

        except Exception as e:
            logger.error(f"Failed to run automatic cleanup: {e}")
            raise


# Global retention manager instance
retention_manager = RetentionManager()


async def schedule_retention_cleanup(data_category: DataCategory) -> str:
    """
    Convenience function to schedule retention cleanup.

    Args:
        data_category: Data category to clean up

    Returns:
        Task ID
    """
    return await retention_manager.schedule_retention_cleanup(data_category)


async def run_automatic_cleanup() -> list[RetentionCleanupResult]:
    """
    Convenience function to run automatic cleanup.

    Returns:
        List of cleanup results
    """
    return await retention_manager.run_automatic_cleanup()
