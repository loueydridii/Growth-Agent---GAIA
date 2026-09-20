import React, { useEffect, useState } from 'react';
import { Check, X, ShieldAlert, ShieldOff } from 'lucide-react';

interface ApprovalAction {
  id: string;
  tool: string;
  rationale: string;
  risk: string;
  created_at: string;
}

const API_BASE = 'http://localhost:8001';

function timeAgo(iso: string) {
  const diff = Date.now() - new Date(iso).getTime();
  const h = Math.floor(diff / 3600000);
  if (h < 1) return `${Math.floor(diff / 60000)}m ago`;
  return `${h}h ago`;
}

const riskColor: Record<string, string> = {
  APPROVAL: 'text-[var(--color-saffron-spark)] border-[var(--color-saffron-spark)]/30',
  BLOCKED: 'text-red-400 border-red-500/30',
  AUTO: 'text-[var(--color-deep-verdant)] border-[var(--color-deep-verdant)]/30',
};

export function Approvals({ onCountChange }: { onCountChange: (n: number) => void }) {
  const [approvals, setApprovals] = useState<ApprovalAction[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchApprovals = async () => {
    try {
      const res = await fetch(`${API_BASE}/api/approvals`);
      const data = await res.json();
      setApprovals(data);
      onCountChange(data.length);
    } catch {
      // silent
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchApprovals(); }, []);

  const handleApprove = async (id: string) => {
    await fetch(`${API_BASE}/api/approve/${id}`, { method: 'POST' });
    const updated = approvals.filter(a => a.id !== id);
    setApprovals(updated);
    onCountChange(updated.length);
  };

  const handleBlock = async (id: string) => {
    await fetch(`${API_BASE}/api/block/${id}`, { method: 'POST' });
    const updated = approvals.filter(a => a.id !== id);
    setApprovals(updated);
    onCountChange(updated.length);
  };

  return (
    <div className="h-full flex flex-col">
      <div className="mb-8 flex-shrink-0">
        <h1 className="text-[48px] font-[400] tracking-[-1.68px] leading-[1.1] text-white">Policy<br />Holds.</h1>
        <p className="text-[14px] font-[200] text-[var(--color-ash-gray)] mt-3">
          Actions requiring your approval before the agent can proceed.
        </p>
      </div>

      {loading && <p className="text-[var(--color-ash-gray)] text-[14px] uppercase tracking-widest">Loading...</p>}

      {!loading && approvals.length === 0 && (
        <div className="flex-1 flex flex-col items-center justify-center gap-4">
          <ShieldOff size={48} className="text-[var(--color-ash-gray)]/30" />
          <p className="text-[18px] font-[200] text-[var(--color-silver-mist)]">No pending policy holds.</p>
          <p className="text-[13px] text-[var(--color-ash-gray)]">The agent is cleared to execute all queued AUTO actions.</p>
        </div>
      )}

      {!loading && approvals.length > 0 && (
        <div className="flex-1 overflow-y-auto space-y-12">
          {approvals.map((action) => (
            <div key={action.id} className="group">
              <div className="flex items-start justify-between mb-4">
                <div>
                  <div className="flex items-center gap-3 mb-2">
                    <ShieldAlert size={16} className="text-[var(--color-saffron-spark)]" />
                    <span className={`text-[11px] uppercase tracking-widest font-semibold px-2 py-0.5 rounded-full border ${riskColor[action.risk] || riskColor['APPROVAL']}`}>
                      {action.risk}
                    </span>
                    <span className="text-[11px] text-[var(--color-ash-gray)]">{timeAgo(action.created_at)}</span>
                  </div>
                  <h3 className="text-[27px] font-[400] tracking-[-0.4px] text-white">{action.tool}</h3>
                </div>
              </div>

              <p className="text-[16px] font-[200] text-[var(--color-silver-mist)] leading-relaxed mb-6">
                {action.rationale}
              </p>

              <div className="flex gap-8">
                <button
                  onClick={() => handleApprove(action.id)}
                  className="flex items-center gap-2 text-[13px] font-semibold uppercase tracking-[0.05em] text-[var(--color-deep-verdant)] hover:text-white transition-colors"
                >
                  <Check size={16} /> Approve & Execute
                </button>
                <button
                  onClick={() => handleBlock(action.id)}
                  className="flex items-center gap-2 text-[13px] font-semibold uppercase tracking-[0.05em] text-[var(--color-ash-gray)] hover:text-white transition-colors"
                >
                  <X size={16} /> Block Action
                </button>
              </div>

              <div className="mt-8 border-b border-white/5" />
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
