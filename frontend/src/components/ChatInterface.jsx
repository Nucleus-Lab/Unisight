import React, { useState, useRef, useEffect } from 'react';
import { useChatContext } from '../../contexts/ChatContext';
import { useCanvas } from '../../contexts/CanvasContext';
import { usePrivy } from '@privy-io/react-auth';
import { XMarkIcon } from '@heroicons/react/24/outline';
import { sendMessage, getCanvasMessages } from '../../services/api';
import Message from '../chat/Message';
import Canvas from '../tabs/Canvas';

const ChatInterface = () => {
  const [message, setMessage] = useState('');
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isLoadingHistory, setIsLoadingHistory] = useState(false);
  const { isChatOpen, setIsChatOpen } = useChatContext();
  const { currentCanvasId, setCurrentCanvasId, clearCanvas } = useCanvas();
  const { ready, authenticated, user, login } = usePrivy();
  const messagesEndRef = useRef(null);
  const [activeVisualizations, setActiveVisualizations] = useState([]);
  
  console.log('Current canvas ID:', currentCanvasId);

  // Auto scroll to bottom when new messages arrive
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Load messages when canvas changes
  useEffect(() => {
    const loadMessages = async () => {
      if (currentCanvasId) {
        setIsLoadingHistory(true);
        try {
          const history = await getCanvasMessages(currentCanvasId);
          setMessages(history.map(msg => ({
            id: msg.message_id,
            text: msg.text,
            isUser: true, // Adjust based on your message structure
            timestamp: msg.created_at
          })));
        } catch (error) {
          console.error('Failed to load messages:', error);
        } finally {
          setIsLoadingHistory(false);
        }
      } else {
        setMessages([]); // Clear messages when no canvas is selected
      }
    };

    loadMessages();
  }, [currentCanvasId]);

  // Clear messages and canvas when authentication changes
  useEffect(() => {
    if (!authenticated) {
      setMessages([]);
      clearCanvas();
    }
  }, [authenticated, clearCanvas]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!message.trim() || !authenticated || !user?.wallet?.address) {
      return;
    }

    setIsLoading(true);
    try {
      console.log('Sending message with canvas ID:', currentCanvasId);
      const response = await sendMessage({
        walletAddress: user.wallet.address,
        canvasId: currentCanvasId,
        text: message
      });

      console.log('Response from server:', response);

      if (!currentCanvasId) {
        console.log('Setting new canvas ID:', response.canvas_id);
        setCurrentCanvasId(response.canvas_id);
      }

      // Add the new message to the messages array
      setMessages(prev => [...prev, {
        id: response.message_id,
        text: message,
        isUser: true,
        timestamp: new Date().toISOString()
      }]);

      setMessage('');
      console.log('Message sent successfully:', response);

      // Simulate AI response (replace this with actual AI response)
      setTimeout(() => {
        setMessages(prev => [...prev, {
          id: Date.now(),
          text: "This is a simulated AI response. Replace this with actual AI response.",
          isUser: false,
          timestamp: new Date().toISOString()
        }]);
      }, 1000);

      // If the response includes visualization IDs, update the state
      if (response.visualization_ids && Array.isArray(response.visualization_ids)) {
        console.log('ChatInterface - Setting active visualizations:', response.visualization_ids);
        setActiveVisualizations(response.visualization_ids);
      }

    } catch (error) {
      console.error('Failed to send message:', error);
    } finally {
      setIsLoading(false);
    }
  };

  console.log('ChatInterface - Current active visualizations:', activeVisualizations);

  if (!isChatOpen) {
    return null;
  }

  const isDisabled = !authenticated || isLoading;

  return (
    <div className="flex flex-col h-full w-[400px] min-w-[400px]">
      {/* Messages Container */}
      <div className="flex-1 overflow-y-auto p-4">
        {isLoadingHistory ? (
          <div className="flex items-center justify-center h-full">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-[#00D179]"></div>
          </div>
        ) : messages.length === 0 ? (
          <div className="h-full flex items-center justify-center">
            <h1 className="text-xl text-gray-700 font-normal">
              {currentCanvasId ? "No messages yet" : "What can I help with?"}
            </h1>
          </div>
        ) : (
          <div className="w-full">
            {messages.map((msg) => (
              <Message
                key={msg.id}
                text={msg.text}
                isUser={msg.isUser}
                timestamp={msg.timestamp}
              />
            ))}
            <div ref={messagesEndRef} />
          </div>
        )}
      </div>

      {/* Input Area */}
      <div className="border-t bg-white p-4">
        <div className="w-full">
          <form onSubmit={handleSubmit} className="flex flex-col space-y-2">
            <div className="flex">
              <input
                type="text"
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                placeholder={authenticated ? "Ask anything..." : "Connect wallet to start chatting..."}
                disabled={isDisabled}
                className="flex-1 px-4 py-3 border rounded-l-lg focus:outline-none focus:ring-1 focus:ring-[#00D179] focus:border-[#00D179] text-base 
                  disabled:bg-gray-50 disabled:text-gray-500 disabled:border-gray-200"
              />
              <button
                type="submit"
                disabled={isDisabled || !message.trim()}
                className={`px-6 py-3 rounded-r-lg focus:outline-none focus:ring-2 focus:ring-[#00D179] focus:ring-offset-2 
                  ${isDisabled || !message.trim()
                    ? 'bg-gray-300 cursor-not-allowed'
                    : 'bg-[#00D179] hover:bg-[#00BD6D]'
                  } text-white transition-colors duration-200 whitespace-nowrap`}
              >
                {isLoading ? 'Sending...' : 'Send'}
              </button>
            </div>

            {/* Authentication reminder */}
            {!authenticated && (
              <div className="text-center">
                <span className="text-sm text-gray-500">
                  Please{' '}
                  <a
                    href="#"
                    onClick={(e) => {
                      e.preventDefault();
                      login();
                    }}
                    className="text-[#00D179] hover:text-[#00BD6D] font-medium cursor-pointer"
                  >
                    connect your wallet
                  </a>
                  {' '}to start chatting
                </span>
              </div>
            )}
          </form>
        </div>
      </div>
      <Canvas visualizationIds={activeVisualizations} />
    </div>
  );
};

export default ChatInterface; 