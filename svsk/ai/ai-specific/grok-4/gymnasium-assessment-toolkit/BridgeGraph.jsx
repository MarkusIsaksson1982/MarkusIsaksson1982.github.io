import React, { useState } from 'react';
import { ResponsiveContainer, ScatterChart, Scatter, Tooltip } from 'recharts';

const BridgeGraph = ({ bridges }) => {
  const [view, setView] = useState('scatter');
  const [scoreMode, setScoreMode] = useState('raw');
  const [threshold, setThreshold] = useState(0.1);

  const filtered = Object.entries(bridges).filter(([_, {raw}]) => raw > threshold);
  const data = filtered.map(([subj, scores], i) => ({ subj, score: scores[scoreMode], x: i * 50, y: 100 - scores[scoreMode] * 100 }));

  return (
    <div>
      {/* Controls from refinement */}
      <select onChange={e => setView(e.target.value)}><option>scatter</option><option>network</option></select>
      {/* ... other controls */}
      {view === 'scatter' ? <ScatterChart data={data} /> : <BridgeNetwork bridges={bridges} />}
    </div>
  );
};
