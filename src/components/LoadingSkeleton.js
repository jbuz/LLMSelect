import React, { memo } from 'react';

const LoadingSkeleton = memo(({ 
  width = '100%', 
  height = '1rem', 
  borderRadius = '8px',
  count = 1,
  style = {}
}) => {
  return (
    <>
      {Array.from({ length: count }).map((_, index) => (
        <div
          key={index}
          className="skeleton"
          style={{
            width,
            height,
            borderRadius,
            marginBottom: count > 1 ? '0.5rem' : 0,
            ...style
          }}
          aria-hidden="true"
        />
      ))}
    </>
  );
});

LoadingSkeleton.displayName = 'LoadingSkeleton';

export default LoadingSkeleton;
