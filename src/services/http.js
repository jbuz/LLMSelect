import axios from 'axios';
import Cookies from 'js-cookie';

const http = axios.create({
  baseURL: '/api/v1',
  timeout: 30000,
  withCredentials: true
});

http.interceptors.request.use((config) => {
  const csrfToken = Cookies.get('csrf_access_token');
  if (csrfToken && !config.headers['X-CSRF-Token']) {
    config.headers['X-CSRF-Token'] = csrfToken;
  }
  return config;
});

export default http;
