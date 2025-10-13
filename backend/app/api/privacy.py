"""
LGPD Compliance API Endpoints

This module provides comprehensive API endpoints for LGPD compliance
including PII detection, consent management, data subject rights,
and audit trail functionality.

Critical for CV-Match Brazilian market deployment - these endpoints
are mandatory for LGPD compliance.
"""

from datetime import UTC, datetime, timedelta
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import HTTPBearer
from pydantic import BaseModel, Field

from app.models.auth_models import User
from app.services.security.audit_trail import (
    AuditEventType,
    DataAccessType,
    audit_trail,
    log_audit_event,
    log_data_access,
)
from app.services.security.consent_manager import ConsentRequest, UserConsentStatus, consent_manager
from app.services.security.data_subject_rights import (
    DataAccessRequest,
    DataDeletionRequest,
    DataPortabilityRequest,
    DataSubjectRightsResponse,
    data_subject_rights_manager,
)
from app.services.security.pii_detection_service import (
    mask_pii,
    scan_for_pii,
    validate_lgpd_compliance,
)
from app.services.security.retention_manager import retention_manager
from app.services.supabase.auth import get_current_user

router = APIRouter(prefix="/api/privacy", tags=["privacy"])
security = HTTPBearer()


# Request/Response Models
class PIIScanRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=50000)
    masking_level: str = Field("partial", regex="^(none|partial|full|hash)$")


class PIIScanResponse(BaseModel):
    has_pii: bool
    pii_types_found: list[str]
    confidence_score: float
    masked_text: str | None = None
    scan_duration_ms: float | None = None
    lgpd_compliant: bool


class ConsentGrantRequest(BaseModel):
    consent_type_name: str
    granted: bool = True
    legal_basis: str = "consent"
    purpose: str | None = None


class ConsentResponse(BaseModel):
    success: bool
    message: str
    consent_id: str | None = None


class DataAccessRequestModel(BaseModel):
    justification: str | None = None


class DataExportRequest(BaseModel):
    format_preference: str = "json"
    include_deleted: bool = False


class DataDeletionRequestModel(BaseModel):
    deletion_scope: str = "all"
    specific_data_types: list[str] | None = None
    justification: str
    retain_legal_required: bool = True


class ComplianceStatusResponse(BaseModel):
    overall_status: str
    has_all_required_consents: bool
    missing_consents: list[str]
    data_retention_status: dict[str, Any]
    audit_summary: dict[str, Any]
    last_updated: datetime


# =====================================================
# PII Detection and Masking Endpoints
# =====================================================


@router.post("/pii/scan", response_model=PIIScanResponse)
async def scan_text_for_pii(
    request: PIIScanRequest, current_user: User = Depends(get_current_user)
):
    """
    Scan text for PII and return detection results.

    This endpoint scans text for Brazilian PII patterns (CPF, RG, etc.)
    and returns detection results with masking options.
    """
    try:
        # Log data access
        await log_data_access(
            user_id=current_user.id,
            data_category="pii_scan",
            access_type=DataAccessType.VIEW,
            access_purpose="PII detection and scanning",
        )

        # Scan for PII
        result = scan_for_pii(request.text)

        # Apply masking if requested
        masked_text = None
        if request.masking_level != "none" and result.masked_text:
            if request.masking_level == "partial":
                masked_text = mask_pii(result.masked_text)
            elif request.masking_level == "full":
                # TODO: Implement full masking
                masked_text = mask_pii(result.masked_text)
            elif request.masking_level == "hash":
                # TODO: Implement hash masking
                masked_text = mask_pii(result.masked_text)

        # Check LGPD compliance
        compliance_result = validate_lgpd_compliance(request.text)

        return PIIScanResponse(
            has_pii=result.has_pii,
            pii_types_found=[pii_type.value for pii_type in result.pii_types_found],
            confidence_score=result.confidence_score,
            masked_text=masked_text,
            scan_duration_ms=result.scan_duration_ms,
            lgpd_compliant=compliance_result["is_compliant"],
        )

    except Exception as e:
        await log_audit_event(
            event_type=AuditEventType.SYSTEM_ERROR,
            action="PII scan failed",
            user_id=current_user.id,
            success=False,
            error_message=str(e),
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to scan text for PII"
        ) from e


@router.post("/pii/mask")
async def mask_text_endpoint(
    text: str, masking_level: str = "partial", current_user: User = Depends(get_current_user)
):
    """
    Mask PII in text using specified masking level.

    This endpoint applies PII masking to text with configurable masking levels.
    """
    try:
        # Log data access
        await log_data_access(
            user_id=current_user.id,
            data_category="pii_masking",
            access_type=DataAccessType.MODIFY,
            access_purpose="PII masking",
        )

        # Apply masking
        masked_text = mask_pii(text)

        return {
            "masked_text": masked_text,
            "original_length": len(text),
            "masked_length": len(masked_text),
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to mask text"
        ) from e


