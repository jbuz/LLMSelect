import React, { useState, useRef, useEffect } from 'react';

/**
 * Format relative time for conversation timestamps
 */
function formatRelativeTime(isoString) {
  const date = new Date(isoString);
  const now = new Date();
  const diffMs = now - date;
  const diffMins = Math.floor(diffMs / 60000);
  const diffHours = Math.floor(diffMins / 60);
  const diffDays = Math.floor(diffHours / 24);
  
  if (diffMins < 1) return 'Just now';
  if (diffMins < 60) return `${diffMins}m ago`;
  if (diffHours < 24) return `${diffHours}h ago`;
  if (diffDays < 7) return `${diffDays}d ago`;
  return date.toLocaleDateString();
}

export default function ConversationItem({
  conversation,
  isActive,
  onSelect,
  onRename,
  onDelete,
  onExport
}) {
  const [isEditing, setIsEditing] = useState(false);
  const [title, setTitle] = useState(conversation.title);
  const [showMenu, setShowMenu] = useState(false);
  const menuRef = useRef(null);

  // Close menu when clicking outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (menuRef.current && !menuRef.current.contains(event.target)) {
        setShowMenu(false);
      }
    };

    if (showMenu) {
      document.addEventListener('mousedown', handleClickOutside);
      return () => {
        document.removeEventListener('mousedown', handleClickOutside);
      };
    }
  }, [showMenu]);

  const handleStartEdit = () => {
    setIsEditing(true);
    setShowMenu(false);
  };

  const handleSaveEdit = () => {
    if (title.trim() && title !== conversation.title) {
      onRename(title.trim());
    }
    setIsEditing(false);
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter') {
      handleSaveEdit();
    } else if (e.key === 'Escape') {
      setTitle(conversation.title);
      setIsEditing(false);
    }
  };

  const toggleMenu = (e) => {
    e.stopPropagation();
    setShowMenu(!showMenu);
  };

  const handleRename = (e) => {
    e.stopPropagation();
    handleStartEdit();
  };

  const handleExport = (e) => {
    e.stopPropagation();
    onExport();
    setShowMenu(false);
  };

  const handleDelete = (e) => {
    e.stopPropagation();
    onDelete();
    setShowMenu(false);
  };

  const handleDoubleClick = (e) => {
    e.stopPropagation();
    if (!isEditing) {
      handleStartEdit();
    }
  };

  return (
    <div 
      className={`conversation-item ${isActive ? 'active' : ''}`}
      onClick={onSelect}
      onDoubleClick={handleDoubleClick}
    >
      {isEditing ? (
        <input
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          onBlur={handleSaveEdit}
          onKeyDown={handleKeyDown}
          autoFocus
          className="title-edit"
          onClick={(e) => e.stopPropagation()}
        />
      ) : (
        <>
          <div className="conversation-header">
            <div className="conversation-title">{conversation.title}</div>
            <button 
              className="menu-btn"
              onClick={toggleMenu}
              aria-label="Conversation actions"
            >
              ⋮
            </button>
          </div>
          
          <div className="conversation-meta">
            <span className="provider-badge">{conversation.provider}</span>
            <span className="timestamp">{formatRelativeTime(conversation.lastMessageAt)}</span>
          </div>
          
          {conversation.preview && (
            <div className="conversation-preview">{conversation.preview}</div>
          )}
          
          {showMenu && (
            <div className="context-menu" ref={menuRef} onClick={(e) => e.stopPropagation()}>
              <button onClick={handleRename}>✏️ Rename</button>
              <button onClick={handleExport}>📥 Export</button>
              <button onClick={handleDelete} className="danger">🗑️ Delete</button>
            </div>
          )}
        </>
      )}
    </div>
  );
}
