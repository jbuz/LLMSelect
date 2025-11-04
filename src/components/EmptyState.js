import React, { memo } from 'react';

const EmptyState = memo(({ 
  icon = '📭', 
  title = 'No items yet', 
  description = '', 
  action = null 
}) => {
  return (
    <div className="empty-state" style={{
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      justifyContent: 'center',
      padding: '3rem 1rem',
      textAlign: 'center',
      color: 'var(--text-muted)',
    }}>
      <div style={{
        fontSize: '3rem',
        marginBottom: '1rem',
        opacity: 0.5,
      }}>
        {icon}
      </div>
      <h3 style={{
        fontSize: '1.25rem',
        fontWeight: 600,
        marginBottom: '0.5rem',
        color: 'var(--text-secondary)',
      }}>
        {title}
      </h3>
      {description && (
        <p style={{
          fontSize: '0.875rem',
          marginBottom: action ? '1.5rem' : 0,
          maxWidth: '400px',
        }}>
          {description}
        </p>
      )}
      {action && action}
    </div>
  );
});

EmptyState.displayName = 'EmptyState';

export default EmptyState;
