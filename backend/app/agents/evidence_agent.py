"""Evidence Agent: Gather simulated evidence for MVP."""
import random
from datetime import datetime, timedelta
from typing import Any, Dict, List

from app.agents.context import looks_like_internal_debug_log


def gather_evidence(parsed: Dict[str, Any], raw_content: str) -> List[Dict[str, Any]]:
    if looks_like_internal_debug_log(parsed, raw_content):
        return [{
            "type": "log",
            "title": "Internal application debug log",
            "content": (
                "The record is an application/database debug message. SQL text appears "
                "as a logged last query, User-Agent/context indicates internal service "
                "activity, and Impact states no external request was detected."
            ),
            "source": "application_log",
            "confidence": 0.9,
        }]

    evidence: List[Dict[str, Any]] = []
    source_ip = parsed.get("source_ip") or "unknown"
    target_ip = parsed.get("target_ip") or "unknown"
    username = parsed.get("username") or "unknown"

    # Log evidence
    evidence.append({
        "type": "log",
        "title": "关联防火墙日志",
        "content": f"{datetime.utcnow().strftime('%Y-%m-%d %H:%M')} fw-01 DROP tcp {source_ip}:54321 -> {target_ip}:22 count=512",
        "source": "firewall",
        "confidence": 0.92,
    })

    # Asset info
    evidence.append({
        "type": "asset",
        "title": f"资产信息: {target_ip}",
        "content": f"IP: {target_ip}\nOS: CentOS 7.9\nRole: 生产服务器\nOwner: ops-team\nPatch: 2026-04",
        "source": "cmdb",
        "confidence": 0.95,
    })

    # IOC match
    ioc_confidence = random.uniform(0.7, 0.98)
    evidence.append({
        "type": "ioc",
        "title": f"IOC 匹配: {source_ip}",
        "content": f"IP {source_ip} 命中威胁情报库: Mirai C2 历史关联 / 恶意扫描源",
        "source": "threat_intel",
        "confidence": round(ioc_confidence, 2),
    })

    # Vuln info (only for certain keywords)
    if any(k in raw_content.lower() for k in ("log4j", "rce", "cve")):
        evidence.append({
            "type": "vuln",
            "title": "漏洞关联: CVE-2021-44228",
            "content": "Log4j 2.x JNDI 远程代码执行漏洞，CVSS 10.0，已出 POC，建议紧急修复。",
            "source": "vuln_db",
            "confidence": 0.96,
        })

    # User evidence
    if username and username != "unknown":
        evidence.append({
            "type": "log",
            "title": f"账号行为: {username}",
            "content": f"账号 {username} 在过去 24h 内从无关联主机登录，触发异常登录策略。",
            "source": "iam",
            "confidence": 0.85,
        })

    return evidence
