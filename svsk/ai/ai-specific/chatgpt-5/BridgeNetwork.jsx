import React, { useEffect, useRef, useState } from "react";
import * as d3 from "d3";

const BridgeNetwork = ({ apiUrl, filePath }) => {
  const svgRef = useRef();
  const [graph, setGraph] = useState({ nodes: [], edges: [] });

  useEffect(() => {
    if (!filePath) return;

    // Fetch graph data from backend
    fetch(`${apiUrl}/visualize/graph?path=${encodeURIComponent(filePath)}`)
      .then((res) => res.json())
      .then((data) => setGraph(data))
      .catch((err) => console.error("Graph fetch error:", err));
  }, [apiUrl, filePath]);

  useEffect(() => {
    if (!graph.nodes.length) return;

    const width = 800;
    const height = 600;

    const svg = d3.select(svgRef.current);
    svg.selectAll("*").remove(); // Clear previous render

    const color = (d) => {
      switch (d.type) {
        case "program":
          return "#1f77b4";
        case "inriktning":
          return "#ff7f0e";
        case "subject":
          return "#2ca02c";
        case "folder":
          return "#9467bd";
        case "file":
          return "#8c564b";
        default:
          return "#7f7f7f";
      }
    };

    const simulation = d3
      .forceSimulation(graph.nodes)
      .force(
        "link",
        d3.forceLink(graph.edges).id((d) => d.id).distance(80)
      )
      .force("charge", d3.forceManyBody().strength(-200))
      .force("center", d3.forceCenter(width / 2, height / 2));

    const link = svg
      .append("g")
      .attr("stroke", "#aaa")
      .attr("stroke-width", 1.5)
      .selectAll("line")
      .data(graph.edges)
      .join("line");

    const node = svg
      .append("g")
      .attr("stroke", "#fff")
      .attr("stroke-width", 1.5)
      .selectAll("circle")
      .data(graph.nodes)
      .join("circle")
      .attr("r", 8)
      .attr("fill", color)
      .call(
        d3
          .drag()
          .on("start", (event, d) => {
            if (!event.active) simulation.alphaTarget(0.3).restart();
            d.fx = d.x;
            d.fy = d.y;
          })
          .on("drag", (event, d) => {
            d.fx = event.x;
            d.fy = event.y;
          })
          .on("end", (event, d) => {
            if (!event.active) simulation.alphaTarget(0);
            d.fx = null;
            d.fy = null;
          })
      );

    const label = svg
      .append("g")
      .selectAll("text")
      .data(graph.nodes)
      .join("text")
      .attr("font-size", 10)
      .attr("dx", 12)
      .attr("dy", 4)
      .text((d) => d.id);

    simulation.on("tick", () => {
      link
        .attr("x1", (d) => d.source.x)
        .attr("y1", (d) => d.source.y)
        .attr("x2", (d) => d.target.x)
        .attr("y2", (d) => d.target.y);

      node.attr("cx", (d) => d.x).attr("cy", (d) => d.y);

      label.attr("x", (d) => d.x).attr("y", (d) => d.y);
    });
  }, [graph]);

  return (
    <div className="w-full flex justify-center">
      <svg ref={svgRef} width={800} height={600}></svg>
    </div>
  );
};

export default BridgeNetwork;
