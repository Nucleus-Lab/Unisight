import React, { useState, useEffect } from 'react';
import VisualizationCard from '../visualization/VisualizationCard';
import { getVisualization } from '../../services/api';

const Canvas = ({ visualizationIds = [] }) => {
  console.log('Canvas - Rendering with visualization IDs:', visualizationIds);
  
  const [visualizations, setVisualizations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Separate useEffect for debugging
  useEffect(() => {
    console.log('Canvas - useEffect triggered, visualizationIds:', visualizationIds);
  }, [visualizationIds]);

  useEffect(() => {
    const fetchVisualizations = async () => {
      console.log('Canvas - Starting to fetch visualizations for IDs:', visualizationIds);
      setLoading(true);
      setError(null);
      
      try {
        const visualizationPromises = visualizationIds.map(id => {
          console.log(`Canvas - Fetching visualization ID: ${id}`);
          return getVisualization(id).catch(error => {
            console.error(`Canvas - Error fetching visualization ${id}:`, error);
            return null;
          });
        });

        const results = await Promise.all(visualizationPromises);
        console.log('Canvas - Raw visualization results:', results);
        
        setVisualizations(results);
      } catch (error) {
        console.error('Canvas - Error fetching visualizations:', error);
        setError('Failed to load visualizations');
      } finally {
        setLoading(false);
      }
    };

    // Add this console log to debug the condition
    console.log('Canvas - Checking visualization IDs length:', {
      length: visualizationIds.length,
      ids: visualizationIds
    });

    if (visualizationIds && visualizationIds.length > 0) {
      console.log('Canvas - Calling fetchVisualizations');
      fetchVisualizations();
    } else {
      console.log('Canvas - No visualization IDs to fetch');
      setLoading(false);
    }
  }, [visualizationIds]); // Make sure dependency array includes visualizationIds

  // Add loading state log
  useEffect(() => {
    console.log('Canvas - Loading state changed:', loading);
  }, [loading]);

  if (loading) {
    console.log('Canvas - Rendering loading state');
    return (
      <div className="h-full flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-gray-900"></div>
      </div>
    );
  }

  if (error) {
    console.log('Canvas - Rendering error state:', error);
    return (
      <div className="h-full flex items-center justify-center text-red-500">
        {error}
      </div>
    );
  }

  if (visualizations.length === 0) {
    console.log('Canvas - Rendering empty state');
    return (
      <div className="h-full flex items-center justify-center text-gray-500">
        {visualizationIds.length === 0 
          ? "No visualizations available"
          : "Loading visualizations..."}
      </div>
    );
  }

  console.log('Canvas - Rendering visualizations:', visualizations);
  return (
    <div className="flex flex-col w-full space-y-6 p-4">
      {visualizations.map((visualization, index) => {
        console.log(`Canvas - Rendering visualization ${index}:`, visualization);
        return (
          <VisualizationCard
            key={`viz-${visualization.id || index}`}
            plotData={visualization.data}
          />
        );
      })}
    </div>
  );
};

export default Canvas; 