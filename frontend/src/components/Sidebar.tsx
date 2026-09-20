import React from 'react';
import { BrainCircuit, MessageSquare, GitBranch, Zap, Settings, ShieldAlert } from 'lucide-react';

type View = 'chat' | 'graph' | 'workflows' | 'approvals' | 'settings';

interface SidebarProps {
  activeView: View;
  onViewChange: (view: View) => void;
  isConnected: boolean;
  pendingCount: number;
}

const navItems: { id: View; label: string; icon: React.ReactNode }[] = [
  { id: 'chat', label: 'Terminal', icon: <MessageSquare size={20} /> },
  { id: 'graph', label: 'Context Graph', icon: <GitBranch size={20} /> },
  { id: 'workflows', label: 'Workflows', icon: <Zap size={20} /> },
  { id: 'approvals', label: 'Policy Holds', icon: <ShieldAlert size={20} /> },
  { id: 'settings', label: 'Settings', icon: <Settings size={20} /> },
];

export function Sidebar({ activeView, onViewChange, isConnected, pendingCount }: SidebarProps) {
  return (
    <aside className="sidebar-glass w-[72px] hover:w-[220px] transition-all duration-300 ease-out group flex flex-col justify-between h-screen fixed left-0 top-0 z-50 overflow-hidden border-r border-white/5">
      {/* Logo */}
      <div>
        <div className="flex items-center gap-3 px-5 py-6 border-b border-white/5">
          <div className="flex-shrink-0 text-[var(--color-electric-iris)]">
            <BrainCircuit size={24} />
          </div>
          <span className="text-[13px] font-semibold tracking-[0.1em] uppercase whitespace-nowrap opacity-0 group-hover:opacity-100 transition-opacity duration-200 delay-100 text-white">
            GAIA
          </span>
        </div>

        {/* Connection dot */}
        <div className="flex items-center gap-3 px-5 py-4">
          <div className={`flex-shrink-0 w-2 h-2 rounded-full transition-colors ${isConnected ? 'bg-[var(--color-deep-verdant)] shadow-[0_0_6px_var(--color-deep-verdant)]' : 'bg-red-500'}`} />
          <span className="text-[11px] text-[var(--color-ash-gray)] uppercase tracking-widest whitespace-nowrap opacity-0 group-hover:opacity-100 transition-opacity duration-200 delay-100">
            {isConnected ? 'Online' : 'Offline'}
          </span>
        </div>

        {/* Nav items */}
        <nav className="mt-4 flex flex-col gap-1 px-3">
          {navItems.map((item) => (
            <button
              key={item.id}
              onClick={() => onViewChange(item.id)}
              className={`flex items-center gap-3 px-3 py-3 rounded-2xl transition-all duration-150 relative group/item text-left w-full
                ${activeView === item.id
                  ? 'bg-[var(--color-electric-iris)]/15 text-white'
                  : 'text-[var(--color-ash-gray)] hover:text-white hover:bg-white/5'
                }`}
            >
              <div className="flex-shrink-0">{item.icon}</div>
              <span className="text-[13px] font-semibold tracking-[0.02em] whitespace-nowrap opacity-0 group-hover:opacity-100 transition-opacity duration-200 delay-100">
                {item.label}
              </span>
              {item.id === 'approvals' && pendingCount > 0 && (
                <span className="ml-auto flex-shrink-0 w-5 h-5 rounded-full bg-[var(--color-saffron-spark)] text-black text-[10px] font-bold flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity duration-200 delay-100">
                  {pendingCount}
                </span>
              )}
              {activeView === item.id && (
                <div className="absolute left-0 top-1/2 -translate-y-1/2 w-0.5 h-4 bg-[var(--color-electric-iris)] rounded-full" />
              )}
            </button>
          ))}
        </nav>
      </div>
    </aside>
  );
}
