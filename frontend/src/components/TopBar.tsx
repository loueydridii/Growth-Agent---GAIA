import React from 'react';
import { Target, Cpu } from 'lucide-react';

interface TopBarProps {
  isConnected: boolean;
  activeGoal: { metric: string; target: string; timeframe: string; current: string } | null;
  model: string;
  onConnectToggle: () => void;
}

export function TopBar({ isConnected, activeGoal, model, onConnectToggle }: TopBarProps) {
  return (
    <header className="fixed top-0 left-[72px] right-0 z-40 h-14 flex items-center justify-between px-8 border-b border-white/5 sidebar-glass">
      {/* Left: Active CEO Goal */}
      <div className="flex items-center gap-3">
        <Target size={14} className="text-[var(--color-saffron-spark)]" />
        {activeGoal ? (
          <span className="text-[12px] font-semibold uppercase tracking-[0.08em] text-[var(--color-ash-gray)]">
            Active Goal:&nbsp;
            <span className="text-white">Grow {activeGoal.metric} {activeGoal.target}</span>
            <span className="text-[var(--color-ash-gray)]"> by {activeGoal.timeframe}</span>
            <span className="ml-3 text-[var(--color-deep-verdant)]">↑ {activeGoal.current}</span>
          </span>
        ) : (
          <span className="text-[12px] font-semibold uppercase tracking-[0.08em] text-[var(--color-ash-gray)]">No active goal set</span>
        )}
      </div>

      {/* Right: Brain + Connect */}
      <div className="flex items-center gap-6">
        <div className="flex items-center gap-2">
          <Cpu size={13} className="text-[var(--color-electric-iris)]" />
          <span className="text-[11px] uppercase tracking-[0.08em] text-[var(--color-ash-gray)]">{model}</span>
        </div>
        <button
          onClick={onConnectToggle}
          className={`flex items-center gap-2 px-4 py-1.5 rounded-full text-[11px] font-semibold uppercase tracking-[0.08em] border transition-all ${
            isConnected
              ? 'border-[var(--color-deep-verdant)]/40 text-[var(--color-deep-verdant)] hover:bg-[var(--color-deep-verdant)]/10'
              : 'border-[var(--color-electric-iris)]/40 text-[var(--color-electric-iris)] hover:bg-[var(--color-electric-iris)]/10'
          }`}
        >
          <div className={`w-1.5 h-1.5 rounded-full ${isConnected ? 'bg-[var(--color-deep-verdant)]' : 'bg-[var(--color-electric-iris)] animate-pulse'}`} />
          {isConnected ? 'Connected' : 'Connect Agent'}
        </button>
      </div>
    </header>
  );
}
