import React from 'react';
import PropTypes from 'prop-types';

const Message = ({ text, isUser, timestamp, isError, isTyping }) => {
  if (isTyping) {
    return (
      <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-4`}>
        <div className="flex items-center space-x-2 px-4 py-2 rounded-lg bg-gray-100">
          <div className="animate-pulse flex space-x-1">
            <div className="h-2 w-2 bg-gray-400 rounded-full"></div>
            <div className="h-2 w-2 bg-gray-400 rounded-full"></div>
            <div className="h-2 w-2 bg-gray-400 rounded-full"></div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-4`}>
      <div className={`max-w-[90%] break-words ${
        isUser 
          ? 'bg-[#00D179] text-white rounded-l-lg rounded-tr-lg' 
          : 'bg-gray-100 text-gray-800 rounded-r-lg rounded-tl-lg'
      } px-4 py-2`}>
        <div className="text-sm whitespace-pre-wrap overflow-wrap-anywhere">
          {text}
        </div>
        <div className={`text-xs mt-1 ${isUser ? 'text-white/70' : 'text-gray-500'}`}>
          {timestamp ? new Date(timestamp).toLocaleTimeString() : ''}
        </div>
      </div>
    </div>
  );
};

Message.propTypes = {
  text: PropTypes.string.isRequired,
  isUser: PropTypes.bool.isRequired,
  timestamp: PropTypes.string.isRequired,
  isError: PropTypes.bool,
  isTyping: PropTypes.bool
};

Message.defaultProps = {
  isError: false
};

export default Message; 