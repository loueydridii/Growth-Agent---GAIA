import React, { useState, useEffect, useCallback } from 'react';
import { Sidebar } from './components/Sidebar';
import { TopBar } from './components/TopBar';
import { Chat } from './components/Chat';
import { Graph } from './components/Graph';
import { Workflows } from './components/Workflows';
import { Approvals } from './components/Approvals';
import { Settings } from './components/Settings';

type View = 'chat' | 'graph' | 'workflows' | 'approvals' | 'settings';

const API_BASE = 'http://localhost:8001';

function App() {
  const [activeView, setActiveView] = useState<View>('chat');
  const [isConnected, setIsConnected] = useState(false);
  const [pendingCount, setPendingCount] = useState(0);
  const [activeGoal, setActiveGoal] = useState<{ metric: string; target: string; timeframe: string; current: string } | null>(null);
  const [model, setModel] = useState('Growth Orchestrator (GAIA)');

  const pingBackend = useCallback(async () => {
    try {
      const res = await fetch(`${API_BASE}/api/status`, { signal: AbortSignal.timeout(2000) });
      if (res.ok) {
        const data = await res.json();
        setIsConnected(true);
        setActiveGoal(data.active_goal);
        setModel(data.model);
      } else {
        setIsConnected(false);
      }
    } catch {
      setIsConnected(false);
    }
  }, []);

  useEffect(() => {
    pingBackend();
    const interval = setInterval(pingBackend, 10000);
    return () => clearInterval(interval);
  }, [pingBackend]);

  const viewContent: Record<View, React.ReactNode> = {
    chat: <Chat />,
    graph: <Graph />,
    workflows: <Workflows />,
    approvals: <Approvals onCountChange={setPendingCount} />,
    settings: <Settings onSave={pingBackend} />,
  };

  return (
    <div className="min-h-screen bg-[var(--color-void)] text-[var(--color-bone-white)] font-['Inter'] overflow-hidden">
      {/* Ambient background particles */}
      <ParticleCanvas />

      {/* Sidebar */}
      <Sidebar
        activeView={activeView}
        onViewChange={setActiveView}
        isConnected={isConnected}
        pendingCount={pendingCount}
      />

      {/* TopBar */}
      <TopBar
        isConnected={isConnected}
        activeGoal={activeGoal}
        model={model}
        onConnectToggle={pingBackend}
      />

      {/* Main content area — offset for sidebar (72px) and topbar (56px) */}
      <main className="ml-[72px] pt-14 h-screen overflow-hidden">
        <div className="h-full p-10 overflow-y-auto">
          {viewContent[activeView]}
        </div>
      </main>
    </div>
  );
}

// Lightweight ambient particle canvas
function ParticleCanvas() {
  const canvasRef = React.useRef<HTMLCanvasElement>(null);

  React.useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;

    const colors = ['#8052ff', '#ffb829', '#15846e', '#c084fc', '#60a5fa'];
    const particles: { x: number; y: number; vx: number; vy: number; color: string; size: number; alpha: number }[] = [];

    for (let i = 0; i < 60; i++) {
      particles.push({
        x: Math.random() * canvas.width,
        y: Math.random() * canvas.height,
        vx: (Math.random() - 0.5) * 0.3,
        vy: (Math.random() - 0.5) * 0.3,
        color: colors[Math.floor(Math.random() * colors.length)],
        size: Math.random() * 4 + 2,
        alpha: Math.random() * 0.15 + 0.03,
      });
    }

    let animId: number;
    const draw = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      particles.forEach(p => {
        p.x += p.vx;
        p.y += p.vy;
        if (p.x < 0) p.x = canvas.width;
        if (p.x > canvas.width) p.x = 0;
        if (p.y < 0) p.y = canvas.height;
        if (p.y > canvas.height) p.y = 0;

        // Draw triangle particle
        ctx.save();
        ctx.globalAlpha = p.alpha;
        ctx.fillStyle = p.color;
        ctx.beginPath();
        ctx.moveTo(p.x, p.y - p.size);
        ctx.lineTo(p.x + p.size, p.y + p.size);
        ctx.lineTo(p.x - p.size, p.y + p.size);
        ctx.closePath();
        ctx.fill();
        ctx.restore();
      });
      animId = requestAnimationFrame(draw);
    };
    draw();

    const onResize = () => {
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;
    };
    window.addEventListener('resize', onResize);
    return () => { cancelAnimationFrame(animId); window.removeEventListener('resize', onResize); };
  }, []);

  return <canvas ref={canvasRef} className="fixed inset-0 pointer-events-none z-0" />;
}

export default App;
