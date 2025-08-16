import React, { useEffect, useRef } from 'react';

const MessageList = ({ messages, isLoading }) => {
  const messagesEndRef = useRef(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isLoading]);

  return (
    <div className="messages-container">
      {messages.length === 0 && (
        <div className="welcome-message">
          <h2>Welcome to MultiChat</h2>
          <p>Choose your AI model and start chatting!</p>
        </div>
      )}
      
      {messages.map((message, index) => (
        <div key={index} className={`message ${message.role} ${message.isError ? 'error' : ''}`}>
          <div className="message-avatar">
            {message.role === 'user' ? '👤' : '🤖'}
          </div>
          <div className="message-content">
            <div className="message-text">{message.content}</div>
          </div>
        </div>
      ))}
      
      {isLoading && (
        <div className="message assistant">
          <div className="message-avatar">🤖</div>
          <div className="message-content">
            <div className="typing-indicator">
              <span></span>
              <span></span>
              <span></span>
            </div>
          </div>
        </div>
      )}
      
      <div ref={messagesEndRef} />
    </div>
  );
};

export default MessageList;