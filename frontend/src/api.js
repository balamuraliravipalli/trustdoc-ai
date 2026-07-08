import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
})

api.interceptors.request.use((config) => {
  const key = import.meta.env.VITE_APP_API_KEY
  if (key) {
    config.headers['X-API-Key'] = key
  }
  const token = localStorage.getItem('trustdoc_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

export default api
