import React, { useState, useEffect, useRef } from 'react';
import VisualizationCard from '../visualization/VisualizationCard';
import { getVisualization, getCanvasVisualizations } from '../../services/api';
import { useCanvas } from '../../contexts/CanvasContext';

const Canvas = ({ visualizationIds = [], setActiveVisualizations }) => {
  const { currentCanvasId } = useCanvas();
  const [visualizations, setVisualizations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const bottomRef = useRef(null);

  // Add auto-scroll effect
  useEffect(() => {
    if (bottomRef.current) {
      bottomRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [visualizations]);

  useEffect(() => {
    const fetchVisualizations = async () => {
      console.log('Canvas - Starting to fetch visualizations');
      setLoading(true);
      setError(null);
      
      try {
        let results = [];
        
        // If we have direct visualization IDs, fetch those
        if (visualizationIds && visualizationIds.length > 0) {
          console.log('Canvas - Fetching specific visualizations:', visualizationIds);
          const visualizationPromises = visualizationIds.map(id => {
            return getVisualization(id).catch(error => {
              console.error(`Canvas - Error fetching visualization ${id}:`, error);
              return null;
            });
          });
          results = await Promise.all(visualizationPromises);
        }
        // If we have a current canvas ID, fetch all its visualizations
        else if (currentCanvasId) {
          console.log('Canvas - Fetching visualizations for canvas:', currentCanvasId);
          const canvasVisualizations = await getCanvasVisualizations(currentCanvasId);
          results = canvasVisualizations.map(viz => ({
            id: viz.visualization_id,
            data: viz.json_data
          }));
          
          // Set these visualizations as active visualizations
          if (setActiveVisualizations && canvasVisualizations.length > 0) {
            const canvasVizIds = canvasVisualizations.map(viz => viz.visualization_id);
            console.log('Canvas - Setting active visualizations from canvas:', canvasVizIds);
            setActiveVisualizations(prev => {
              // Only add new visualization IDs that aren't already in the list
              const newVizIds = canvasVizIds.filter(id => !prev.includes(id));
              return [...prev, ...newVizIds];
            });
          }
        }

        console.log('Canvas - Visualization results:', results);
        setVisualizations(results.filter(Boolean)); // Filter out null results
      } catch (error) {
        console.error('Canvas - Error fetching visualizations:', error);
        setError('Failed to load visualizations');
      } finally {
        setLoading(false);
      }
    };

    // Fetch if we have either visualization IDs or a canvas ID
    if ((visualizationIds && visualizationIds.length > 0) || currentCanvasId) {
      fetchVisualizations();
    } else {
      setLoading(false);
      setVisualizations([]);
    }
  }, [visualizationIds, currentCanvasId, setActiveVisualizations]); // Add setActiveVisualizations to dependencies

  if (loading) {
    return (
      <div className="h-full flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-gray-900"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="h-full flex items-center justify-center text-red-500">
        {error}
      </div>
    );
  }

  if (visualizations.length === 0) {
    return (
      <div className="h-full flex items-center justify-center text-gray-500">
        No visualizations available
      </div>
    );
  }

  return (
    <div className="flex flex-col w-full space-y-6 p-4 overflow-y-auto">
      {visualizations.map((visualization, index) => (
        <VisualizationCard
          key={`viz-${visualization.id || index}`}
          plotData={visualization.data}
        />
      ))}
      <div ref={bottomRef} /> {/* Add ref for auto-scrolling */}
    </div>
  );
};

export default Canvas; 