// Frontend Configuration
// This file handles environment-specific configuration

const config = {
  // API Configuration
  apiUrl: process.env.REACT_APP_API_URL || 'http://localhost:5000/api',
  
  // Environment
  environment: process.env.REACT_APP_ENV || 'development',
  
  // App Configuration
  appName: process.env.REACT_APP_APP_NAME || 'SBC Document Processor',
  version: process.env.REACT_APP_VERSION || '1.0.0',
  
  // Feature Flags
  enableDebug: process.env.REACT_APP_ENABLE_DEBUG === 'true',
  enableLogging: process.env.REACT_APP_ENABLE_LOGGING === 'true',
  
  // Dynamic API URL based on environment
  getApiUrl: () => {
    // For production, use the current domain
    if (process.env.NODE_ENV === 'production') {
      // If REACT_APP_API_URL is set, use it
      if (process.env.REACT_APP_API_URL) {
        return process.env.REACT_APP_API_URL;
      }
      
      // Otherwise, use the same domain as the frontend
      const protocol = window.location.protocol;
      const hostname = window.location.hostname;
      const port = window.location.port ? `:${window.location.port}` : '';
      
      // If frontend is on a different port, assume backend is on port 5000
      if (port && port !== ':3000') {
        return `${protocol}//${hostname}:5000/api`;
      }
      
      // Default to same domain
      return `${protocol}//${hostname}/api`;
    }
    
    // For development, use localhost:5000
    return process.env.REACT_APP_API_URL || 'http://localhost:5000/api';
  }
};

export default config;
