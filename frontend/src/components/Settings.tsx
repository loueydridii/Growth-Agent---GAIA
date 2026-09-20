import React, { useState, useEffect } from 'react';
import { Save, Check } from 'lucide-react';

const API_BASE = 'http://localhost:8001';

interface StatusData {
  agent_name: string;
  full_name: string;
  model: string;
  skills: string[];
  active_goal: { metric: string; target: string; timeframe: string; current: string };
}

export function Settings({ onSave }: { onSave: () => void }) {
  const [status, setStatus] = useState<StatusData | null>(null);
  const [saved, setSaved] = useState(false);

  // Form state
  const [n8nUrl, setN8nUrl] = useState('http://localhost:5678');
  const [n8nKey, setN8nKey] = useState('');
  const [goalMetric, setGoalMetric] = useState('pipeline');
  const [goalTarget, setGoalTarget] = useState('+30%');
  const [goalTimeframe, setGoalTimeframe] = useState('Q4 2026');

  useEffect(() => {
    fetch(`${API_BASE}/api/status`).then(r => r.json()).then(d => {
      setStatus(d);
      setGoalMetric(d.active_goal.metric);
      setGoalTarget(d.active_goal.target);
      setGoalTimeframe(d.active_goal.timeframe);
    }).catch(() => {});

    // Load from localStorage
    const stored = localStorage.getItem('gaia_settings');
    if (stored) {
      const s = JSON.parse(stored);
      if (s.n8nUrl) setN8nUrl(s.n8nUrl);
      if (s.n8nKey) setN8nKey(s.n8nKey);
    }
  }, []);

  const handleSave = async () => {
    try {
      await fetch(`${API_BASE}/api/settings`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          n8n_url: n8nUrl,
          n8n_api_key: n8nKey,
          goal_metric: goalMetric,
          goal_target: goalTarget,
          goal_timeframe: goalTimeframe,
        }),
      });
      localStorage.setItem('gaia_settings', JSON.stringify({ n8nUrl, n8nKey }));
      setSaved(true);
      setTimeout(() => setSaved(false), 2000);
      onSave();
    } catch {
      // silent
    }
  };

  const inputClass = "w-full bg-transparent border-b border-white/10 text-white text-[15px] font-[200] py-3 focus:outline-none focus:border-[var(--color-electric-iris)] transition-colors placeholder:text-white/20";
  const labelClass = "text-[11px] uppercase tracking-widest text-[var(--color-ash-gray)] block mb-2";

  return (
    <div className="h-full flex flex-col max-w-xl">
      <div className="mb-12 flex-shrink-0">
        <h1 className="text-[48px] font-[400] tracking-[-1.68px] leading-[1.1] text-white">Settings.</h1>
        <p className="text-[14px] font-[200] text-[var(--color-ash-gray)] mt-3">Configure the GAIA brain, active goal, and integrations.</p>
      </div>

      {/* Agent Info */}
      {status && (
        <section className="mb-12 pb-12 border-b border-white/5">
          <p className="text-[11px] uppercase tracking-widest text-[var(--color-ash-gray)] mb-6">Brain</p>
          <p className="text-[24px] font-[400] text-white mb-1">{status.full_name}</p>
          <p className="text-[14px] font-[200] text-[var(--color-silver-mist)]">{status.model}</p>
          <div className="flex flex-wrap gap-2 mt-4">
            {status.skills.map(s => (
              <span key={s} className="text-[10px] uppercase tracking-wider px-2 py-0.5 rounded-full border border-white/10 text-[var(--color-ash-gray)]">{s}</span>
            ))}
          </div>
        </section>
      )}

      {/* CEO Goal */}
      <section className="mb-12 pb-12 border-b border-white/5">
        <p className="text-[11px] uppercase tracking-widest text-[var(--color-ash-gray)] mb-6">CEO Goal</p>
        <div className="space-y-6">
          <div>
            <label className={labelClass}>Metric</label>
            <input className={inputClass} value={goalMetric} onChange={e => setGoalMetric(e.target.value)} placeholder="e.g. pipeline, revenue, leads" />
          </div>
          <div>
            <label className={labelClass}>Target</label>
            <input className={inputClass} value={goalTarget} onChange={e => setGoalTarget(e.target.value)} placeholder="e.g. +30%" />
          </div>
          <div>
            <label className={labelClass}>Timeframe</label>
            <input className={inputClass} value={goalTimeframe} onChange={e => setGoalTimeframe(e.target.value)} placeholder="e.g. Q4 2026" />
          </div>
        </div>
      </section>

      {/* n8n Integration */}
      <section className="mb-12 pb-12 border-b border-white/5">
        <p className="text-[11px] uppercase tracking-widest text-[var(--color-ash-gray)] mb-6">n8n Integration</p>
        <div className="space-y-6">
          <div>
            <label className={labelClass}>n8n URL</label>
            <input className={inputClass} value={n8nUrl} onChange={e => setN8nUrl(e.target.value)} placeholder="http://localhost:5678" />
          </div>
          <div>
            <label className={labelClass}>API Key</label>
            <input className={inputClass} type="password" value={n8nKey} onChange={e => setN8nKey(e.target.value)} placeholder="Paste your n8n API key here" />
            <p className="text-[11px] text-[var(--color-ash-gray)] mt-2">
              Generate in n8n → Settings → API. Required for live workflow data.
            </p>
          </div>
        </div>
      </section>

      {/* Save */}
      <div>
        <button onClick={handleSave} className="btn-primary flex items-center gap-2">
          {saved ? <Check size={16} /> : <Save size={16} />}
          {saved ? 'Saved' : 'Save Settings'}
        </button>
      </div>
    </div>
  );
}
