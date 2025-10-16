"""
Comprehensive file security utilities for secure file uploads.

This module provides file validation, virus scanning, and security checks
to prevent malicious file uploads and ensure file integrity.
"""

import hashlib
import logging
import os
import re
import tempfile
from typing import Any

import magic
from pydantic import BaseModel

logger = logging.getLogger(__name__)


class FileSecurityConfig(BaseModel):
    """Configuration for file security validation."""

    # File size limits (in bytes)
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    min_file_size: int = 1  # 1 byte

    # Allowed file types
    allowed_mime_types: set[str] = {
        "application/pdf",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "text/plain",
    }

    allowed_extensions: set[str] = {".pdf", ".docx", ".txt"}

    # Content validation settings
    scan_for_malware: bool = True
    validate_content_signature: bool = True
    check_for_embedded_scripts: bool = True

    # Metadata validation
    max_filename_length: int = 255
    allowed_filename_chars: str = r"^[a-zA-Z0-9._\-\s]+$"

    # Temporary file handling
    cleanup_temp_files: bool = True


class FileSecurityResult(BaseModel):
    """Result of file security validation."""

    is_safe: bool
    file_info: dict[str, Any]
    warnings: list[str] = []
    errors: list[str] = []
    blocked_patterns: list[str] = []
    checksum: str | None = None
    metadata: dict[str, Any] = {}


