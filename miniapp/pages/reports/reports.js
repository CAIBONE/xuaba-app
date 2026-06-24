// pages/reports/reports.js
const api = require('../../utils/api')

Page({
  data: {
    projects: [],
    currentProjectId: null,
    progress: null,
    heatmap: null,
    heatmapDays: [],
    weakNodes: [],
    forgetting: null
  },

  onLoad() {
    this.loadProjects()
  },

  async loadProjects() {
    try {
      const projects = await api.projects.list()
      if (projects.length > 0) {
        this.setData({
          projects,
          currentProjectId: projects[0].id
        })
        this.loadData(projects[0].id)
      }
    } catch (err) {
      console.error('加载项目列表失败:', err)
    }
  },

  onProjectChange(e) {
    const projectId = this.data.projects[e.detail.value].id
    this.setData({ currentProjectId: projectId })
    this.loadData(projectId)
  },

  async loadData(projectId) {
    wx.showLoading({ title: '加载中...' })
    try {
      // 并行加载所有报表数据
      const [progress, heatmap, weakNodes, forgetting] = await Promise.all([
        api.reports.progress(projectId),
        api.reports.heatmap(90),
        api.reports.weakNodes(projectId),
        api.reports.forgetting(projectId)
      ])

      this.setData({
        progress,
        heatmap,
        heatmapDays: heatmap.days.slice(-42), // 最近 42 天
        weakNodes: weakNodes.weak_nodes,
        forgetting
      })
    } catch (err) {
      console.error('加载报表失败:', err)
      wx.showToast({ title: '加载失败', icon: 'none' })
    } finally {
      wx.hideLoading()
    }
  }
})
