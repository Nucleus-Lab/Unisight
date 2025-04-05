import React, { useState, useEffect, useCallback } from 'react';
import { getMCPServers, getCurrentMCP, selectMCPServer } from '../services/api';

const MCPSelector = () => {
  const [mcpServers, setMcpServers] = useState([]);
  const [currentServer, setCurrentServer] = useState('');
  const [isLoading, setIsLoading] = useState(true);
  const [isChanging, setIsChanging] = useState(false);

  useEffect(() => {
    loadMCPData();
  }, []);

  const loadMCPData = async () => {
    try {
      const [servers, current] = await Promise.all([
        getMCPServers(),
        getCurrentMCP()
      ]);
      setMcpServers(servers);
      setCurrentServer(current.current_server);
    } catch (error) {
      console.error('Error loading MCP data:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleServerChange = async (event) => {
    const newServer = event.target.value;
    setIsChanging(true);
    try {
      await selectMCPServer(newServer);
      setCurrentServer(newServer);
      // Show a success message
      const message = document.createElement('div');
      message.className = 'fixed bottom-4 right-4 bg-green-500 text-white px-4 py-2 rounded-lg shadow-lg transition-opacity duration-500';
      message.textContent = `Switched to ${newServer} data source`;
      document.body.appendChild(message);
      
      // Remove the message after 3 seconds
      setTimeout(() => {
        message.style.opacity = '0';
        setTimeout(() => document.body.removeChild(message), 500);
      }, 3000);

    } catch (error) {
      console.error('Error changing MCP server:', error);
      // Show error message
      const errorMessage = document.createElement('div');
      errorMessage.className = 'fixed bottom-4 right-4 bg-red-500 text-white px-4 py-2 rounded-lg shadow-lg transition-opacity duration-500';
      errorMessage.textContent = 'Failed to switch data source';
      document.body.appendChild(errorMessage);
      
      setTimeout(() => {
        errorMessage.style.opacity = '0';
        setTimeout(() => document.body.removeChild(errorMessage), 500);
      }, 3000);
    } finally {
      setIsChanging(false);
    }
  };

  if (isLoading) {
    return <div className="animate-pulse">Loading...</div>;
  }

  return (
    <div className="flex items-center space-x-2">
      <label htmlFor="mcp-select" className="text-sm text-gray-600">
        Data Source:
      </label>
      <select
        id="mcp-select"
        value={currentServer}
        onChange={handleServerChange}
        disabled={isChanging}
        className={`px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-[#00D179] focus:border-[#00D179] text-sm
          ${isChanging ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}`}
      >
        {mcpServers.map((server) => (
          <option key={server.name} value={server.name}>
            {server.description}
          </option>
        ))}
      </select>
      {isChanging && (
        <div className="w-4 h-4 border-2 border-[#00D179] border-t-transparent rounded-full animate-spin"></div>
      )}
    </div>
  );
};

export default MCPSelector; 