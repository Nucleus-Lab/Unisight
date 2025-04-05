import React, { useState, useRef, useEffect } from 'react';
import { useChatContext } from '../../contexts/ChatContext';
import { useCanvas } from '../../contexts/CanvasContext';
import { usePrivy } from '@privy-io/react-auth';
import { XMarkIcon } from '@heroicons/react/24/outline';
import { sendMessage, getCanvasMessages, getMessage } from '../../services/api';
import Message from '../chat/Message';
import PropTypes from 'prop-types';
import { AI_USER_ID } from '../../constants/constants';
import MCPSelector from '../MCPSelector';

const ChatInterface = ({ setActiveTab, setActiveVisualizations }) => {
  const [message, setMessage] = useState('');
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isLoadingHistory, setIsLoadingHistory] = useState(false);
  const { isChatOpen, setIsChatOpen } = useChatContext();
  const { currentCanvasId, setCurrentCanvasId, clearCanvas } = useCanvas();
  const { ready, authenticated, user, login } = usePrivy();
  const messagesEndRef = useRef(null);
  
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
          console.log('Message history:', history);
          // for the first message, log the data type of the user_id
          console.log('First message user_id:', history[0].user_id);
          console.log('First message user_id type:', typeof history[0].user_id);
          console.log('AI_USER_ID:', AI_USER_ID);
          console.log('AI_USER_ID type:', typeof AI_USER_ID);
          setMessages(history.map(msg => ({
            id: msg.message_id,
            text: msg.text,
            isUser: parseInt(msg.user_id) !== AI_USER_ID, // Check if the message is from AI
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

    const userMessage = message;
    setMessage(''); // Clear input immediately
    setIsLoading(true);

    try {
      // Add user message immediately
      const userMessageId = Date.now();
      setMessages(prev => [...prev, {
        id: userMessageId,
        text: userMessage,
        isUser: true,
        timestamp: new Date().toISOString()
      }]);

      // Show AI is typing
      const typingId = 'typing-' + Date.now(); // Unique ID for typing indicator
      setMessages(prev => [...prev, {
        id: typingId,
        text: '',
        isUser: false,
        isTyping: true
      }]);

      // Send message and get response
      const response = await sendMessage({
        walletAddress: user.wallet.address,
        canvasId: currentCanvasId,
        text: userMessage
      });

      if (!currentCanvasId) {
        setCurrentCanvasId(response.canvas_id);
      }

      // Remove typing indicator and add AI response
      setMessages(prev => {
        // Remove the typing indicator
        const withoutTyping = prev.filter(msg => msg.id !== typingId);
        
        // Add the AI response
        const aiMessage = {
          id: response.ai_message_id,
          text: response.ai_message_text,
          isUser: false,
          timestamp: response.created_at
        };

        // Get the message from the API if needed
        if (response.ai_message_id) {
          getMessage(response.ai_message_id)
            .then(fullMessage => {
              // Update the message with complete data if needed
              setMessages(prev => prev.map(msg => 
                msg.id === response.ai_message_id 
                  ? { ...msg, text: fullMessage.text }
                  : msg
              ));
            })
            .catch(console.error);
        }

        return [...withoutTyping, aiMessage];
      });

      // Handle visualizations if any
      if (response.visualization_ids?.length > 0) {
        setActiveVisualizations(response.visualization_ids);
        setActiveTab('canvas');
      }

    } catch (error) {
      console.error('Failed to send message:', error);
      // Remove typing indicator and show error
      setMessages(prev => {
        const withoutTyping = prev.filter(msg => msg.id !== 'typing');
        return [...withoutTyping, {
          id: Date.now(),
          text: "Failed to get response. Please try again.",
          isUser: false,
          timestamp: new Date().toISOString(),
          isError: true
        }];
      });
    } finally {
      setIsLoading(false);
    }
  };

  // Update the Message component to handle error messages
  const renderMessages = () => {
    if (isLoadingHistory) {
      return (
        <div className="flex items-center justify-center h-full">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-[#00D179]"></div>
        </div>
      );
    }

    if (messages.length === 0) {
      return (
        <div className="h-full flex items-center justify-center">
          <h1 className="text-xl text-gray-700 font-normal">
            {currentCanvasId ? "No messages yet" : "What can I help with?"}
          </h1>
        </div>
      );
    }

    return (
      <div className="w-full">
        {messages.map((msg) => (
          <Message
            key={msg.id}
            text={msg.text}
            isUser={msg.isUser}
            timestamp={msg.timestamp}
            isError={msg.isError}
            isTyping={msg.isTyping}
          />
        ))}
        <div ref={messagesEndRef} />
      </div>
    );
  };

  if (!isChatOpen) {
    return null;
  }

  const isDisabled = !authenticated || isLoading;

  return (
    <div className="flex flex-col h-full w-[400px] min-w-[400px]">
      {/* Messages Container */}
      <div className="flex-1 overflow-y-auto p-4">
        <div className="border-b bg-white p-4 flex justify-between items-center">
          <MCPSelector />
        </div>
        {renderMessages()}
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

ChatInterface.propTypes = {
  setActiveTab: PropTypes.func.isRequired,
  setActiveVisualizations: PropTypes.func.isRequired,
};

export default ChatInterface; 