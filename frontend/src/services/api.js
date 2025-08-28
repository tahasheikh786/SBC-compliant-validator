import axios from 'axios';
import config from '../config';

const api = axios.create({
  baseURL: config.getApiUrl(),
  headers: {
    'Content-Type': 'application/json',
  },
});

export const uploadFile = async (file) => {
  const formData = new FormData();
  formData.append('file', file);
  
  const response = await api.post('/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  
  return response.data;
};

export const getRecords = async () => {
  const response = await api.get('/records');
  return response.data;
};

export const deleteRecord = async (recordId) => {
  const response = await api.delete(`/records/${recordId}`);
  return response.data;
};

export const healthCheck = async () => {
  const response = await api.get('/health');
  return response.data;
};

export default api;
