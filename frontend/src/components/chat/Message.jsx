import React from 'react';
import PropTypes from 'prop-types';

const Message = ({ text, isUser, timestamp, isError }) => {
  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-4`}>
      <div
        className={`max-w-[80%] rounded-lg px-4 py-2 ${
          isUser
            ? 'bg-[#00D179] text-white'
            : isError
            ? 'bg-red-100 text-red-700'
            : 'bg-gray-100 text-gray-800'
        }`}
      >
        <p className="text-sm">{text}</p>
        <span className="text-xs opacity-75 mt-1 block">
          {new Date(timestamp).toLocaleTimeString()}
        </span>
      </div>
    </div>
  );
};

Message.propTypes = {
  text: PropTypes.string.isRequired,
  isUser: PropTypes.bool.isRequired,
  timestamp: PropTypes.string.isRequired,
  isError: PropTypes.bool
};

Message.defaultProps = {
  isError: false
};

export default Message; 