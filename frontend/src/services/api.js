import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000
});

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    // Add API key for development
    config.headers['X-API-Key'] = process.env.REACT_APP_API_KEY || 'your_secure_api_key_for_development';
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response) {
      const { status, data } = error.response;
      
      if (status === 401) {
        // Unauthorized - clear token and redirect to login
        localStorage.removeItem('token');
        window.location.href = '/login';
      } else if (status === 429) {
        // Rate limit
        console.error('Rate limit exceeded. Please wait.');
      } else if (status >= 500) {
        console.error('Server error. Please try again later.');
      }
      
      return Promise.reject(error);
    }
    return Promise.reject(error);
  }
);

// API service functions
export const farmerService = {
  getFarmerByPhone: (phone) => api.get(`/api/farmers/${phone}`),
  getFarmerPayments: (farmerId, scheme) => api.get(`/api/farmers/${farmerId}/payments`, { params: { scheme } }),
  getSoilHealth: (farmerId) => api.get(`/api/farmers/${farmerId}/soil-health`),
  searchFarmers: (name) => api.get('/api/farmers/search/by-name', { params: { name } }),
  getDistricts: () => api.get('/api/farmers/districts/list'),
  getStatistics: () => api.get('/api/farmers/statistics/summary')
};

export const queryService = {
  processQuery: (question, phoneNumber, language = 'hi') => 
    api.post('/api/queries/', { question, phone_number: phoneNumber, language }),
  getHistory: (phoneNumber) => api.get('/api/queries/history', { params: { phone_number: phoneNumber } }),
  getIntents: () => api.get('/api/queries/intents'),
  getSampleQueries: () => api.get('/api/queries/sample-queries'),
  submitFeedback: (queryId, rating, comments) => 
    api.post('/api/queries/feedback', { query_id: queryId, rating, comments })
};

export const voiceService = {
  speechToText: (audioBase64, language = 'hi', format = 'wav') =>
    api.post('/api/voice/stt', { audio_base64: audioBase64, language, audio_format: format }),
  textToSpeech: (text, language = 'hi', gender = 'female') =>
    api.post('/api/voice/tts', { text, language, gender }, { responseType: 'blob' }),
  uploadAudio: (audioFile, language = 'hi') => {
    const formData = new FormData();
    formData.append('audio_file', audioFile);
    formData.append('language', language);
    return api.post('/api/voice/stt/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
  },
  initiateCall: (phoneNumber, language = 'hi', message = null) =>
    api.post('/api/voice/call', { phone_number: phoneNumber, language, message }),
  getLanguages: () => api.get('/api/voice/languages')
};

export const dashboardService = {
  getStats: () => api.get('/api/dashboard/stats'),
  getCharts: () => api.get('/api/dashboard/charts'),
  getRecentQueries: (limit = 10) => api.get('/api/dashboard/recent', { params: { limit } })
};

export default api;