class FileSecurityValidator:
    """Comprehensive file security validator."""

    def __init__(self, config: FileSecurityConfig | None = None):
        """Initialize file security validator."""
        self.config = config or FileSecurityConfig()
        self._init_malware_patterns()

    def _init_malware_patterns(self) -> None:
        """Initialize malware and malicious content patterns."""
        self.malware_patterns = {
            # Executable signatures
            "executable_signatures": [
                b"MZ",  # Windows PE executable
                b"\x7fELF",  # Linux executable
                b"\xca\xfe\xba\xbe",  # Java class file
                b"\xfe\xed\xfa\xce",  # Mach-O binary (macOS)
                b"\xfe\xed\xfa\xcf",  # Mach-O binary (macOS)
            ],
            # Script content patterns
            "script_patterns": [
                rb"<script[^>]*>.*?</script>",
                rb"javascript:",
                rb"vbscript:",
                rb"onload\s*=",
                rb"onerror\s*=",
                rb"onclick\s*=",
                rb"eval\s*\(",
                rb"exec\s*\(",
            ],
            # Suspicious content patterns
            "suspicious_content": [
                rb"base64_decode",
                rb"shell_exec",
                rb"system\s*\(",
                rb"passthru",
                rb"file_get_contents",
                rb"curl_exec",
                rb"\$_POST",
                rb"\$_GET",
                rb"\$_REQUEST",
            ],
            # Macro patterns for Office documents
            "macro_patterns": [
                rb"vbaProject",
                rb"AutoOpen",
                rb"AutoExec",
                rb"Document_Open",
                rb"Workbook_Open",
            ],
        }

    def validate_file(
        self,
        file_content: bytes,
        filename: str,
        content_type: str | None = None,
    ) -> FileSecurityResult:
        """
        Comprehensive file security validation.

        Args:
            file_content: File content as bytes
            filename: Original filename
            content_type: Declared content type

        Returns:
            FileSecurityResult with validation details
        """
        result = FileSecurityResult(
            is_safe=True,
            file_info={
                "filename": filename,
                "content_type": content_type,
                "size": len(file_content),
            },
            metadata={},
        )

        try:
            # Step 1: Basic validation
            self._validate_basic_properties(file_content, filename, result)

            # Step 2: Filename validation
            self._validate_filename(filename, result)

            # Step 3: Content type validation
            self._validate_content_type(file_content, content_type, result)

            # Step 4: Content signature validation
            if self.config.validate_content_signature:
                self._validate_content_signature(file_content, result)

            # Step 5: Malware scanning
            if self.config.scan_for_malware:
                self._scan_for_malware(file_content, result)

            # Step 6: Script detection
            if self.config.check_for_embedded_scripts:
                self._scan_for_scripts(file_content, result)

            # Step 7: Generate checksum
            result.checksum = self._generate_checksum(file_content)

            # Step 8: Extract safe metadata
            self._extract_metadata(file_content, result)

            logger.info(f"File security validation completed for {filename}: safe={result.is_safe}")

        except Exception as e:
            logger.error(f"Error during file security validation: {str(e)}")
            result.is_safe = False
            result.errors.append(f"Validation error: {str(e)}")

        return result

    def _validate_basic_properties(
        self, file_content: bytes, filename: str, result: FileSecurityResult
    ) -> None:
        """Validate basic file properties."""
        file_size = len(file_content)

        # Check file size limits
        if file_size < self.config.min_file_size:
            result.is_safe = False
            result.errors.append(f"File too small: {file_size} bytes")
            return

        if file_size > self.config.max_file_size:
            result.is_safe = False
            result.errors.append(
                f"File too large: {file_size} bytes (max: {self.config.max_file_size})"
            )
            return

        # Check for empty files
        if not file_content.strip():
            result.is_safe = False
            result.errors.append("File is empty or contains only whitespace")
            return

        result.warnings.append(f"File size validation passed: {file_size} bytes")

    def _validate_filename(self, filename: str, result: FileSecurityResult) -> None:
        """Validate filename against security threats."""
        # Check filename length
        if len(filename) > self.config.max_filename_length:
            result.is_safe = False
            result.errors.append(f"Filename too long: {len(filename)} characters")
            return

        # Check for path traversal
        if ".." in filename or "/" in filename or "\\" in filename:
            result.is_safe = False
            result.errors.append("Path traversal detected in filename")
            return

        # Check for null bytes
        if "\x00" in filename:
            result.is_safe = False
            result.errors.append("Null bytes detected in filename")
            return

        # Check for dangerous characters
        dangerous_chars = ["<", ">", ":", '"', "|", "?", "*"]
        if any(char in filename for char in dangerous_chars):
            result.is_safe = False
            result.errors.append(f"Dangerous characters in filename: {filename}")
            return

        # Check filename pattern
        if not re.match(self.config.allowed_filename_chars, filename):
            result.is_safe = False
            result.errors.append("Filename contains invalid characters")
            return

        # Check file extension
        file_ext = os.path.splitext(filename)[1].lower()
        if file_ext not in self.config.allowed_extensions:
            result.is_safe = False
            result.errors.append(f"File extension not allowed: {file_ext}")
            return

        result.warnings.append(f"Filename validation passed: {filename}")

    def _validate_content_type(
        self, file_content: bytes, content_type: str | None, result: FileSecurityResult
    ) -> None:
        """Validate content type matches file content."""
        # Detect actual content type
        try:
            actual_content_type = magic.from_buffer(file_content, mime=True)
        except Exception as e:
            logger.warning(f"Failed to detect content type: {str(e)}")
            actual_content_type = None

        # Validate declared content type
        if content_type:
            if content_type not in self.config.allowed_mime_types:
                result.is_safe = False
                result.errors.append(f"Content type not allowed: {content_type}")
                return

        # Validate actual content type
        if actual_content_type:
            if actual_content_type not in self.config.allowed_mime_types:
                result.is_safe = False
                result.errors.append(f"Detected content type not allowed: {actual_content_type}")
                return

            # Check for content type mismatch
            if content_type and content_type != actual_content_type:
                result.warnings.append(
                    f"Content type mismatch: declared={content_type}, detected={actual_content_type}"
                )

        result.file_info["detected_content_type"] = actual_content_type
        result.warnings.append(f"Content type validation passed: {actual_content_type}")

    def _validate_content_signature(self, file_content: bytes, result: FileSecurityResult) -> None:
        """Validate file content signature (magic numbers)."""
        # PDF signature
        if file_content.startswith(b"%PDF"):
            if not self._validate_pdf_signature(file_content):
                result.is_safe = False
                result.errors.append("Invalid PDF signature detected")
                return
            result.warnings.append("PDF signature validation passed")

        # DOCX signature (ZIP container)
        elif file_content.startswith(b"PK\x03\x04"):
            if not self._validate_docx_signature(file_content):
                result.is_safe = False
                result.errors.append("Invalid DOCX signature detected")
                return
            result.warnings.append("DOCX signature validation passed")

        # Plain text
        elif self._is_plain_text(file_content):
            result.warnings.append("Plain text file detected")

        else:
            result.is_safe = False
            result.errors.append("Unknown or invalid file signature")

    def _validate_pdf_signature(self, content: bytes) -> bool:
        """Validate PDF file signature."""
        if not content.startswith(b"%PDF-"):
            return False

        # Check for PDF version
        try:
            version_line = content.split(b"\n")[0].decode("utf-8")
            if not re.match(r"%PDF-\d\.\d", version_line):
                return False
        except (UnicodeDecodeError, IndexError):
            return False

        # Look for %%EOF marker
        if b"%%EOF" not in content[-1024:]:  # Check last 1KB
            return False

        return True

    def _validate_docx_signature(self, content: bytes) -> bool:
        """Validate DOCX file signature."""
        if not content.startswith(b"PK\x03\x04"):
            return False

        # DOCX files should contain specific XML files
        try:
            import io
            import zipfile

            with zipfile.ZipFile(io.BytesIO(content)) as zip_file:
                required_files = ["[Content_Types].xml", "word/document.xml"]
                for req_file in required_files:
                    if req_file not in zip_file.namelist():
                        return False

                # Check for suspicious files
                suspicious_files = ["vbaProject.bin", "word/vbaProject.bin"]
                for susp_file in suspicious_files:
                    if susp_file in zip_file.namelist():
                        return False

        except Exception:
            return False

        return True

    def _is_plain_text(self, content: bytes) -> bool:
        """Check if content is plain text."""
        try:
            # Try to decode as UTF-8
            content.decode("utf-8")
            return True
        except UnicodeDecodeError:
            return False

    def _scan_for_malware(self, file_content: bytes, result: FileSecurityResult) -> None:
        """Scan for malware patterns."""
        content_lower = file_content.lower()

        # Check for executable signatures
        for pattern_name, patterns in self.malware_patterns.items():
            for pattern in patterns:
                if pattern in content_lower:
                    result.is_safe = False
                    result.errors.append(f"Malicious pattern detected: {pattern_name}")
                    result.blocked_patterns.append(pattern_name)
                    return

        result.warnings.append("Malware scan passed")

    def _scan_for_scripts(self, file_content: bytes, result: FileSecurityResult) -> None:
        """Scan for embedded scripts."""
        # Check for script patterns
        for pattern in self.malware_patterns["script_patterns"]:
            if re.search(pattern, file_content, re.IGNORECASE | re.DOTALL):
                pattern_name = pattern.decode("utf-8", errors="ignore")[
                    :20
                ]  # Truncate for readability
                result.warnings.append(f"Script pattern detected: {pattern_name}")
                result.blocked_patterns.append("script_pattern")

        # Additional checks for Office documents
        if file_content.startswith(b"PK\x03\x04"):  # DOCX
            self._scan_docx_macros(file_content, result)

    def _scan_docx_macros(self, file_content: bytes, result: FileSecurityResult) -> None:
        """Scan DOCX files for macros."""
        try:
            import io
            import zipfile

            with zipfile.ZipFile(io.BytesIO(file_content)) as zip_file:
                # Check for macro-related files
                macro_files = [
                    "vbaProject.bin",
                    "word/vbaProject.bin",
                    "xl/vbaProject.bin",
                    "ppt/vbaProject.bin",
                ]

                for macro_file in macro_files:
                    if macro_file in zip_file.namelist():
                        result.warnings.append("VBA macros detected in document")
                        result.blocked_patterns.append("office_macros")
                        break

        except Exception as e:
            logger.warning(f"Failed to scan for DOCX macros: {str(e)}")

    def _generate_checksum(self, file_content: bytes) -> str:
        """Generate SHA-256 checksum of file content."""
        return hashlib.sha256(file_content).hexdigest()

    def _extract_metadata(self, file_content: bytes, result: FileSecurityResult) -> None:
        """Extract safe metadata from file."""
        metadata: dict[str, Any] = {}

        # File info
        metadata["file_size"] = len(file_content)
        metadata["checksum"] = result.checksum

        # Content type info
        try:
            detected_type = magic.from_buffer(file_content)
            metadata["detected_type"] = detected_type
        except Exception:
            pass

        # PDF metadata
        if file_content.startswith(b"%PDF"):
            metadata.update(self._extract_pdf_metadata(file_content))

        # Store metadata
        result.metadata = metadata

    def _extract_pdf_metadata(self, content: bytes) -> dict[str, Any]:
        """Extract safe metadata from PDF file."""
        metadata: dict[str, Any] = {"file_type": "PDF"}

        try:
            # Extract PDF version
            content_str = content.decode("utf-8", errors="ignore")
            version_match = re.search(r"%PDF-(\d\.\d)", content_str)
            if version_match:
                metadata["pdf_version"] = version_match.group(1)

            # Count pages (basic estimation)
            page_count = content_str.count("/Type /Page")
            metadata["estimated_pages"] = str(page_count)

        except Exception as e:
            logger.warning(f"Failed to extract PDF metadata: {str(e)}")

        return metadata


