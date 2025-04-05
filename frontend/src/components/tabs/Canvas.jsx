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
  const visualizationRefs = useRef({});

  // Add auto-scroll effect for new visualizations
  useEffect(() => {
    if (bottomRef.current) {
      bottomRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [visualizations]);

  // Listen for visualization update events
  useEffect(() => {
    const handleVisualizationUpdated = (event) => {
      const { visualizationId } = event.detail;
      console.log('Canvas - Received visualization update event for ID:', visualizationId);
      
      // Find the visualization in our list
      const vizIndex = visualizations.findIndex(viz => viz.id === visualizationId);
      
      if (vizIndex >= 0) {
        console.log('Canvas - Found visualization at index:', vizIndex);
        
        // Create a ref for this visualization if it doesn't exist
        if (!visualizationRefs.current[visualizationId]) {
          visualizationRefs.current[visualizationId] = React.createRef();
        }
        
        // Scroll to the visualization after a short delay to ensure it's rendered
        setTimeout(() => {
          if (visualizationRefs.current[visualizationId]?.current) {
            console.log('Canvas - Scrolling to visualization:', visualizationId);
            visualizationRefs.current[visualizationId].current.scrollIntoView({ 
              behavior: 'smooth',
              block: 'center'
            });
          } else {
            console.warn('Canvas - Could not find ref for visualization:', visualizationId);
          }
        }, 100);
      } else {
        console.warn('Canvas - Visualization not found in current list:', visualizationId);
      }
    };

    // Add event listener
    window.addEventListener('visualizationUpdated', handleVisualizationUpdated);
    
    // Clean up
    return () => {
      window.removeEventListener('visualizationUpdated', handleVisualizationUpdated);
    };
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
        <div 
          key={`viz-${visualization.id || index}`}
          ref={visualizationRefs.current[visualization.id] || null}
        >
          <VisualizationCard
            plotData={visualization.data}
            visualizationId={visualization.id}
          />
        </div>
      ))}
      <div ref={bottomRef} /> {/* Add ref for auto-scrolling */}
    </div>
  );
};

export default Canvas; 