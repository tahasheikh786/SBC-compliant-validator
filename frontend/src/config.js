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
    // For production, use the Render backend URL
    if (process.env.NODE_ENV === 'production') {
      // If REACT_APP_API_URL is set, use it
      if (process.env.REACT_APP_API_URL) {
        return process.env.REACT_APP_API_URL;
      }
      
      // Default to Render backend URL
      return 'https://sbc-compliant-validator.onrender.com/api';
    }
    
    // For development, use localhost:5000
    return process.env.REACT_APP_API_URL || 'http://localhost:5000/api';
  }
};

export default config;
