"""Triage Agent: Risk assessment."""
import json
import re
from typing import Any, Dict

from app.agents.context import benign_internal_debug_result, looks_like_internal_debug_log
from app.core.llm_provider import get_llm_provider

SYSTEM_PROMPT = """You are a senior security triage analyst.
Assess the parsed alert and return only JSON:
{
  "event_type": "event type",
  "risk_level": "critical/high/medium/low/info",
  "confidence": 0.0,
  "priority": "P0/P1/P2/P3",
  "classification": "malicious/suspicious/benign",
  "disposition": "true_positive/false_positive/needs_review",
  "reasoning": "short evidence-based explanation"
}

False-positive control rules:
- Do not classify an event as SQL injection from SQL keywords alone.
- SQL in Application Log, Database Debug Message, Developer enabled debug mode,
  Last query, SQL audit log, SQL log, internal-service, backend-service,
  scheduler, cron, report-service, or "No external request detected" context is
  normally a benign internal/debug log.
- Only classify SQL Injection Attempt when SQL keywords appear in external HTTP
  URL/parameter/body/cookie/header input and there is injection structure such
  as OR 1=1, UNION SELECT, SLEEP, comments, sqlmap, abnormal SQL errors,
  abnormal returned rows, latency, authentication bypass, or data exfiltration
  impact.
- If evidence is internal service debug logging and no external request was
  detected, use risk_level low or info, classification benign, disposition
  false_positive.
"""


def triage(parsed: Dict[str, Any], raw_content: str) -> Dict[str, Any]:
    if looks_like_internal_debug_log(parsed, raw_content):
        return benign_internal_debug_result(parsed, raw_content)

    llm = get_llm_provider()
    prompt = (
        "Raw alert:\n"
        f"{raw_content}\n\n"
        "Parsed fields:\n"
        f"{json.dumps(parsed, ensure_ascii=False, indent=2)}\n\n"
        "Perform risk triage. Pay close attention to whether this is an external "
        "attack record or an internal/debug/application log."
    )
    try:
        raw = llm.generate(prompt, system=SYSTEM_PROMPT, max_tokens=1024)
        match = re.search(r"```json\s*(.*?)\s*```", raw, re.DOTALL)
        if match:
            raw = match.group(1)
        result = json.loads(raw)
        result["confidence"] = float(result.get("confidence", 0.8))
        return _guard_triage_result(result, parsed, raw_content)
    except Exception:
        return _fallback_triage(parsed, raw_content)


def _guard_triage_result(result: Dict[str, Any], parsed: Dict[str, Any], raw_content: str) -> Dict[str, Any]:
    if looks_like_internal_debug_log(parsed, raw_content):
        return benign_internal_debug_result(parsed, raw_content)
    return result


def _fallback_triage(parsed: Dict[str, Any], raw_content: str) -> Dict[str, Any]:
    if looks_like_internal_debug_log(parsed, raw_content):
        return benign_internal_debug_result(parsed, raw_content)

    text = raw_content.lower()

    has_sql_keyword = any(k in text for k in ("select ", " union ", " from ", " admin", "password"))
    has_sql_attack_context = any(
        k in text
        for k in (
            "sql injection",
            "payload:",
            "sqlmap",
            "' or '1'='1",
            " union select ",
            " sleep(",
            "--",
            "/*",
            "impact: 200 ok returned",
            "sql error",
        )
    )
    has_external_context = any(k in text for k in ("waf alert", "http", "uri:", "url:", "body:", "cookie:", "header:"))

    if has_sql_keyword and not (has_sql_attack_context and has_external_context):
        return {
            "event_type": "Application or Database Log Requiring Review",
            "risk_level": "low",
            "confidence": 0.75,
            "priority": "P3",
            "classification": "benign",
            "disposition": "needs_review",
            "reasoning": "SQL keywords were found, but there is no clear external request or injection payload evidence.",
        }

    if any(k in text for k in ("rce", "reverse shell", "log4j")):
        return {
            "event_type": "High Risk Exploit Attempt",
            "risk_level": "critical",
            "confidence": 0.95,
            "priority": "P0",
            "classification": "malicious",
            "disposition": "true_positive",
            "reasoning": "Remote execution or command-and-control evidence was found.",
        }
    if has_sql_attack_context and has_external_context:
        return {
            "event_type": "SQL Injection Attempt",
            "risk_level": "critical",
            "confidence": 0.9,
            "priority": "P0",
            "classification": "malicious",
            "disposition": "true_positive",
            "reasoning": "SQL injection payload evidence appears in an external request context.",
        }
    if any(k in text for k in ("brute force", "mimikatz", "lateral movement", "psexec", "wmi")):
        return {
            "event_type": "Intrusion or Lateral Movement",
            "risk_level": "high",
            "confidence": 0.88,
            "priority": "P1",
            "classification": "suspicious",
            "disposition": "needs_review",
            "reasoning": "Authentication attack or lateral movement indicators were found.",
        }
    if any(k in text for k in ("miner", "cryptominer")):
        return {
            "event_type": "Malware or Cryptomining",
            "risk_level": "medium",
            "confidence": 0.82,
            "priority": "P2",
            "classification": "suspicious",
            "disposition": "needs_review",
            "reasoning": "Cryptomining indicators were found.",
        }
    return {
        "event_type": "Unknown or Low Signal Event",
        "risk_level": "low",
        "confidence": 0.5,
        "priority": "P3",
        "classification": "benign",
        "disposition": "needs_review",
        "reasoning": "No clear attack evidence was found.",
    }
