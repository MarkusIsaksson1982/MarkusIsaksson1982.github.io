import React, { useState, useEffect, useCallback } from 'react';
import { AlertCircle, Download, Upload, Settings, RefreshCw, Network } from 'lucide-react';

const BridgeNetwork = () => {
  const [curriculumData, setCurriculumData] = useState(null);
  const [graphData, setGraphData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [config, setConfig] = useState({
    apiBaseUrl: 'http://localhost:8000',
    layoutAlgorithm: 'spring',
    includeBridges: true,
    threshold: 0.1
  });
  
  // API calls
  const apiCall = useCallback(async (endpoint, method = 'GET', data = null) => {
    const url = `${config.apiBaseUrl}${endpoint}`;
    const options = {
      method,
      headers: {
        'Content-Type': 'application/json',
      }
    };
    
    if (data) {
      options.body = JSON.stringify(data);
    }
    
    const response = await fetch(url, options);
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }
    
    return response.json();
  }, [config.apiBaseUrl]);
  
  // Upload and parse PDF
  const handleFileUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;
    
    setLoading(true);
    setError(null);
    
    try {
      const formData = new FormData();
      formData.append('file', file);
      
      const response = await fetch(`${config.apiBaseUrl}/upload/pdf`, {
        method: 'POST',
        body: formData
      });
      
      if (!response.ok) {
        throw new Error(`Upload failed: ${response.statusText}`);
      }
      
      const result = await response.json();
      setCurriculumData(result.curriculum_data);
      
      // Generate graph visualization
      await generateGraph(result.curriculum_data);
      
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };
  
  // Parse manifest
  const handleManifestParse = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const result = await apiCall('/parse/manifest', 'POST', {
        manifest_path: 'gy25_manifest.json'
      });
      
      if (result.length > 0) {
        setCurriculumData(result[0].curriculum_data);
        await generateGraph(result[0].curriculum_data);
      }
      
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };
  
  // Generate graph visualization
  const generateGraph = async (data) => {
    try {
      const graphResult = await apiCall('/visualize/graph', 'POST', {
        curriculum_data: data,
        include_bridges: config.includeBridges,
        layout_algorithm: config.layoutAlgorithm
      });
      
      setGraphData(graphResult);
    } catch (err) {
      console.error('Graph generation failed:', err);
    }
  };
  
  // Analyze bridge for specific descriptor
  const analyzeBridge = async (descriptor) => {
    try {
      const result = await apiCall('/analyze/bridges', 'POST', {
        descriptor,
        language: 'sv',
        threshold: config.threshold
      });
      
      return result;
    } catch (err) {
      console.error('Bridge analysis failed:', err);
      return null;
    }
  };
  
  // Export data
  const handleExport = async (format) => {
    if (!curriculumData) return;
    
    try {
      const result = await apiCall(`/export/${format}`, 'POST', {
        curriculum_data: curriculumData,
        format
      });
      
      const blob = new Blob([result.content], { 
        type: format === 'json' ? 'application/json' : 'text/plain' 
      });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `curriculum.${format}`;
      a.click();
      URL.revokeObjectURL(url);
      
    } catch (err) {
      setError(`Export failed: ${err.message}`);
    }
  };
  
  // Simple network visualization using SVG
  const NetworkVisualization = ({ data }) => {
    if (!data || !data.nodes) return null;
    
    const width = 800;
    const height = 600;
    const centerX = width / 2;
    const centerY = height / 2;
    
    return (
      <div className=\"border rounded-lg p-4 bg-white\">
        <h3 className=\"text-lg font-semibold mb-4
