import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 90000, // 90s — AI calls can take time
})

export const getLeads = (params) => api.get('/leads', { params })
export const getLeadsMeta = () => api.get('/leads/meta')
export const searchLeads = (query) => api.post('/leads/search', { query })
export const getLead = (id) => api.get(`/leads/${id}`)
export const getIntelligence = (id) => api.get(`/leads/${id}/intelligence`)
export const getStrategy = (id) => api.get(`/leads/${id}/strategy`)
export const getEmailVariants = (id) => api.get(`/leads/${id}/emails`)
export const getFunnel = () => api.get('/analytics/funnel')
export const getPerformance = () => api.get('/analytics/performance')
export const getAnalyticsReport = () => api.get('/analytics/report')

export default api
