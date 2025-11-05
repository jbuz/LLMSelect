import React, { useEffect, useRef, memo } from 'react';
import MarkdownMessage from './MarkdownMessage';

const MessageList = memo(({ messages, isLoading, isStreaming, currentMessage }) => {
  const messagesEndRef = useRef(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isLoading, currentMessage]);

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
            {message.role === 'assistant' ? (
              <MarkdownMessage content={message.content} />
            ) : (
              <div className="message-text">{message.content}</div>
            )}
          </div>
        </div>
      ))}
      
      {isStreaming && currentMessage && (
        <div className="message assistant streaming">
          <div className="message-avatar">🤖</div>
          <div className="message-content">
            <MarkdownMessage content={currentMessage} />
            <span className="streaming-cursor">▊</span>
          </div>
        </div>
      )}
      
      {isLoading && !isStreaming && (
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
});

MessageList.displayName = 'MessageList';

export default MessageList;