"""Pydantic schemas."""
from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict


# Alert schemas
class AlertBase(BaseModel):
    title: str
    raw_content: Optional[str] = None
    source_type: str = "manual"
    severity: str = "medium"
    status: str = "pending"


class AlertCreate(AlertBase):
    pass


class AlertUpdate(BaseModel):
    title: Optional[str] = None
    severity: Optional[str] = None
    status: Optional[str] = None
    raw_content: Optional[str] = None


class AlertOut(AlertBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime


# Incident schemas
class IncidentBase(BaseModel):
    event_type: Optional[str] = None
    risk_level: Optional[str] = None
    confidence: Optional[float] = 0.0
    summary: Optional[str] = None
    attack_stage: Optional[str] = None
    status: str = "pending"


class IncidentCreate(IncidentBase):
    alert_id: int


class IncidentOut(IncidentBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    alert_id: int
    created_at: datetime
    updated_at: datetime


class IncidentDetail(IncidentOut):
    alert: Optional[AlertOut] = None
    agent_runs: List["AgentRunOut"] = []
    evidence_items: List["EvidenceItemOut"] = []
    response_actions: List["ResponseActionOut"] = []
    reports: List["ReportOut"] = []


# AgentRun schemas
class AgentRunBase(BaseModel):
    agent_name: str
    status: str = "running"
    input_data: Optional[Dict[str, Any]] = None
    output_data: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None


class AgentRunOut(AgentRunBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    incident_id: int
    started_at: datetime
    finished_at: Optional[datetime] = None


# EvidenceItem schemas
class EvidenceItemBase(BaseModel):
    type: str
    title: str
    content: Optional[str] = None
    source: Optional[str] = None
    confidence: Optional[float] = 0.0


class EvidenceItemOut(EvidenceItemBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    incident_id: int
    created_at: datetime


# ResponseAction schemas
class ResponseActionBase(BaseModel):
    action_type: str
    description: str
    risk: str = "medium"
    approval_required: bool = False
    status: str = "pending"


class ResponseActionOut(ResponseActionBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    incident_id: int
    approved_by: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class ActionApproval(BaseModel):
    approved_by: str


# Report schemas
class ReportBase(BaseModel):
    content: str
    format: str = "markdown"


class ReportOut(ReportBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    incident_id: int
    created_at: datetime


# Pipeline schemas
class AnalyzeRequest(BaseModel):
    use_demo_case: Optional[str] = None


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    messages: List[ChatMessage]


# Rebuild forward refs
IncidentDetail.model_rebuild()
