import api from './api'

export const productService = {
  search: (params) => api.get('/products', { params }),
  getById: (id) => api.get(`/products/${id}`),
  getPriceHistory: (id, params) => api.get(`/products/${id}/price-history`, { params }),
  getReviews: (id, params) => api.get(`/products/${id}/reviews`, { params }),
}
