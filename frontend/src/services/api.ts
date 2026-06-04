import type { Alert, Incident, AgentRun, EvidenceItem, ResponseAction, Report } from '../types';

const API_BASE = '/api';

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || err.error || `HTTP ${res.status}`);
  }
  return res.json() as Promise<T>;
}

export const api = {
  health: () => request<{ ok: boolean }>('/health'),

  alerts: {
    list: () => request<Alert[]>('/alerts'),
    create: (data: Partial<Alert>) => request<Alert>('/alerts', { method: 'POST', body: JSON.stringify(data) }),
    delete: (id: number) => request<any>(`/alerts/${id}`, { method: 'DELETE' }),
    fromCase: (caseId: string) => request<Alert>(`/alerts/from-case/${caseId}`, { method: 'POST' }),
  },

  incidents: {
    list: () => request<Incident[]>('/incidents'),
    get: (id: number) => request<Incident>(`/incidents/${id}`),
    create: (data: Partial<Incident>) => request<Incident>('/incidents', { method: 'POST', body: JSON.stringify(data) }),
    analyze: (id: number) => request<any>(`/incidents/${id}/analyze`, { method: 'POST' }),
  },

  agents: {
    list: (incidentId: number) => request<AgentRun[]>(`/incidents/${incidentId}/agents`),
  },

  evidence: {
    list: (incidentId: number) => request<EvidenceItem[]>(`/incidents/${incidentId}/evidence`),
  },

  actions: {
    list: (incidentId: number) => request<ResponseAction[]>(`/incidents/${incidentId}/actions`),
    approve: (incidentId: number, actionId: number, approvedBy: string) =>
      request<any>(`/incidents/${incidentId}/actions/${actionId}/approve`, { method: 'POST', body: JSON.stringify({ approved_by: approvedBy }) }),
    reject: (incidentId: number, actionId: number, approvedBy: string) =>
      request<any>(`/incidents/${incidentId}/actions/${actionId}/reject`, { method: 'POST', body: JSON.stringify({ approved_by: approvedBy }) }),
    simulate: (incidentId: number, actionId: number) =>
      request<any>(`/incidents/${incidentId}/actions/${actionId}/simulate`, { method: 'POST' }),
  },

  reports: {
    get: (incidentId: number) => request<Report>(`/incidents/${incidentId}/report`),
    generate: (incidentId: number) => request<Report>(`/incidents/${incidentId}/report`, { method: 'POST' }),
  },
};

