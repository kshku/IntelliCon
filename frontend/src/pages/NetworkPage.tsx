import React, { useState } from 'react';
import {
  Share2,
  GitBranch,
  Search,
  Users2,
  Shield,
  Phone,
  ArrowRight,
  Activity
} from 'lucide-react';

export const NetworkPage: React.FC = () => {
  const [suspectA, setSuspectA] = useState('Raju (Gangleader)');
  const [suspectB, setSuspectB] = useState('Kumar (Accomplice)');

  // Mock nodes for visual SVG network diagram
  const nodes = [
    { id: '1', label: 'Raju', role: 'Gang Leader', x: 250, y: 130, color: 'fill-red-500' },
    { id: '2', label: 'Kumar', role: 'Main Accomplice', x: 130, y: 250, color: 'fill-orange-500' },
    { id: '3', label: 'Suresh', role: 'Driver / Transport', x: 370, y: 250, color: 'fill-blue-500' },
    { id: '4', label: 'Mahesh', role: 'Filer / Money Trail', x: 250, y: 320, color: 'fill-purple-500' },
    { id: '5', label: 'Anil', role: 'Receiver', x: 80, y: 120, color: 'fill-teal-500' },
    { id: '6', label: 'FIR-482/2025', role: 'Case Master Record', x: 420, y: 100, color: 'fill-slate-600', isCase: true },
  ];

  const connections = [
    { from: '1', to: '2', type: 'Co-accused', color: 'stroke-red-400' },
    { from: '1', to: '3', type: 'Shared Case', color: 'stroke-blue-400' },
    { from: '1', to: '4', type: 'Phone call contact', color: 'stroke-purple-400' },
    { from: '2', to: '4', type: 'Money Transfer', color: 'stroke-orange-400' },
    { from: '2', to: '5', type: 'Accomplice', color: 'stroke-teal-400' },
    { from: '1', to: '6', type: 'Primary Accused', color: 'stroke-slate-400', dashed: true },
    { from: '3', to: '6', type: 'Co-accused link', color: 'stroke-slate-400', dashed: true },
  ];

  return (
    <div className="space-y-6 font-sans pb-12">
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Side: Network Visualization canvas */}
        <div className="lg:col-span-8 bg-white rounded-card border border-border-light p-6 shadow-sm flex flex-col justify-between min-h-[500px]">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-2">
              <div className="w-2 h-5 bg-purple-accent rounded-full" />
              <h2 className="text-[18px] font-bold text-heading-dark">Criminal Network Discovery</h2>
            </div>
            
            <div className="flex items-center gap-2 text-[12px] font-bold text-slate-400">
              <Activity className="w-4 h-4 text-green-500 animate-pulse" />
              <span>Neo4j Graph Database Connected</span>
            </div>
          </div>

          {/* SVG Canvas Map Visualizer */}
          <div className="flex-1 bg-slate-900 rounded-custom-lg relative overflow-hidden border border-slate-950 flex items-center justify-center min-h-[400px]">
            <svg className="w-full h-full min-h-[400px]" viewBox="0 0 500 400">
              {/* Draw connections lines */}
              {connections.map((c, idx) => {
                const nFrom = nodes.find(n => n.id === c.from);
                const nTo = nodes.find(n => n.id === c.to);
                if (!nFrom || !nTo) return null;
                return (
                  <g key={idx}>
                    <line
                      x1={nFrom.x}
                      y1={nFrom.y}
                      x2={nTo.x}
                      y2={nTo.y}
                      className={`${c.color} stroke-[1.8]`}
                      strokeDasharray={c.dashed ? '4,4' : 'none'}
                    />
                    {/* Connection type label */}
                    <text
                      x={(nFrom.x + nTo.x) / 2}
                      y={(nFrom.y + nTo.y) / 2 - 5}
                      fill="#94A3B8"
                      fontSize="9"
                      fontWeight="bold"
                      textAnchor="middle"
                      className="bg-slate-950 px-1 font-mono"
                    >
                      {c.type}
                    </text>
                  </g>
                );
              })}

              {/* Draw nodes circles */}
              {nodes.map((n) => (
                <g key={n.id} className="cursor-pointer group">
                  <circle
                    cx={n.x}
                    cy={n.y}
                    r={n.isCase ? '16' : '12'}
                    className={`${n.color} stroke-slate-900 stroke-2 group-hover:scale-110 transition-transform duration-100`}
                  />
                  
                  {/* Outer circle rings */}
                  <circle
                    cx={n.x}
                    cy={n.y}
                    r={n.isCase ? '22' : '18'}
                    fill="none"
                    stroke={n.isCase ? '#475569' : '#3B82F6'}
                    strokeWidth="1"
                    strokeOpacity="0.4"
                    className="group-hover:scale-115 transition-transform duration-200"
                  />

                  {/* Label Text below node */}
                  <text
                    x={n.x}
                    y={n.y + (n.isCase ? 32 : 28)}
                    fill="#F8FAFC"
                    fontSize="11"
                    fontWeight="bold"
                    textAnchor="middle"
                  >
                    {n.label}
                  </text>
                  
                  {/* Small sublabel role */}
                  <text
                    x={n.x}
                    y={n.y + (n.isCase ? 42 : 38)}
                    fill="#64748B"
                    fontSize="8.5"
                    fontWeight="bold"
                    textAnchor="middle"
                  >
                    {n.role}
                  </text>
                </g>
              ))}
            </svg>

            {/* Quick stats floating tag */}
            <div className="absolute bottom-4 left-4 bg-slate-950/80 backdrop-blur-md border border-slate-800 rounded-btn p-3 text-[11px] font-semibold text-slate-300">
              <span className="block font-bold text-white mb-1">Graph Statistics</span>
              <span className="block text-slate-400">• Total Nodes Indexed: 14,892</span>
              <span className="block text-slate-400">• Association links: 86,432</span>
            </div>
          </div>
        </div>

        {/* Right Side: Network queries control dashboard */}
        <div className="lg:col-span-4 space-y-6">
          {/* Query parameters panel */}
          <div className="bg-white rounded-card border border-border-light p-6 shadow-sm space-y-5">
            <h3 className="text-[15px] font-bold text-heading-dark flex items-center gap-1.5 border-b border-slate-100 pb-3">
              <GitBranch className="w-4.5 h-4.5 text-primary-blue" />
              <span>Link Analysis Panel</span>
            </h3>

            {/* Suspect inputs */}
            <div className="space-y-4">
              <div className="space-y-1.5">
                <span className="text-[12px] text-gray-text font-bold uppercase tracking-wider">Node A (Suspect / Case)</span>
                <div className="relative flex items-center">
                  <input
                    type="text"
                    value={suspectA}
                    onChange={(e) => setSuspectA(e.target.value)}
                    className="w-full h-11 pl-10 pr-4 rounded-btn bg-bg-light border border-border-light text-[13px] text-heading-dark font-medium focus:outline-none focus:border-primary-blue"
                  />
                  <Search className="absolute left-3.5 w-4 h-4 text-slate-400" />
                </div>
              </div>

              <div className="space-y-1.5">
                <span className="text-[12px] text-gray-text font-bold uppercase tracking-wider">Node B (Target)</span>
                <div className="relative flex items-center">
                  <input
                    type="text"
                    value={suspectB}
                    onChange={(e) => setSuspectB(e.target.value)}
                    className="w-full h-11 pl-10 pr-4 rounded-btn bg-bg-light border border-border-light text-[13px] text-heading-dark font-medium focus:outline-none focus:border-primary-blue"
                  />
                  <Search className="absolute left-3.5 w-4 h-4 text-slate-400" />
                </div>
              </div>
            </div>

            <button onClick={() => console.log('Finding connection pathways:', suspectA, '→', suspectB)} className="w-full h-11 bg-primary-blue hover:bg-blue-600 text-white rounded-btn text-[13px] font-bold shadow-md shadow-blue-500/10 flex items-center justify-center gap-2 cursor-pointer transition-all hover:scale-102">
              <Share2 className="w-4 h-4" />
              <span>Find Connection Pathways</span>
            </button>
          </div>

          {/* Connected list profile matchings */}
          <div className="bg-white rounded-card border border-border-light p-6 shadow-sm space-y-4">
            <h3 className="text-[15px] font-bold text-heading-dark border-b border-slate-100 pb-3 flex items-center gap-1.5">
              <Users2 className="w-4.5 h-4.5 text-primary-blue" />
              <span>Discovered Relations</span>
            </h3>

            <div className="space-y-3">
              {[
                { name: 'Kumar (Main Accomplice)', detail: 'Shared co-accused in 4 case folders', icon: Shield, color: 'text-orange-500 bg-orange-50' },
                { name: 'Mahesh (Money Trail)', detail: 'Direct transfer of 15L found in bank checks', icon: ArrowRight, color: 'text-purple-500 bg-purple-50' },
                { name: 'Suresh (Transport provider)', detail: 'Spotted in calls 12 times prior to incident', icon: Phone, color: 'text-blue-500 bg-blue-50' },
              ].map((item, idx) => {
                const Icon = item.icon;
                return (
                  <div key={idx} className="flex gap-3 p-3 rounded-btn bg-slate-50 border border-slate-100">
                    <div className={`w-9 h-9 rounded-btn flex items-center justify-center flex-shrink-0 ${item.color}`}>
                      <Icon className="w-4 h-4" />
                    </div>
                    <div className="truncate">
                      <span className="text-[13px] font-bold text-heading-dark block leading-tight">{item.name}</span>
                      <span className="text-[11px] text-slate-500 font-semibold">{item.detail}</span>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
