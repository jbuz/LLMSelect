import http from './http';

export const authApi = {
  register: (data) => http.post('/auth/register', data),
  login: (data) => http.post('/auth/login', data),
  logout: () => http.post('/auth/logout'),
  me: () => http.get('/auth/me'),
  refresh: () => http.post('/auth/refresh')
};

export const chatApi = {
  sendMessage: (data) => http.post('/chat', data),
  compare: (data) => http.post('/compare', data)
};

export const keyApi = {
  save: (keys) => http.post('/keys', keys)
};
