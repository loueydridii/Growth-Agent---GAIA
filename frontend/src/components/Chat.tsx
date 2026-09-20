import React, { useState, useEffect, useRef } from 'react';
import { Send, Loader2, BrainCircuit } from 'lucide-react';

interface ChatMessage {
  role: 'user' | 'agent';
  content: string;
  thought_process?: string[];
  category?: string;
  timestamp: string;
}

const API_BASE = 'http://localhost:8001';

function formatTime(iso: string) {
  return new Date(iso).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
}

export function Chat() {
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      role: 'agent',
      content: 'GAIA is online. I am operating in CEO Mode — ready to receive growth objectives. Try: "Grow pipeline by 30% in Q4" or "Scan for competitor opportunities".',
      timestamp: new Date().toISOString(),
    }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [expandedThoughts, setExpandedThoughts] = useState<Set<number>>(new Set());
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

  const toggleThought = (idx: number) => {
    setExpandedThoughts(prev => {
      const next = new Set(prev);
      next.has(idx) ? next.delete(idx) : next.add(idx);
      return next;
    });
  };

  const handleSend = async () => {
    if (!input.trim() || loading) return;

    const userMsg: ChatMessage = { role: 'user', content: input, timestamp: new Date().toISOString() };
    setMessages(prev => [...prev, userMsg]);
    const currentInput = input;
    setInput('');
    setLoading(true);

    try {
      const res = await fetch(`${API_BASE}/api/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ command: currentInput }),
      });

      if (!res.ok) throw new Error('API error');
      const data = await res.json();

      setMessages(prev => [...prev, {
        role: 'agent',
        content: data.response,
        thought_process: data.thought_process,
        category: data.category,
        timestamp: new Date().toISOString(),
      }]);
    } catch {
      setMessages(prev => [...prev, {
        role: 'agent',
        content: 'Connection error. Make sure the GAIA backend is running on port 8000.',
        timestamp: new Date().toISOString(),
      }]);
    } finally {
      setLoading(false);
    }
  };

  const categoryColors: Record<string, string> = {
    CEO_GOAL: 'text-[var(--color-electric-iris)]',
    OPPORTUNITY_SCAN: 'text-[var(--color-saffron-spark)]',
    EXPERIMENT: 'text-[var(--color-deep-verdant)]',
    GENERAL: 'text-[var(--color-ash-gray)]',
  };

  return (
    <div className="flex flex-col h-full">
      {/* Hero heading */}
      <div className="mb-8 flex-shrink-0">
        <h1 className="text-[48px] font-[400] tracking-[-1.68px] leading-[1.1] text-white">Growth<br />Terminal.</h1>
        <p className="text-[14px] font-[200] text-[var(--color-ash-gray)] mt-3">Issue CEO directives. The agent thinks, plans, and executes.</p>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto space-y-8 pr-2 chat-scroll mb-6">
        {messages.map((msg, i) => (
          <div key={i} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
            {msg.role === 'agent' && (
              <div className="flex-shrink-0 w-8 h-8 rounded-full bg-[var(--color-electric-iris)]/15 border border-[var(--color-electric-iris)]/20 flex items-center justify-center mr-3 mt-1">
                <BrainCircuit size={14} className="text-[var(--color-electric-iris)]" />
              </div>
            )}
            <div className={`max-w-[75%] ${msg.role === 'user' ? 'text-right' : 'text-left'}`}>
              <div className="flex items-center gap-3 mb-2">
                <span className="text-[11px] uppercase tracking-widest text-[var(--color-ash-gray)]">
                  {msg.role === 'user' ? 'CEO' : 'GAIA'}
                </span>
                {msg.category && (
                  <span className={`text-[10px] uppercase tracking-widest font-semibold ${categoryColors[msg.category] || 'text-[var(--color-ash-gray)]'}`}>
                    [{msg.category}]
                  </span>
                )}
                <span className="text-[10px] text-[var(--color-ash-gray)]/50">{formatTime(msg.timestamp)}</span>
              </div>

              <p className={`text-[16px] font-[200] leading-relaxed ${msg.role === 'user' ? 'text-white' : 'text-[var(--color-silver-mist)]'}`}>
                {msg.content}
              </p>

              {/* Thought process toggle */}
              {msg.thought_process && msg.thought_process.length > 0 && (
                <div className="mt-3">
                  <button
                    onClick={() => toggleThought(i)}
                    className="text-[11px] uppercase tracking-widest text-[var(--color-electric-iris)]/60 hover:text-[var(--color-electric-iris)] transition-colors"
                  >
                    {expandedThoughts.has(i) ? '▴ Hide reasoning' : '▾ Show reasoning'}
                  </button>
                  {expandedThoughts.has(i) && (
                    <div className="mt-3 space-y-2 pl-3 border-l border-[var(--color-electric-iris)]/20">
                      {msg.thought_process.map((step, si) => (
                        <p key={si} className="text-[12px] font-[300] text-[var(--color-ash-gray)] font-mono">{step}</p>
                      ))}
                    </div>
                  )}
                </div>
              )}
            </div>
            {msg.role === 'user' && (
              <div className="flex-shrink-0 w-8 h-8 rounded-full bg-white/5 border border-white/10 flex items-center justify-center ml-3 mt-1">
                <span className="text-[10px] font-bold text-[var(--color-ash-gray)]">CEO</span>
              </div>
            )}
          </div>
        ))}

        {/* Loading indicator */}
        {loading && (
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-full bg-[var(--color-electric-iris)]/15 border border-[var(--color-electric-iris)]/20 flex items-center justify-center">
              <BrainCircuit size={14} className="text-[var(--color-electric-iris)]" />
            </div>
            <div className="flex items-center gap-2 text-[var(--color-ash-gray)]">
              <Loader2 size={14} className="animate-spin" />
              <span className="text-[12px] uppercase tracking-widest">GAIA is thinking...</span>
            </div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      {/* Glass Input */}
      <div className="flex-shrink-0">
        <div className="glass-input-panel rounded-3xl border border-white/10 flex items-center px-6 py-2 gap-4 shadow-2xl">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleSend()}
            placeholder="Deploy a growth objective..."
            disabled={loading}
            className="flex-1 bg-transparent text-[16px] font-[200] text-white py-3 focus:outline-none placeholder:text-[var(--color-ash-gray)]/50 disabled:opacity-50"
          />
          <button
            onClick={handleSend}
            disabled={loading || !input.trim()}
            className="flex-shrink-0 w-10 h-10 rounded-full bg-[var(--color-electric-iris)] text-white flex items-center justify-center hover:opacity-90 transition-opacity disabled:opacity-30 disabled:cursor-not-allowed"
          >
            {loading ? <Loader2 size={18} className="animate-spin" /> : <Send size={18} />}
          </button>
        </div>
        <p className="text-[11px] text-[var(--color-ash-gray)]/40 mt-3 ml-6">
          Try: "Grow pipeline by 30%" · "Scan competitor landscape" · "Run an experiment on landing page"
        </p>
      </div>
    </div>
  );
}
