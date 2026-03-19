import api from './api'

export const alertService = {
  create: (data) => api.post('/alerts/create', data),
  list: (email, params) => api.get('/alerts', { params: { email, ...params } }),
  delete: (id) => api.delete(`/alerts/${id}`),
}
