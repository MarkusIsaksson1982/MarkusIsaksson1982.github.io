import React from 'react';
import ForceGraph2D from 'react-force-graph-2d';

const BridgeNetwork = ({ bridges }) => {
  const nodes = [{ id: 'Descriptor' }, ...Object.keys(bridges).map(id => ({ id }))];
  const links = Object.entries(bridges).map(([subj, {raw}]) => ({ source: 'Descriptor', target: subj, value: raw }));
  return <ForceGraph2D graphData={{ nodes, links }} linkWidth={l => l.value * 5} />;
};
