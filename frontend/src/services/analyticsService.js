import api from './api'

export const analyticsService = {
  getTrending: (params) => api.get('/analytics/trending', { params }),
  getPriceComparison: (params) => api.get('/analytics/price-comparison', { params }),
  getMarketOverview: () => api.get('/analytics/market-overview'),
  getCategoryInsights: (categoryId) => api.get(`/analytics/category-insights/${categoryId}`),
}
