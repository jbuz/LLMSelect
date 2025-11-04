import { useEffect, useCallback } from 'react';

export const useKeyboardShortcuts = (shortcuts = {}) => {
  const handleKeyDown = useCallback((event) => {
    const { key, ctrlKey, metaKey, shiftKey, altKey } = event;
    const isMac = navigator.platform.toUpperCase().indexOf('MAC') >= 0;
    const modKey = isMac ? metaKey : ctrlKey;

    // Check each shortcut
    Object.entries(shortcuts).forEach(([combo, handler]) => {
      const parts = combo.toLowerCase().split('+');
      const hasCtrl = parts.includes('ctrl') || parts.includes('cmd');
      const hasShift = parts.includes('shift');
      const hasAlt = parts.includes('alt');
      const keyPart = parts[parts.length - 1];

      const modifierMatch = 
        (hasCtrl ? modKey : !modKey) &&
        (hasShift ? shiftKey : !shiftKey) &&
        (hasAlt ? altKey : !altKey);

      const keyMatch = key.toLowerCase() === keyPart;

      if (modifierMatch && keyMatch) {
        event.preventDefault();
        handler(event);
      }
    });
  }, [shortcuts]);

  useEffect(() => {
    document.addEventListener('keydown', handleKeyDown);
    return () => {
      document.removeEventListener('keydown', handleKeyDown);
    };
  }, [handleKeyDown]);
};

export default useKeyboardShortcuts;
