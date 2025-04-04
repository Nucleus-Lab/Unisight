import React, { useEffect, useState } from 'react';
import { getCanvasFirstMessage, getCanvasFirstVisualization } from '../../services/api';

const CanvasCard = ({ canvasId, onClick }) => {
  const [preview, setPreview] = useState({
    message: null,
    visualization: null,
    loading: true,
    error: null
  });

  useEffect(() => {
    const loadPreviews = async () => {
      try {
        const [messageRes, visualizationRes] = await Promise.all([
          getCanvasFirstMessage(canvasId),
          getCanvasFirstVisualization(canvasId)
        ]);

        setPreview({
          message: messageRes,
          visualization: visualizationRes,
          loading: false,
          error: null
        });
      } catch (error) {
        console.error('Error loading canvas previews:', error);
        setPreview(prev => ({
          ...prev,
          loading: false,
          error: 'Failed to load preview'
        }));
      }
    };

    loadPreviews();
  }, [canvasId]);

  if (preview.loading) {
    return (
      <div className="bg-white rounded-lg shadow-md p-4 w-full max-w-sm h-48 animate-pulse">
        <div className="h-4 bg-gray-200 rounded w-3/4 mb-4"></div>
        <div className="h-32 bg-gray-200 rounded"></div>
      </div>
    );
  }

  return (
    <div 
      onClick={onClick}
      className="bg-white rounded-lg shadow-md p-4 w-full max-w-sm hover:shadow-lg transition-shadow duration-200 cursor-pointer"
    >
      {/* Message Preview */}
      <div className="mb-4">
        <p className="text-sm text-gray-600 line-clamp-2">
          {preview.message?.text || 'No message preview available'}
        </p>
        <span className="text-xs text-gray-400">
          {preview.message?.created_at && new Date(preview.message.created_at).toLocaleDateString()}
        </span>
      </div>

      {/* Visualization Preview */}
      {preview.visualization?.json_data ? (
        <div className="h-32 bg-gray-50 rounded-md p-2 overflow-hidden">
          {/* You can render a small version of the visualization here */}
          <pre className="text-xs text-gray-500 overflow-hidden">
            {JSON.stringify(preview.visualization.json_data, null, 2)}
          </pre>
        </div>
      ) : (
        <div className="h-32 bg-gray-50 rounded-md flex items-center justify-center">
          <span className="text-sm text-gray-400">No visualization available</span>
        </div>
      )}
    </div>
  );
};

export default CanvasCard; 