import { Check, X, Play, ShieldAlert, ShieldCheck } from 'lucide-react';
import { useAppStore } from '../stores/appStore';
import { api } from '../services/api';

const riskClass: Record<string, string> = {
  high: 'bg-red-50 border-red-200 text-red-700',
  medium: 'bg-orange-50 border-orange-200 text-orange-700',
  low: 'bg-green-50 border-green-200 text-green-700',
};

export default function ActionPanel() {
  const { selectedIncident, actions, refreshIncidentDetail } = useAppStore();

  if (!actions.length) {
    return <div className="text-xs text-slate-400 text-center py-4">暂无处置建议</div>;
  }

  const handleApprove = async (actionId: number) => {
    if (!selectedIncident) return;
    await api.actions.approve(selectedIncident.id, actionId, 'operator');
    await refreshIncidentDetail();
  };

  const handleReject = async (actionId: number) => {
    if (!selectedIncident) return;
    await api.actions.reject(selectedIncident.id, actionId, 'operator');
    await refreshIncidentDetail();
  };

  const handleSimulate = async (actionId: number) => {
    if (!selectedIncident) return;
    await api.actions.simulate(selectedIncident.id, actionId);
    await refreshIncidentDetail();
  };

  return (
    <div className="space-y-2">
      {actions.map((action) => (
        <div key={action.id} className={`border rounded-md p-2.5 ${riskClass[action.risk] || 'bg-slate-50 border-slate-200'}`}>
          <div className="flex items-start justify-between mb-1">
            <div className="flex items-center gap-1.5">
              {action.approval_required ? (
                <ShieldAlert className="w-3.5 h-3.5" />
              ) : (
                <ShieldCheck className="w-3.5 h-3.5" />
              )}
              <span className="text-xs font-semibold">{action.action_type}</span>
            </div>
            <span className="text-[10px] px-1.5 py-0.5 rounded bg-white/80 border border-black/5">
              {action.status}
            </span>
          </div>
          <div className="text-[11px] opacity-90 leading-relaxed">{action.description}</div>
          {action.risk === 'high' && (
            <div className="text-[10px] mt-1 opacity-75">⚠️ 高风险动作，需要人工审批</div>
          )}
          <div className="flex gap-1 mt-2">
            {action.status === 'pending' && (
              <>
                <button
                  onClick={() => handleApprove(action.id)}
                  className="flex items-center gap-1 text-[10px] bg-green-600 hover:bg-green-700 text-white px-2 py-1 rounded"
                >
                  <Check className="w-3 h-3" /> 审批
                </button>
                <button
                  onClick={() => handleReject(action.id)}
                  className="flex items-center gap-1 text-[10px] bg-slate-500 hover:bg-slate-600 text-white px-2 py-1 rounded"
                >
                  <X className="w-3 h-3" /> 驳回
                </button>
                <button
                  onClick={() => handleSimulate(action.id)}
                  className="flex items-center gap-1 text-[10px] bg-primary-600 hover:bg-primary-700 text-white px-2 py-1 rounded"
                >
                  <Play className="w-3 h-3" /> 模拟执行
                </button>
              </>
            )}
            {action.status !== 'pending' && (
              <span className="text-[10px] text-slate-500">已{action.status} · {action.approved_by || 'system'}</span>
            )}
          </div>
        </div>
      ))}
    </div>
  );
}
