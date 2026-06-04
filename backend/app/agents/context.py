"""Shared context checks for security agents."""
import ipaddress
import re
from typing import Any, Dict


INTERNAL_LOG_MARKERS = (
    "application log",
    "database debug message",
    "developer enabled debug mode",
    "last query",
    "sql audit log",
    "sql log",
    "debug mode",
)

INTERNAL_SERVICE_MARKERS = (
    "internal-service",
    "backend-service",
    "scheduler",
    "cron",
    "report-service",
)

NO_EXTERNAL_MARKERS = (
    "no external request detected",
    "response: ok",
)

ATTACK_PAYLOAD_MARKERS = (
    "' or '1'='1",
    "\" or \"1\"=\"1",
    " union select ",
    " sleep(",
    "benchmark(",
    "--",
    "/*",
    "*/",
    "jndi:",
    "sqlmap",
    "payload:",
    "http parameter",
    "url:",
    "cookie:",
    "header:",
    "body:",
)


def is_private_ip(value: Any) -> bool:
    if not value:
        return False
    try:
        return ipaddress.ip_address(str(value)).is_private
    except ValueError:
        return False


def extract_source_ip(raw_content: str, parsed: Dict[str, Any]) -> str | None:
    if parsed.get("source_ip"):
        return str(parsed["source_ip"])
    match = re.search(r"\bSource:\s*((?:[0-9]{1,3}\.){3}[0-9]{1,3})\b", raw_content, re.I)
    return match.group(1) if match else None


def looks_like_internal_debug_log(parsed: Dict[str, Any], raw_content: str) -> bool:
    """Detect benign internal SQL/debug logs before keyword-only triage can overfire."""
    text = raw_content.lower()
    source_ip = extract_source_ip(raw_content, parsed)

    has_internal_log_context = any(marker in text for marker in INTERNAL_LOG_MARKERS)
    has_internal_service = any(marker in text for marker in INTERNAL_SERVICE_MARKERS)
    explicitly_no_external = any(marker in text for marker in NO_EXTERNAL_MARKERS)
    has_private_source = is_private_ip(source_ip)
    has_sql_log_context = any(marker in text for marker in ("last query", "select ", " from "))
    has_attack_payload = any(marker in text for marker in ATTACK_PAYLOAD_MARKERS)
    has_external_request_field = any(
        marker in text
        for marker in ("http request", "request:", "uri:", "path:", "querystring:", "x-forwarded-for")
    )

    return (
        has_internal_log_context
        and has_sql_log_context
        and explicitly_no_external
        and (has_internal_service or has_private_source)
        and not has_attack_payload
        and not has_external_request_field
    )


def benign_internal_debug_result(parsed: Dict[str, Any], raw_content: str) -> Dict[str, Any]:
    source_ip = extract_source_ip(raw_content, parsed) or "unknown"
    return {
        "event_type": "Application Debug Log / Internal Database Query Log",
        "risk_level": "low",
        "confidence": 0.82,
        "priority": "P3",
        "classification": "benign",
        "disposition": "false_positive",
        "reasoning": (
            "The log is an internal application/database debug message from "
            f"{source_ip}. SQL keywords appear inside a recorded last-query/debug "
            "context, not in an external HTTP parameter or attack payload. Impact "
            "explicitly states no external request was detected."
        ),
    }