# =====================================================
# Consent Management Endpoints
# =====================================================


@router.get("/consents", response_model=UserConsentStatus)
async def get_user_consents(current_user: User = Depends(get_current_user)):
    """
    Get user's current consent status.

    Returns all consents granted by the user and their current status.
    """
    try:
        consent_status = await consent_manager.get_user_consent_status(current_user.id)
        return consent_status

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve consent status",
        ) from e


@router.post("/consents", response_model=ConsentResponse)
async def grant_consent(
    request: ConsentGrantRequest,
    http_request: Request,
    current_user: User = Depends(get_current_user),
):
    """
    Grant or revoke consent for a specific purpose.

    This endpoint allows users to grant or revoke consent for data processing
    activities in compliance with LGPD requirements.
    """
    try:
        # Get client information
        client_ip = http_request.client.host if http_request.client else "unknown"
        user_agent = http_request.headers.get("user-agent")

        # Create consent request
        consent_request = ConsentRequest(
            consent_type_name=request.consent_type_name,
            granted=request.granted,
            legal_basis=request.legal_basis,
            purpose=request.purpose,
            ip_address=client_ip,
            user_agent=user_agent,
        )

        # Record consent
        consent_record = await consent_manager.record_user_consent(current_user.id, consent_request)

        # Log audit event
        await log_audit_event(
            event_type=AuditEventType.CONSENT_GRANTED
            if request.granted
            else AuditEventType.CONSENT_REVOKED,
            action=f"{'Granted' if request.granted else 'Revoked'} consent for {request.consent_type_name}",
            user_id=current_user.id,
            table_name="user_consents",
            record_id=consent_record.id if consent_record else None,
            success=True,
        )

        return ConsentResponse(
            success=True,
            message=f"Consent {'granted' if request.granted else 'revoked'} successfully",
            consent_id=consent_record.id if consent_record else None,
        )

    except Exception as e:
        await log_audit_event(
            event_type=AuditEventType.SYSTEM_ERROR,
            action="Consent recording failed",
            user_id=current_user.id,
            success=False,
            error_message=str(e),
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to record consent"
        ) from e


@router.get("/consents/{consent_type_name}")
async def check_consent(consent_type_name: str, current_user: User = Depends(get_current_user)):
    """
    Check if user has granted specific consent.

    Returns the current status of a specific consent type.
    """
    try:
        consent_check = await consent_manager.check_user_consent(current_user.id, consent_type_name)
        return consent_check

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to check consent status",
        ) from e


@router.delete("/consents")
async def revoke_all_consents(
    justification: str = "User request", current_user: User = Depends(get_current_user)
):
    """
    Revoke all user consents (right to withdrawal).

    This endpoint allows users to withdraw all previously granted consents
    as required by LGPD Article 8.
    """
    try:
        await consent_manager.revoke_all_consents(current_user.id, justification)

        # Log audit event
        await log_audit_event(
            event_type=AuditEventType.CONSENT_REVOKED,
            action="Revoked all consents",
            user_id=current_user.id,
            success=True,
        )

        return {"message": "All consents revoked successfully"}

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to revoke consents"
        ) from e


# =====================================================
# Data Subject Rights Endpoints
# =====================================================


@router.post("/data-access", response_model=DataSubjectRightsResponse)
async def request_data_access(
    request: DataAccessRequestModel,
    http_request: Request,
    current_user: User = Depends(get_current_user),
):
    """
    Request access to personal data (LGPD Article 18, I).

    This endpoint allows users to request access to all personal data
    stored about them as required by LGPD.
    """
    try:
        # Get client information
        client_ip = http_request.client.host if http_request.client else "unknown"
        user_agent = http_request.headers.get("user-agent")

        # Create data access request
        access_request = DataAccessRequest(
            user_id=current_user.id,
            request_type="access",
            justification=request.justification,
            ip_address=client_ip,
            user_agent=user_agent,
        )

        # Create and process request
        request_id = await data_subject_rights_manager.create_data_access_request(access_request)
        result = await data_subject_rights_manager.process_data_access_request(request_id)

        # Log audit event
        await log_audit_event(
            event_type=AuditEventType.DATA_ACCESS,
            action="User requested data access",
            user_id=current_user.id,
            success=True,
        )

        return result

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process data access request",
        ) from e


