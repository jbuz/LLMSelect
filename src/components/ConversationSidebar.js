import React, { useState, useCallback } from 'react';
import ConversationItem from './ConversationItem';

export default function ConversationSidebar({
  conversations,
  activeConversationId,
  onSelectConversation,
  onNewConversation,
  onRenameConversation,
  onDeleteConversation,
  onExportConversation,
  onSearch,
  isOpen,
  onToggle
}) {
  const [searchQuery, setSearchQuery] = useState('');

  const handleSearchChange = useCallback((e) => {
    const query = e.target.value;
    setSearchQuery(query);
    // Debounce search
    if (onSearch) {
      onSearch(query);
    }
  }, [onSearch]);

  return (
    <aside className={`conversation-sidebar ${isOpen ? 'open' : 'closed'}`}>
      <div className="sidebar-header">
        <button 
          onClick={onToggle} 
          className="toggle-btn" 
          aria-label="Toggle sidebar"
        >
          {isOpen ? '◀' : '▶'}
        </button>
        <button 
          onClick={onNewConversation} 
          className="new-conversation-btn"
        >
          ➕ New Chat
        </button>
      </div>
      
      <div className="search-box">
        <input 
          type="search" 
          placeholder="Search conversations..."
          value={searchQuery}
          onChange={handleSearchChange}
          aria-label="Search conversations"
        />
      </div>
      
      <div className="conversation-list">
        {conversations.length === 0 ? (
          <div className="empty-state">
            <p>No conversations yet</p>
          </div>
        ) : (
          conversations.map(conv => (
            <ConversationItem
              key={conv.id}
              conversation={conv}
              isActive={conv.id === activeConversationId}
              onSelect={() => onSelectConversation(conv.id)}
              onRename={(newTitle) => onRenameConversation(conv.id, newTitle)}
              onDelete={() => onDeleteConversation(conv.id)}
              onExport={() => onExportConversation(conv.id)}
            />
          ))
        )}
      </div>
    </aside>
  );
}
