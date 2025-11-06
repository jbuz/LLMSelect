import React, { Suspense, lazy } from 'react';
import { AuthProvider, AppProvider, ChatProvider } from './contexts';
import AppLayout from './components/AppLayout';
import './styles.css';

// Lazy load pages and heavy components
const ChatMode = lazy(() => import('./pages/ChatMode'));
const ComparisonMode = lazy(() => import('./components/ComparisonMode'));
const ComparisonHistory = lazy(() => import('./components/ComparisonHistory'));

// Loading fallback
const LoadingFallback = () => (
  <div style={{ 
    display: 'flex', 
    alignItems: 'center', 
    justifyContent: 'center', 
    padding: '2rem',
    color: '#666'
  }}>
    Loading...
  </div>
);

const App = () => {
  return (
    <AuthProvider>
      <AppProvider>
        <ChatProvider>
          <Suspense fallback={<LoadingFallback />}>
            <AppLayout>
              {/* AppLayout handles routing and mode switching */}
            </AppLayout>
          </Suspense>
        </ChatProvider>
      </AppProvider>
    </AuthProvider>
  );
};

export default App;