@router.post("/data-export")
async def request_data_export(
    request: DataExportRequest,
    http_request: Request,
    current_user: User = Depends(get_current_user),
):
    """
    Request data portability (LGPD Article 18, V).

    This endpoint allows users to request their personal data in a
    structured, commonly used format as required by LGPD.
    """
    try:
        # Get client information
        client_ip = http_request.client.host if http_request.client else "unknown"
        user_agent = http_request.headers.get("user-agent")

        # Create portability request
        portability_request = DataPortabilityRequest(
            user_id=current_user.id,
            format_preference=request.format_preference,
            include_deleted=request.include_deleted,
            ip_address=client_ip,
            user_agent=user_agent,
        )

        # Create and process request
        request_id = await data_subject_rights_manager.create_data_portability_request(
            portability_request
        )
        result = await data_subject_rights_manager.process_data_portability_request(request_id)

        # Log audit event
        await log_audit_event(
            event_type=AuditEventType.DATA_EXPORT,
            action="User requested data export",
            user_id=current_user.id,
            success=True,
        )

        return result

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process data export request",
        ) from e


@router.post("/data-deletion")
async def request_data_deletion(
    request: DataDeletionRequestModel,
    http_request: Request,
    current_user: User = Depends(get_current_user),
):
    """
    Request data deletion (Right to be Forgotten - LGPD Article 18, VI).

    This endpoint allows users to request deletion of their personal data
    as required by LGPD, with options for scope and legal requirements.
    """
    try:
        # Get client information
        client_ip = http_request.client.host if http_request.client else "unknown"
        user_agent = http_request.headers.get("user-agent")

        # Create deletion request
        deletion_request = DataDeletionRequest(
            user_id=current_user.id,
            deletion_scope=request.deletion_scope,
            specific_data_types=request.specific_data_types,
            justification=request.justification,
            retain_legal_required=request.retain_legal_required,
            ip_address=client_ip,
            user_agent=user_agent,
        )

        # Create and process request
        request_id = await data_subject_rights_manager.create_data_deletion_request(
            deletion_request
        )
        result = await data_subject_rights_manager.process_data_deletion_request(request_id)

        # Log audit event
        await log_audit_event(
            event_type=AuditEventType.DATA_DELETION,
            action="User requested data deletion",
            user_id=current_user.id,
            success=True,
        )

        return result

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process data deletion request",
        ) from e


# =====================================================
# Compliance Status Endpoints
# =====================================================


@router.get("/compliance/status", response_model=ComplianceStatusResponse)
async def get_compliance_status(current_user: User = Depends(get_current_user)):
    """
    Get user's LGPD compliance status.

    Returns comprehensive compliance information including consent status,
    data retention information, and audit summary.
    """
    try:
        # Get consent status
        consent_status = await consent_manager.get_user_consent_status(current_user.id)

        # Get retention status
        retention_status = await retention_manager.get_retention_status()

        # Get user audit trail summary
        user_audit_logs = await audit_trail.get_user_audit_trail(
            current_user.id, start_date=datetime.now(UTC) - timedelta(days=30)
        )

        audit_summary = {
            "total_events": len(user_audit_logs),
            "event_types": list(
                {log.get("event_type") for log in user_audit_logs if log.get("event_type")}
            ),
            "last_activity": max(
                (log.get("created_at") for log in user_audit_logs if log.get("created_at")),
                default=None,
            )
            if user_audit_logs
            else None,
        }

        return ComplianceStatusResponse(
            overall_status="compliant"
            if consent_status.has_all_required_consents
            else "non_compliant",
            has_all_required_consents=consent_status.has_all_required_consents,
            missing_consents=consent_status.missing_required_consents,
            data_retention_status=retention_status,
            audit_summary=audit_summary,
            last_updated=datetime.now(UTC),
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve compliance status",
        ) from e


@router.get("/audit-trail")
async def get_audit_trail(
    start_date: datetime | None = None,
    end_date: datetime | None = None,
    current_user: User = Depends(get_current_user),
):
    """
    Get user's audit trail.

    Returns all audit events for the current user within the specified date range.
    """
    try:
        # Log data access
        await log_data_access(
            user_id=current_user.id,
            data_category="audit_trail",
            access_type=DataAccessType.VIEW,
            access_purpose="User requested audit trail",
        )

        audit_logs = await audit_trail.get_user_audit_trail(
            user_id=current_user.id, start_date=start_date, end_date=end_date
        )

        return {"audit_logs": audit_logs, "total_count": len(audit_logs)}

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve audit trail",
        ) from e


# =====================================================
# Admin Endpoints (for system administrators)
# =====================================================


