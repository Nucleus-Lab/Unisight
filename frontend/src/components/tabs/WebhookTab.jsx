import React, { useState, useEffect } from 'react';
import { getLatestWebhookEvent } from '../../services/api';

const WebhookTab = () => {
  const [latestEvent, setLatestEvent] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Hardcoded subscription details from the successful webhook creation
  const webhookDetails = {
    subscriptionId: '5660',
    description: 'Monitor all transactions for wallet 0xae2fc483527b8ef99eb5d9b44875f005ba1fae13',
    protocol: 'ethereum',
    network: 'mainnet',
    eventType: 'ADDRESS_ACTIVITY',
    notification: {
      webhookUrl: 'https://d0a2-111-235-226-130.ngrok-free.app'
    },
    condition: {
      addresses: ['0xae2fc483527b8ef99eb5d9b44875f005ba1fae13']
    },
    createdAt: '2025-04-05T20:01:54.880Z'
  };

  // Function to format timestamp to local time
  const formatTimestamp = (timestamp) => {
    try {
      const date = new Date(timestamp);
      return date.toLocaleString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit',
        hour12: true,
        timeZoneName: 'short'
      });
    } catch (error) {
      console.error('Error formatting timestamp:', error);
      return timestamp; // Return original timestamp if parsing fails
    }
  };

  // Function to fetch the latest event
  const fetchLatestEvent = async () => {
    try {
      setLoading(true);
      const data = await getLatestWebhookEvent();
      setLatestEvent(data);
      setError(null);
    } catch (error) {
      console.error('Error fetching latest event:', error);
      setError(error.message);
    } finally {
      setLoading(false);
    }
  };

  // Fetch latest event periodically
  useEffect(() => {
    fetchLatestEvent();
    const interval = setInterval(fetchLatestEvent, 5000); // Poll every 5 seconds
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="space-y-4">
      {/* Webhook Configuration Section */}
      <div className="bg-white p-4 rounded-lg shadow-sm border border-gray-200">
        <h2 className="text-lg font-medium mb-2">Active Webhook Configuration</h2>
        <div className="bg-gray-50 p-3 rounded-md space-y-2">
          <div>
            <p className="text-sm text-gray-600 mb-1">Subscription ID:</p>
            <code className="bg-gray-100 px-2 py-1 rounded text-sm font-mono">
              {webhookDetails.subscriptionId}
            </code>
          </div>
          
          <div>
            <p className="text-sm text-gray-600 mb-1">Webhook URL:</p>
            <code className="bg-gray-100 px-2 py-1 rounded text-sm font-mono break-all">
              {webhookDetails.notification.webhookUrl}/api/webhook/nodit
            </code>
          </div>

          <div>
            <p className="text-sm text-gray-600 mb-1">Description:</p>
            <p className="text-sm">{webhookDetails.description}</p>
          </div>

          <div>
            <p className="text-sm text-gray-600 mb-1">Configuration:</p>
            <div className="bg-gray-100 p-2 rounded">
              <p className="text-sm"><span className="font-medium">Protocol:</span> {webhookDetails.protocol}</p>
              <p className="text-sm"><span className="font-medium">Network:</span> {webhookDetails.network}</p>
              <p className="text-sm"><span className="font-medium">Event Type:</span> {webhookDetails.eventType}</p>
              <p className="text-sm"><span className="font-medium">Monitored Address:</span></p>
              <code className="text-xs font-mono break-all">
                {webhookDetails.condition.addresses[0]}
              </code>
            </div>
          </div>

          <div>
            <p className="text-sm text-gray-600 mb-1">Created At:</p>
            <p className="text-sm">
              {formatTimestamp(webhookDetails.createdAt)}
            </p>
          </div>
        </div>
      </div>

      {/* Latest Event Section */}
      <div className="bg-white p-4 rounded-lg shadow-sm border border-gray-200">
        <h2 className="text-lg font-medium mb-2">Latest Received Event</h2>
        {latestEvent ? (
          <div className="bg-gray-50 p-3 rounded-md space-y-2">
            <div>
              <p className="text-sm text-gray-600 mb-1">Event ID:</p>
              <code className="bg-gray-100 px-2 py-1 rounded text-sm font-mono">
                {latestEvent.id}
              </code>
            </div>
            
            <div>
              <p className="text-sm text-gray-600 mb-1">Timestamp:</p>
              <p className="text-sm">
                {formatTimestamp(latestEvent.timestamp)}
              </p>
            </div>

            <div>
              <p className="text-sm text-gray-600 mb-1">Event Type:</p>
              <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-blue-100 text-blue-800">
                {latestEvent.event_type}
              </span>
            </div>

            <div>
              <p className="text-sm text-gray-600 mb-1">Status:</p>
              <span className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium
                ${latestEvent.status === 'success' ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'}`}>
                {latestEvent.status}
              </span>
            </div>

            <div>
              <p className="text-sm text-gray-600 mb-1">Data:</p>
              <pre className="bg-gray-100 p-2 rounded text-xs font-mono whitespace-pre-wrap overflow-x-auto">
                {JSON.stringify(latestEvent.data, null, 2)}
              </pre>
            </div>
          </div>
        ) : (
          <div className="text-center text-gray-500 py-4">
            No events received yet
          </div>
        )}
      </div>

      {/* Important Notes Section */}
      <div className="bg-yellow-50 p-4 rounded-lg border border-yellow-200">
        <h3 className="text-sm font-medium text-yellow-800 mb-2">Important Notes</h3>
        <ul className="list-disc list-inside text-sm text-yellow-700 space-y-1">
          <li>This webhook URL is temporary and will change when ngrok is restarted</li>
          <li>The free ngrok session expires after 2 hours</li>
          <li>You'll need to create a new webhook subscription with the new URL after restarting ngrok</li>
          <li>Monitor your webhook events in the ngrok inspector at: <a href="http://127.0.0.1:4040" target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline">http://127.0.0.1:4040</a></li>
        </ul>
      </div>
    </div>
  );
};

export default WebhookTab; 