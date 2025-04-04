import React from 'react';

const Message = ({ text, isUser, timestamp }) => {
  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-4`}>
      <div
        className={`w-fit max-w-[280px] rounded-2xl px-4 py-2 break-words ${
          isUser
            ? 'bg-[#00D179] text-white rounded-br-none'
            : 'bg-gray-100 text-gray-800 rounded-bl-none'
        }`}
      >
        <p className="text-sm whitespace-pre-wrap">{text}</p>
        <span className={`text-xs mt-1 block ${isUser ? 'text-gray-100' : 'text-gray-500'}`}>
          {new Date(timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
        </span>
      </div>
    </div>
  );
};

export default Message; 