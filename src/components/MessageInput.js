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
    // Ctrl+Enter or Cmd+Enter to send
    if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) {
      e.preventDefault();
      handleSubmit(e);
    }
    // Plain Enter (without Shift) also sends
    else if (e.key === 'Enter' && !e.shiftKey) {
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
          placeholder={placeholder || "Type your message... (Enter or Ctrl+Enter to send, Shift+Enter for new line)"}
          disabled={isLoading}
          rows={1}
          aria-label="Message input"
        />
        {isLoading && onCancel ? (
          <button
            type="button"
            className="cancel-button"
            onClick={handleCancel}
            title="Cancel streaming"
            aria-label="Cancel streaming"
          >
            ✕
          </button>
        ) : (
          <button
            type="submit"
            className="send-button"
            disabled={!message.trim() || isLoading}
            aria-label="Send message"
          >
            <svg viewBox="0 0 24 24" width="20" height="20" fill="currentColor" aria-hidden="true">
              <path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"/>
            </svg>
          </button>
        )}
      </div>
    </form>
  );
};

export default MessageInput;