// utils/api.js

const { get, post, put, del } = require('./request')

// 用户相关
const auth = {
  login: (code) => post('/auth/login', { code }),
  getMe: () => get('/auth/me'),
  updateProfile: (data) => put('/auth/profile', data)
}

// 项目相关
const projects = {
  list: (params) => get('/projects', params),
  get: (id) => get(`/projects/${id}`),
  create: (data) => post('/projects', data),
  update: (id, data) => put(`/projects/${id}`, data),
  delete: (id) => del(`/projects/${id}`),
  generateTree: (id) => post(`/projects/${id}/generate-tree`),
  generatePlan: (id, data) => post(`/projects/${id}/generate-plan`, data),
  refineGoal: (id, data) => post(`/projects/${id}/refine-goal`, data)
}

// 节点相关
const nodes = {
  listByProject: (projectId) => get(`/nodes/project/${projectId}`),
  getTree: (projectId) => get(`/nodes/project/${projectId}/tree`),
  get: (id) => get(`/nodes/${id}`),
  update: (id, data) => put(`/nodes/${id}`, data)
}

// 教材相关
const contents = {
  listByNode: (nodeId) => get(`/contents/node/${nodeId}`),
  get: (id) => get(`/contents/${id}`),
  generate: (data) => post('/contents/generate', data),
  batchGenerate: (nodeIds, contentType = 'lesson') => post('/contents/batch-generate', { node_ids: nodeIds, content_type: contentType }),
  push: (id, data) => post(`/contents/${id}/push`, data)
}

// 测验相关
const quizzes = {
  get: (id) => get(`/quizzes/${id}`),
  generate: (data) => post('/quizzes/generate', data),
  submit: (id, data) => post(`/quizzes/${id}/submit`, data),
  feedback: (id, data) => post(`/quizzes/${id}/feedback`, data)
}

// 笔记相关
const notes = {
  listByContent: (contentId) => get(`/contents/${contentId}/notes`),
  create: (contentId, data) => post(`/contents/${contentId}/notes`, data),
  delete: (id) => del(`/notes/${id}`)
}

// 对话相关
const chat = {
  send: (projectId, message) => post(`/chat/${projectId}`, { message }),
  history: (projectId) => get(`/chat/${projectId}/history`)
}

// 报表相关
const reports = {
  progress: (projectId) => get(`/reports/progress/${projectId}`),
  mastery: (projectId, nodeId) => get(`/reports/mastery/${projectId}/${nodeId}`),
  heatmap: (days = 365) => get('/reports/heatmap', { days }),
  forgetting: (projectId) => get(`/reports/forgetting/${projectId}`),
  weakNodes: (projectId, threshold = 0.6) => get(`/reports/weak-nodes/${projectId}`, { threshold })
}

// 学习计划相关
const schedules = {
  getDailyPlan: (projectId, dailyMinutes = 60) => get(`/schedules/daily-plan/${projectId}`, { daily_minutes: dailyMinutes })
}

module.exports = {
  auth,
  projects,
  nodes,
  contents,
  quizzes,
  notes,
  chat,
  reports,
  schedules
}
