import axios from 'axios';

/**
 * Axios instance for making API requests.
 *
 * This instance is configured to use the Next.js API routes as a proxy to the
 * backend, and it includes credentials to handle httpOnly cookies for
 * authentication. It also has a response interceptor to handle 401
 * Unauthorized errors by redirecting to the login page.
 */
const api = axios.create({
  baseURL: '/api',
  withCredentials: true, // Important for sending httpOnly cookies
  headers: {
    'Content-Type': 'application/json',
  },
});

// Response interceptor for handling errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Redirect to login on unauthorized
      if (typeof window !== 'undefined' && !window.location.pathname.includes('/login')) {
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  }
);

export default api;
