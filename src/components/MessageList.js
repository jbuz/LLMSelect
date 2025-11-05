import React, { useEffect, useRef, memo, useMemo } from 'react';
import { VariableSizeList as List } from 'react-window';
import MarkdownMessage from './MarkdownMessage';

// Configuration constants for virtualization
const VIRTUALIZATION_THRESHOLD = 50; // Messages count threshold for enabling virtualization
const CHARS_PER_LINE = 80; // Estimated characters per line for sizing
const PIXELS_PER_LINE = 24; // Height per line of text in pixels
const BASE_HEIGHT = 60; // Minimum height for a message row in pixels
const MAX_HEIGHT = 500; // Maximum height for a message row in pixels

const MessageList = memo(({ messages, isLoading, isStreaming, currentMessage }) => {
  const messagesEndRef = useRef(null);
  const listRef = useRef(null);

  useEffect(() => {
    // Auto-scroll to bottom on new messages
    if (messages.length < VIRTUALIZATION_THRESHOLD) {
      messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    } else if (listRef.current) {
      listRef.current.scrollToItem(messages.length, 'end');
    }
  }, [messages, isLoading, currentMessage]);

  // Estimate row height for virtualization
  const getItemSize = useMemo(() => {
    return (index) => {
      const message = messages[index];
      if (!message) return BASE_HEIGHT;
      // Estimate based on content length
      const contentLength = message.content?.length || 0;
      const estimatedLines = Math.ceil(contentLength / CHARS_PER_LINE);
      return Math.max(BASE_HEIGHT, Math.min(estimatedLines * PIXELS_PER_LINE + BASE_HEIGHT, MAX_HEIGHT));
    };
  }, [messages]);

  // Render individual message row
  const MessageRow = memo(({ index, style }) => {
    const message = messages[index];
    if (!message) return null;

    return (
      <div style={style} className={`message ${message.role} ${message.isError ? 'error' : ''}`}>
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
    );
  });

  MessageRow.displayName = 'MessageRow';

  // Use standard rendering for smaller lists, virtualization for large lists
  const shouldVirtualize = messages.length > VIRTUALIZATION_THRESHOLD;

  return (
    <div className="messages-container">
      {messages.length === 0 && (
        <div className="welcome-message">
          <h2>Welcome to MultiChat</h2>
          <p>Choose your AI model and start chatting!</p>
        </div>
      )}
      
      {shouldVirtualize ? (
        // Virtualized rendering for large lists
        <List
          ref={listRef}
          height={600}
          itemCount={messages.length}
          itemSize={getItemSize}
          width="100%"
          style={{ overflowX: 'hidden' }}
        >
          {MessageRow}
        </List>
      ) : (
        // Standard rendering for smaller lists
        messages.map((message, index) => (
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
        ))
      )}
      
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