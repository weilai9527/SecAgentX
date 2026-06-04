import { useEffect, useState } from 'react';
import { Shield, Plus, Loader2 } from 'lucide-react';
import { useAppStore } from '../stores/appStore';
import AlertList from '../components/AlertList';
import AlertDetail from '../components/AlertDetail';
import AgentFlow from '../components/AgentFlow';
import EvidencePanel from '../components/EvidencePanel';
import AttackChain from '../components/AttackChain';
import ActionPanel from '../components/ActionPanel';
import ReportView from '../components/ReportView';
import { api } from '../services/api';

const TABS = [
  { key: 'agents', label: 'Agent Runs' },
  { key: 'evidence', label: 'Evidence' },
  { key: 'chain', label: 'Attack Chain' },
  { key: 'actions', label: 'Actions' },
  { key: 'report', label: 'Report' },
] as const;

type TabKey = typeof TABS[number]['key'];

export default function Workbench() {
  const [activeTab, setActiveTab] = useState<TabKey>('agents');
  const [showNewAlert, setShowNewAlert] = useState(false);
  const [newAlertText, setNewAlertText] = useState('');

  const {
    selectedIncident,
    loading,
    refreshAlerts,
    refreshIncidents,
    selectIncident,
    runAnalysis,
  } = useAppStore();

  useEffect(() => {
    refreshAlerts();
    refreshIncidents();
  }, [refreshAlerts, refreshIncidents]);

  const handleCreateAlert = async () => {
    if (!newAlertText.trim()) return;
    await useAppStore.getState().refreshAlerts();
    const alert = await api.alerts.create({
      title: newAlertText.split('\n')[0].slice(0, 80) || 'Manual Alert',
      raw_content: newAlertText,
      source_type: 'manual',
      severity: 'medium',
      status: 'pending',
    });
    await refreshAlerts();
    const incident = await api.incidents.create({ alert_id: alert.id, status: 'pending' });
    await refreshIncidents();
    await selectIncident(incident.id);
    setShowNewAlert(false);
    setNewAlertText('');
  };

  return (
    <div className="h-screen flex flex-col bg-slate-50">
      <header className="h-14 bg-white border-b border-slate-200 flex items-center justify-between px-4 shrink-0">
        <div className="flex items-center gap-2">
          <Shield className="w-6 h-6 text-primary-600" />
          <h1 className="font-bold text-lg text-slate-800">SecAgentX</h1>
          <span className="text-xs text-slate-400 ml-2">SecOps Workbench</span>
        </div>
        <button
          onClick={() => setShowNewAlert(true)}
          className="flex items-center gap-1 bg-primary-600 hover:bg-primary-700 text-white text-sm px-3 py-1.5 rounded-md transition"
        >
          <Plus className="w-4 h-4" />
          New Alert
        </button>
      </header>

      <div className="flex-1 flex overflow-hidden">
        <aside className="w-80 bg-white border-r border-slate-200 flex flex-col shrink-0">
          <AlertList />
        </aside>

        <main className="flex-1 flex flex-col min-w-0 bg-white">
          <AlertDetail onAnalyze={(id) => runAnalysis(id)} />
        </main>

        <aside className="w-[26rem] bg-white border-l border-slate-200 flex flex-col shrink-0">
          <div className="flex border-b border-slate-200 overflow-x-auto">
            {TABS.map((t) => (
              <button
                key={t.key}
                onClick={() => setActiveTab(t.key)}
                className={`px-3 py-2 text-xs font-medium whitespace-nowrap border-b-2 transition ${
                  activeTab === t.key
                    ? 'border-primary-600 text-primary-700'
                    : 'border-transparent text-slate-500 hover:text-slate-700'
                }`}
              >
                {t.label}
              </button>
            ))}
          </div>
          <div className="flex-1 overflow-auto p-3">
            {loading && (
              <div className="flex items-center justify-center py-8 text-slate-400">
                <Loader2 className="w-5 h-5 animate-spin mr-2" />
                Processing...
              </div>
            )}
            {!selectedIncident && !loading && (
              <div className="text-sm text-slate-400 text-center py-8">Select an incident from the left</div>
            )}
            {selectedIncident && (
              <>
                {activeTab === 'agents' && <AgentFlow />}
                {activeTab === 'evidence' && <EvidencePanel />}
                {activeTab === 'chain' && <AttackChain />}
                {activeTab === 'actions' && <ActionPanel />}
                {activeTab === 'report' && <ReportView />}
              </>
            )}
          </div>
        </aside>
      </div>

      {showNewAlert && (
        <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-xl w-[600px] max-w-[90vw] flex flex-col max-h-[80vh]">
            <div className="px-4 py-3 border-b border-slate-200 font-semibold">New Alert</div>
            <div className="p-4 flex-1">
              <textarea
                className="w-full h-48 border border-slate-300 rounded-md p-3 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500 resize-none"
                placeholder="Paste alert logs or description..."
                value={newAlertText}
                onChange={(e) => setNewAlertText(e.target.value)}
              />
            </div>
            <div className="px-4 py-3 border-t border-slate-200 flex justify-end gap-2">
              <button
                onClick={() => setShowNewAlert(false)}
                className="px-3 py-1.5 text-sm text-slate-600 hover:bg-slate-100 rounded-md"
              >
                Cancel
              </button>
              <button
                onClick={handleCreateAlert}
                className="px-3 py-1.5 text-sm bg-primary-600 text-white rounded-md hover:bg-primary-700"
              >
                Create
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
