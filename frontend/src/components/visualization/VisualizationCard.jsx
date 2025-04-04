import React from 'react';
import Plot from 'react-plotly.js';

const VisualizationCard = ({ plotData }) => {
  console.log('VisualizationCard - Raw plotData received:', plotData);

  // Ensure plotData is properly formatted for Plotly
  const plotlyData = React.useMemo(() => {
    try {
      const parsedData = typeof plotData === 'string' ? JSON.parse(plotData) : plotData;
      console.log('VisualizationCard - Parsed plotData:', {
        fullData: parsedData,
        hasData: !!parsedData?.data,
        hasLayout: !!parsedData?.layout,
        dataStructure: parsedData?.data ? 
          `Array of ${parsedData.data.length} traces` : 
          'No data array found'
      });

      // Verify the data structure is correct for Plotly
      if (!parsedData?.data || !Array.isArray(parsedData.data)) {
        console.error('VisualizationCard - Invalid data structure:', parsedData);
        return null;
      }

      return parsedData;
    } catch (error) {
      console.error('VisualizationCard - Error parsing plot data:', error);
      return null;
    }
  }, [plotData]);

  if (!plotlyData) {
    console.warn('VisualizationCard - No valid plotly data available');
    return (
      <div className="p-4 border rounded-lg bg-white shadow-sm">
        <p className="text-red-500">Error: Invalid visualization data structure</p>
        <pre className="text-xs mt-2 bg-gray-100 p-2 rounded">
          {JSON.stringify(plotData, null, 2)}
        </pre>
      </div>
    );
  }

  console.log('VisualizationCard - Rendering Plot with data:', {
    dataLength: plotlyData.data.length,
    layout: plotlyData.layout
  });

  return (
    <div className="p-4 border rounded-lg bg-white shadow-sm">
      <Plot
        data={plotlyData.data}
        layout={{
          ...plotlyData.layout,
          autosize: true,
          margin: { l: 50, r: 50, t: 50, b: 50 },
        }}
        config={{
          responsive: true,
          displayModeBar: true,
          scrollZoom: true,
        }}
        className="w-full h-full"
        style={{ minHeight: '400px' }}
        onInitialized={(figure) => {
          console.log('VisualizationCard - Plot initialized:', figure);
        }}
        onError={(err) => {
          console.error('VisualizationCard - Plot error:', err);
        }}
        onUpdate={(figure) => {
          console.log('VisualizationCard - Plot updated:', figure);
        }}
      />
    </div>
  );
};

export default VisualizationCard; 