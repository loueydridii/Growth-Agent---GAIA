import React, { useEffect, useState, useRef } from 'react';
import { RefreshCw } from 'lucide-react';

interface MemoryNode {
  id: string;
  source: string;
  target: string;
  relation: string;
}

interface GraphNode {
  id: string;
  label: string;
  x: number;
  y: number;
  color: string;
}

interface GraphEdge {
  source: string;
  target: string;
  label: string;
}

import { API_BASE } from '../config';

const NODE_COLORS = [
  'var(--color-electric-iris)',
  'var(--color-saffron-spark)',
  'var(--color-deep-verdant)',
  '#c084fc',
  '#60a5fa',
];

function buildGraph(nodes: MemoryNode[]): { graphNodes: GraphNode[]; edges: GraphEdge[] } {
  const nodeMap = new Map<string, GraphNode>();
  const edges: GraphEdge[] = [];
  let colorIdx = 0;

  const cx = 400, cy = 280;
  const allLabels = [...new Set(nodes.flatMap(n => [n.source, n.target]))];

  allLabels.forEach((label, i) => {
    const angle = (i / allLabels.length) * 2 * Math.PI;
    const r = 180;
    nodeMap.set(label, {
      id: label,
      label,
      x: cx + r * Math.cos(angle),
      y: cy + r * Math.sin(angle),
      color: NODE_COLORS[colorIdx++ % NODE_COLORS.length],
    });
  });

  nodes.forEach(n => {
    edges.push({ source: n.source, target: n.target, label: n.relation });
  });

  return { graphNodes: Array.from(nodeMap.values()), edges };
}

export function Graph() {
  const [rawNodes, setRawNodes] = useState<MemoryNode[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);

  const fetchMemory = async () => {
    setLoading(true);
    setError(false);
    try {
      const res = await fetch(`${API_BASE}/api/memory`);
      const data = await res.json();
      setRawNodes(data);
    } catch {
      setError(true);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchMemory(); }, []);

  const { graphNodes, edges } = buildGraph(rawNodes);

  return (
    <div className="h-full flex flex-col">
      <div className="mb-8 flex items-end justify-between flex-shrink-0">
        <div>
          <h1 className="text-[48px] font-[400] tracking-[-1.68px] leading-[1.1] text-white">Context<br />Graph.</h1>
          <p className="text-[14px] font-[200] text-[var(--color-ash-gray)] mt-3">Live temporal knowledge graph from Graphiti memory.</p>
        </div>
        <button onClick={fetchMemory} className="flex items-center gap-2 text-[12px] uppercase tracking-widest text-[var(--color-ash-gray)] hover:text-white transition-colors">
          <RefreshCw size={14} />
          Refresh
        </button>
      </div>

      {loading && <div className="flex-1 flex items-center justify-center"><p className="text-[var(--color-ash-gray)] text-[14px] uppercase tracking-widest">Loading memory nodes...</p></div>}
      {error && <div className="flex-1 flex items-center justify-center"><p className="text-red-400 text-[14px] uppercase tracking-widest">Failed to reach GAIA backend.</p></div>}

      {!loading && !error && (
        <div className="flex-1 flex gap-8">
          {/* SVG Graph */}
          <div className="flex-1 glass-panel rounded-3xl border border-white/5 overflow-hidden relative">
            <svg width="100%" height="100%" viewBox="0 0 800 560" className="absolute inset-0">
              <defs>
                <marker id="arrow" markerWidth="6" markerHeight="6" refX="5" refY="3" orient="auto">
                  <path d="M0,0 L0,6 L6,3 z" fill="rgba(128,82,255,0.5)" />
                </marker>
              </defs>

              {/* Edges */}
              {edges.map((edge, i) => {
                const from = graphNodes.find(n => n.id === edge.source);
                const to = graphNodes.find(n => n.id === edge.target);
                if (!from || !to) return null;
                const mx = (from.x + to.x) / 2;
                const my = (from.y + to.y) / 2;
                return (
                  <g key={i}>
                    <line
                      x1={from.x} y1={from.y} x2={to.x} y2={to.y}
                      stroke="rgba(128,82,255,0.25)" strokeWidth={1.5}
                      markerEnd="url(#arrow)"
                    />
                    <text x={mx} y={my - 6} fill="rgba(255,184,41,0.7)" fontSize="9" textAnchor="middle" fontFamily="Inter">
                      {edge.label}
                    </text>
                  </g>
                );
              })}

              {/* Nodes */}
              {graphNodes.map((node, i) => (
                <g key={i}>
                  <circle cx={node.x} cy={node.y} r={36} fill={`${node.color}15`} stroke={node.color} strokeWidth={1} />
                  <text
                    x={node.x} y={node.y - 4} fill="white" fontSize="9" textAnchor="middle" fontFamily="Inter"
                    fontWeight="400"
                  >
                    {node.label.split(': ')[0]}
                  </text>
                  <text
                    x={node.x} y={node.y + 9} fill={node.color} fontSize="9" textAnchor="middle" fontFamily="Inter"
                  >
                    {node.label.split(': ')[1] || ''}
                  </text>
                </g>
              ))}
            </svg>
          </div>

          {/* Node list */}
          <div className="w-64 flex-shrink-0 space-y-4 overflow-y-auto">
            <p className="text-[11px] uppercase tracking-widest text-[var(--color-ash-gray)] mb-4">Raw Edges</p>
            {rawNodes.map((n, i) => (
              <div key={i} className="text-[13px] font-[200] leading-relaxed text-[var(--color-silver-mist)] border-b border-white/5 pb-4">
                <span className="text-white text-[12px]">{n.source}</span>
                <span className="text-[var(--color-electric-iris)] mx-2 text-[11px]">â†’ [{n.relation}] â†’</span>
                <span className="text-white text-[12px]">{n.target}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

