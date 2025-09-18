import axios from 'axios';

const axiosInstance = axios.create({
  baseURL: 'http://localhost:8000/api/', // <--- use localhost, not 127.0.0.1
  withCredentials: true,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add request interceptor to automatically include CSRF token
axiosInstance.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem("token"); // sliding token
    if (token) {
      config.headers["Authorization"] = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Add response interceptor to handle CSRF errors
axiosInstance.interceptors.response.use(
  (response) => {
    // Check for refreshed token in response headers
    const newToken = response.headers['x-refreshed-token'];
    if (newToken) {
      localStorage.setItem("token", newToken);
    }
    return response;
  },
  async (error) => {
    // Check if this is a specific endpoint where 403 is expected for executives
    const isExecutiveEndpoint = error.config?.url?.includes('form-data') || 
                               error.config?.url?.includes('create') || 
                               error.config?.url?.includes('edit') ||
                               error.config?.url?.includes('submit');
    
    // Only logout on 401 (unauthorized) or 403 (forbidden) on non-executive endpoints
    if (error.response?.status === 401 || 
        (error.response?.status === 403 && !isExecutiveEndpoint)) {
      // Session expired or access denied on protected endpoints — clear any local state & redirect
      localStorage.removeItem('isLoggedIn');
      localStorage.removeItem("token");
      window.location.href = "/signin";
      return;
    }

    // For 403 errors on executive endpoints, don't logout but let the component handle the error
    if (error.response?.status === 403 && isExecutiveEndpoint) {
      // This is expected for executive users, don't logout
      console.log('Access denied on executive endpoint:', error.config?.url);
      return Promise.reject(error);
    }

    // if (error.response?.status === 403 && error.response?.data?.detail?.includes('CSRF')) {
    //   // Try to get a new CSRF token
    //   try {
    //     await axiosInstance.get('get-csrf/');
    //     await axios.get('http://127.0.0.1:8000/api/get-csrf/', {
    //       withCredentials: true
    //     });
    //     // Retry the original request
    //     const originalRequest = error.config;
    //     const match = document.cookie.match(/csrftoken=([^;]+)/);
    //     const csrfToken = match ? match[1] : null;
    //     if (csrfToken) {
    //       originalRequest.headers['X-CSRFToken'] = csrfToken;
    //     }
    //     return axiosInstance(originalRequest);
    //   } catch (csrfError) {
    //     console.error('Failed to get CSRF token:', csrfError);
    //   }
    // }
    return Promise.reject(error);
  }
);

export default axiosInstance;