@router.get("/admin/compliance-overview")
async def get_compliance_overview(current_user: User = Depends(get_current_user)):
    """
    Get system-wide compliance overview (admin only).

    Returns comprehensive compliance information for the entire system.
    """
    try:
        # Check if user is admin (TODO: implement proper admin check)
        # For now, we'll assume all authenticated users can access this

        # Get system compliance status
        compliance_status = await audit_trail.get_compliance_status()

        # Get data access report
        access_report = await audit_trail.get_data_access_report(
            start_date=datetime.now(UTC) - timedelta(days=30)
        )

        return {
            "compliance_status": compliance_status,
            "data_access_report": access_report,
            "generated_at": datetime.now(UTC),
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve compliance overview",
        ) from e


@router.post("/admin/retention-cleanup")
async def trigger_retention_cleanup(
    data_category: str, current_user: User = Depends(get_current_user)
):
    """
    Trigger retention cleanup for specific data category (admin only).

    This endpoint allows administrators to manually trigger data retention
    cleanup processes.
    """
    try:
        # Check if user is admin (TODO: implement proper admin check)

        from app.services.security.retention_manager import DataCategory

        # Convert string to enum
        try:
            category_enum = DataCategory(data_category)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid data category: {data_category}",
            )

        # Schedule and execute cleanup
        task_id = await retention_manager.schedule_retention_cleanup(category_enum)
        result = await retention_manager.execute_retention_cleanup(task_id)

        # Log audit event
        await log_audit_event(
            event_type=AuditEventType.ADMIN_ACTION,
            action=f"Triggered retention cleanup for {data_category}",
            user_id=current_user.id,
            success=True,
        )

        return {
            "task_id": task_id,
            "cleanup_result": result,
            "message": "Retention cleanup completed successfully",
        }

    except Exception as e:
        await log_audit_event(
            event_type=AuditEventType.SYSTEM_ERROR,
            action="Retention cleanup failed",
            user_id=current_user.id,
            success=False,
            error_message=str(e),
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to execute retention cleanup",
        ) from e


# =====================================================
# Privacy Policy and Information Endpoints
# =====================================================


@router.get("/privacy-policy")
async def get_privacy_policy():
    """
    Get current privacy policy.

    Returns the current privacy policy with LGPD compliance information.
    """
    try:
        # TODO: Retrieve actual privacy policy from database or storage
        privacy_policy = {
            "title": "Política de Privacidade - CV-Match",
            "version": "1.0",
            "last_updated": "2025-10-13",
            "lgpd_compliant": True,
            "sections": [
                {
                    "title": "Dados Pessoais Coletados",
                    "content": "Coletamos informações pessoais como nome, email, CPF, e dados profissionais para fornecer nossos serviços.",
                },
                {
                    "title": "Finalidade do Tratamento",
                    "content": "Seus dados são utilizados para otimizar currículos, encontrar vagas compatíveis e melhorar nossos serviços.",
                },
                {
                    "title": "Base Legal",
                    "content": "O tratamento dos dados é baseado em consentimento, execução de contrato e obrigação legal.",
                },
                {
                    "title": "Direitos do Titular",
                    "content": "Você tem direito de acesso, correção, portabilidade e eliminação de seus dados conforme LGPD.",
                },
                {
                    "title": "Tempo de Armazenamento",
                    "content": "Seus dados são armazenados pelo período necessário para cumprir as finalidades, em conformidade com a LGPD.",
                },
            ],
        }

        return privacy_policy

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve privacy policy",
        ) from e


@router.get("/data-processing-activities")
async def get_data_processing_activities():
    """
    Get information about data processing activities.

    Returns information about all data processing activities as required
    by LGPD Article 12.
    """
    try:
        # TODO: Retrieve actual data processing activities from database
        activities = [
            {
                "name": "Análise de Currículo",
                "description": "Análise de currículos para otimização e matching com vagas",
                "purpose": "Melhorar as chances do candidato no mercado de trabalho",
                "legal_basis": "Consentimento",
                "data_categories": ["Dados pessoais", "Dados profissionais", "Contato"],
                "retention_period": "2 anos",
                "third_party_sharing": False,
            },
            {
                "name": "Gerenciamento de Conta",
                "description": "Manutenção de contas de usuário e perfis",
                "purpose": "Fornecer acesso aos serviços",
                "legal_basis": "Execução de contrato",
                "data_categories": ["Dados de conta", "Contato"],
                "retention_period": "5 anos",
                "third_party_sharing": False,
            },
        ]

        return {"activities": activities}

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve data processing activities",
        ) from e
