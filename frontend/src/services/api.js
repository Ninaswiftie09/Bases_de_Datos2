import axios from 'axios'

export const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE || 'http://localhost:8000',
  timeout: 120000,
})

export function formatError(error) {
  if (error?.response?.data?.detail) return String(error.response.data.detail)
  if (error?.message) return error.message
  return 'Error desconocido'
}

export const getGraphConnected = async () => {
  const response = await fetch("http://localhost:8000/graph/connected");
  return response.json();
};