import React, { useState } from 'react';
import { useChatContext } from '../../contexts/ChatContext';
import { XMarkIcon } from '@heroicons/react/24/outline';

const ChatInterface = () => {
  const [message, setMessage] = useState('');
  const { isChatOpen, setIsChatOpen } = useChatContext();
  
  console.log('Rendering ChatInterface');

  const handleSubmit = (e) => {
    e.preventDefault();
    console.log('Sending message:', message);
    setMessage('');
  };

  if (!isChatOpen) {
    return null;
  }

  return (
    <div className="flex flex-col h-full">
      {/* Center Content Container */}
      <div className="flex-1 flex flex-col items-center justify-center max-w-2xl mx-auto w-full px-4">
        {/* Content Wrapper - keeps elements close together */}
        <div className="flex flex-col items-center space-y-6">
          {/* Welcome Text */}
          <div className="text-center">
            <h1 className="text-xl text-gray-700 font-normal">
              What can I help with?
            </h1>
          </div>
          
          {/* Input Area */}
          <div className="w-full max-w-xl">
            <form onSubmit={handleSubmit} className="flex w-full">
              <input
                type="text"
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                placeholder="Ask anything..."
                className="flex-1 px-4 py-3 border rounded-l-lg focus:outline-none focus:ring-1 focus:ring-[#00D179] focus:border-[#00D179] text-base"
              />
              <button
                type="submit"
                className="px-6 py-3 bg-[#00D179] text-white rounded-l-none rounded-r-lg hover:bg-[#00BD6D] focus:outline-none focus:ring-2 focus:ring-[#00D179] focus:ring-offset-2"
              >
                Send
              </button>
            </form>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ChatInterface; 