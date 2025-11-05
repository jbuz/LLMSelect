import axios from 'axios';
import Cookies from 'js-cookie';

const http = axios.create({
  baseURL: '/api/v1',
  timeout: 30000,
  withCredentials: true
});

// Track in-flight requests for deduplication
const pendingRequests = new Map();

// Generate request key for deduplication
function generateRequestKey(config) {
  return `${config.method}:${config.url}:${JSON.stringify(config.params)}`;
}

http.interceptors.request.use((config) => {
  const csrfToken = Cookies.get('csrf_access_token');
  if (csrfToken && !config.headers['X-CSRF-Token']) {
    config.headers['X-CSRF-Token'] = csrfToken;
  }

  // Add AbortController for request cancellation
  if (!config.signal) {
    const controller = new AbortController();
    config.signal = controller.signal;
    config.controller = controller;
  }

  // Request deduplication (skip for mutations like POST/PUT/DELETE)
  if (['get', 'head', 'options'].includes(config.method?.toLowerCase())) {
    const requestKey = generateRequestKey(config);
    
    if (pendingRequests.has(requestKey)) {
      // Return the existing pending request
      return pendingRequests.get(requestKey);
    }
    
    // Store this request as pending
    const requestPromise = Promise.resolve(config);
    pendingRequests.set(requestKey, requestPromise);
    
    // Clean up after request completes
    const cleanup = () => {
      pendingRequests.delete(requestKey);
    };
    
    if (config.signal) {
      config.signal.addEventListener('abort', cleanup);
    }
  }

  return config;
});

http.interceptors.response.use(
  (response) => {
    // Clean up pending request tracking on success
    if (response.config) {
      const requestKey = generateRequestKey(response.config);
      pendingRequests.delete(requestKey);
    }
    return response;
  },
  (error) => {
    // Clean up pending request tracking on error
    if (error.config) {
      const requestKey = generateRequestKey(error.config);
      pendingRequests.delete(requestKey);
    }
    return Promise.reject(error);
  }
);

// Helper to cancel a request
export function cancelRequest(config) {
  if (config && config.controller) {
    config.controller.abort();
  }
}

// Helper to cancel all pending requests
export function cancelAllRequests() {
  pendingRequests.clear();
}

export default http;
