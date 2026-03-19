import api from './api'

export const aiService = {
  predictPrice: (productId, days = 7) =>
    api.get(`/ai/predict-price/${productId}`, { params: { days } }),

  getAnomalies: (limit = 20) =>
    api.get('/ai/anomalies', { params: { limit } }),

  checkReviews: (reviews) =>
    api.post('/ai/check-reviews', { reviews }),
}
