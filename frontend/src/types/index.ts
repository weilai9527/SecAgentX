export interface Alert {
  id: number;
  title: string;
  raw_content?: string;
  source_type: string;
  severity: string;
  status: string;
  created_at: string;
  updated_at: string;
}

export interface Incident {
  id: number;
  alert_id: number;
  event_type?: string;
  risk_level?: string;
  confidence?: number;
  summary?: string;
  attack_stage?: string;
  status: string;
  created_at: string;
  updated_at: string;
  alert?: Alert;
  agent_runs?: AgentRun[];
  evidence_items?: EvidenceItem[];
  response_actions?: ResponseAction[];
  reports?: Report[];
}

export interface AgentRun {
  id: number;
  incident_id: number;
  agent_name: string;
  status: string;
  input_data?: any;
  output_data?: any;
  error_message?: string;
  started_at: string;
  finished_at?: string;
}

export interface EvidenceItem {
  id: number;
  incident_id: number;
  type: string;
  title: string;
  content?: string;
  source?: string;
  confidence?: number;
  created_at: string;
}

export interface ResponseAction {
  id: number;
  incident_id: number;
  action_type: string;
  description: string;
  risk: string;
  approval_required: boolean;
  status: string;
  approved_by?: string;
  created_at: string;
  updated_at: string;
}

export interface Report {
  id: number;
  incident_id: number;
  content: string;
  format: string;
  created_at: string;
}

export interface DemoCase {
  id: string;
  title: string;
  severity: string;
  raw_content: string;
}
