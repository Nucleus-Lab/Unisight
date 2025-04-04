import React from 'react';
import { useChatContext } from '../../contexts/ChatContext';
import { ChatBubbleLeftIcon, XMarkIcon } from '@heroicons/react/24/outline';

const ChatToggleButton = () => {
  const { isChatOpen, setIsChatOpen } = useChatContext();

  return (
    <button
      onClick={() => setIsChatOpen(!isChatOpen)}
      className="fixed bottom-4 right-4 p-3 bg-[#00D179] text-white rounded-full shadow-lg hover:bg-[#00BD6D] focus:outline-none focus:ring-2 focus:ring-[#00D179] focus:ring-offset-2"
    >
      {isChatOpen ? (
        <XMarkIcon className="h-6 w-6" />
      ) : (
        <ChatBubbleLeftIcon className="h-6 w-6" />
      )}
    </button>
  );
};

export default ChatToggleButton; 