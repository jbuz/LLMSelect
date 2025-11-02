import React, { useState } from 'react';

const MessageInput = ({ onSendMessage, isLoading, onCancel, placeholder }) => {
  const [message, setMessage] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (message.trim() && !isLoading) {
      onSendMessage(message.trim());
      setMessage('');
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  const handleCancel = () => {
    if (onCancel) {
      onCancel();
    }
  };

  return (
    <form className="message-input-form" onSubmit={handleSubmit}>
      <div className="input-container">
        <textarea
          className="message-textarea"
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={placeholder || "Type your message... (Press Enter to send, Shift+Enter for new line)"}
          disabled={isLoading}
          rows={1}
        />
        {isLoading && onCancel ? (
          <button
            type="button"
            className="cancel-button"
            onClick={handleCancel}
            title="Cancel streaming"
          >
            ✕
          </button>
        ) : (
          <button
            type="submit"
            className="send-button"
            disabled={!message.trim() || isLoading}
          >
            <svg viewBox="0 0 24 24" width="20" height="20" fill="currentColor">
              <path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"/>
            </svg>
          </button>
        )}
      </div>
    </form>
  );
};

export default MessageInput;