# Global validator instance
default_validator = FileSecurityValidator()


def validate_file_security(
    file_content: bytes,
    filename: str,
    content_type: str | None = None,
    config: FileSecurityConfig | None = None,
) -> FileSecurityResult:
    """
    Validate file security using default or custom validator.

    Args:
        file_content: File content as bytes
        filename: Original filename
        content_type: Declared content type
        config: Optional custom configuration

    Returns:
        FileSecurityResult with validation details
    """
    validator = FileSecurityValidator(config) if config else default_validator
    return validator.validate_file(file_content, filename, content_type)


def secure_file_cleanup(filepath: str) -> bool:
    """
    Securely delete a temporary file.

    Args:
        filepath: Path to file to delete

    Returns:
        True if deletion successful
    """
    try:
        if os.path.exists(filepath):
            os.remove(filepath)
            logger.info(f"Securely deleted temporary file: {filepath}")
            return True
    except Exception as e:
        logger.error(f"Failed to delete temporary file {filepath}: {str(e)}")
    return False


def create_secure_temp_file(suffix: str = ".tmp") -> str:
    """
    Create a secure temporary file.

    Args:
        suffix: File suffix

    Returns:
        Path to temporary file
    """
    fd, temp_path = tempfile.mkstemp(suffix=suffix)
    os.close(fd)
    return temp_path
