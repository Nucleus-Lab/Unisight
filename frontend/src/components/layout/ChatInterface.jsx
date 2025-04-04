import React, { useState, useRef, useEffect } from 'react';
import { useChatContext } from '../../contexts/ChatContext';
import { usePrivy } from '@privy-io/react-auth';
import { XMarkIcon } from '@heroicons/react/24/outline';
import { sendMessage } from '../../services/api';
import Message from '../chat/Message';

const ChatInterface = () => {
  const [message, setMessage] = useState('');
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const { isChatOpen, setIsChatOpen } = useChatContext();
  const { ready, authenticated, user, login } = usePrivy();
  const [currentCanvasId, setCurrentCanvasId] = useState(null);
  const messagesEndRef = useRef(null);
  
  console.log('Current canvas ID:', currentCanvasId);

  // Auto scroll to bottom when new messages arrive
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

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

    } catch (error) {
      console.error('Failed to send message:', error);
    } finally {
      setIsLoading(false);
    }
  };

  if (!isChatOpen) {
    return null;
  }

  const isDisabled = !authenticated || isLoading;

  return (
    <div className="flex flex-col h-full w-[400px] min-w-[400px]">
      {/* Messages Container */}
      <div className="flex-1 overflow-y-auto p-4">
        {messages.length === 0 ? (
          <div className="h-full flex items-center justify-center">
            <h1 className="text-xl text-gray-700 font-normal">
              What can I help with?
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
    </div>
  );
};

export default ChatInterface; 