import api from './api'

export const systemService = {
  getHealth: () => api.get('/health'),
  getSystemStats: () => api.get('/stats/system'),
  getCrawlLogs: () => api.get('/stats/crawl'),
}
