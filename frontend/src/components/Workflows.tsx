import React, { useEffect, useState } from 'react';
import { RefreshCw, Play, ExternalLink, Zap, ZapOff } from 'lucide-react';

interface Workflow {
  id: string;
  name: string;
  active: boolean;
  updatedAt: string;
  tags: string[];
}

import { API_BASE } from '../config';

function timeAgo(iso: string) {
  const diff = Date.now() - new Date(iso).getTime();
  const h = Math.floor(diff / 3600000);
  if (h < 1) return `${Math.floor(diff / 60000)}m ago`;
  if (h < 24) return `${h}h ago`;
  return `${Math.floor(h / 24)}d ago`;
}

export function Workflows() {
  const [workflows, setWorkflows] = useState<Workflow[]>([]);
  const [source, setSource] = useState<'live' | 'mock'>('mock');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);

  const fetchWorkflows = async () => {
    setLoading(true);
    setError(false);
    try {
      const res = await fetch(`${API_BASE}/api/workflows`);
      const data = await res.json();
      setWorkflows(data.workflows);
      setSource(data.source);
    } catch {
      setError(true);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchWorkflows(); }, []);

  return (
    <div className="h-full flex flex-col">
      <div className="mb-8 flex items-end justify-between flex-shrink-0">
        <div>
          <h1 className="text-[48px] font-[400] tracking-[-1.68px] leading-[1.1] text-white">Automation<br />Workflows.</h1>
          <p className="text-[14px] font-[200] text-[var(--color-ash-gray)] mt-3">
            Live n8n workflow status.&nbsp;
            {source === 'mock' && (
              <span className="text-[var(--color-saffron-spark)]">
                Showing mock data â€” add n8n API key in Settings to connect live.
              </span>
            )}
            {source === 'live' && <span className="text-[var(--color-deep-verdant)]">Connected to n8n.</span>}
          </p>
        </div>
        <div className="flex items-center gap-4">
          <a
            href="http://localhost:5678"
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-2 text-[12px] uppercase tracking-widest text-[var(--color-ash-gray)] hover:text-white transition-colors"
          >
            <ExternalLink size={14} />
            Open n8n
          </a>
          <button onClick={fetchWorkflows} className="flex items-center gap-2 text-[12px] uppercase tracking-widest text-[var(--color-ash-gray)] hover:text-white transition-colors">
            <RefreshCw size={14} />
            Refresh
          </button>
        </div>
      </div>

      {loading && <p className="text-[var(--color-ash-gray)] text-[14px] uppercase tracking-widest">Loading workflows...</p>}
      {error && <p className="text-red-400 text-[14px] uppercase tracking-widest">Failed to reach GAIA backend.</p>}

      {!loading && !error && (
        <div className="flex-1 overflow-y-auto space-y-1">
          {/* Header row */}
          <div className="grid grid-cols-12 text-[11px] uppercase tracking-widest text-[var(--color-ash-gray)] px-6 py-3 border-b border-white/5 mb-2">
            <span className="col-span-1">Status</span>
            <span className="col-span-5">Workflow</span>
            <span className="col-span-3">Tags</span>
            <span className="col-span-2">Last Run</span>
            <span className="col-span-1 text-right">Action</span>
          </div>

          {workflows.map((wf) => (
            <div
              key={wf.id}
              className="grid grid-cols-12 items-center px-6 py-4 rounded-2xl hover:bg-white/3 transition-colors group"
            >
              <div className="col-span-1">
                {wf.active ? (
                  <Zap size={14} className="text-[var(--color-deep-verdant)]" />
                ) : (
                  <ZapOff size={14} className="text-[var(--color-ash-gray)]" />
                )}
              </div>
              <div className="col-span-5">
                <p className="text-[15px] font-[400] text-white">{wf.name}</p>
                <p className="text-[11px] text-[var(--color-ash-gray)] mt-0.5">{wf.id}</p>
              </div>
              <div className="col-span-3 flex gap-2 flex-wrap">
                {wf.tags.map(tag => (
                  <span
                    key={tag}
                    className="text-[10px] uppercase tracking-wider px-2 py-0.5 rounded-full border border-white/10 text-[var(--color-ash-gray)]"
                  >
                    {tag}
                  </span>
                ))}
              </div>
              <div className="col-span-2 text-[12px] text-[var(--color-ash-gray)]">{timeAgo(wf.updatedAt)}</div>
              <div className="col-span-1 flex justify-end">
                <button className="opacity-0 group-hover:opacity-100 transition-opacity flex items-center gap-1 text-[11px] uppercase tracking-wider text-[var(--color-electric-iris)] hover:text-white">
                  <Play size={12} /> Run
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

