// pages/schedule/schedule.js
const api = require('../../utils/api')

Page({
  data: {
    projects: [],
    currentProjectId: null,
    dailyPlan: null,
    loading: false
  },

  onLoad() {
    this.loadProjects()
  },

  async loadProjects() {
    wx.showLoading({ title: '加载中...' })
    try {
      const projects = await api.projects.list()
      this.setData({ projects })
      if (projects.length > 0) {
        this.setData({ currentProjectId: projects[0].id })
        this.loadDailyPlan(projects[0].id)
      }
    } catch (err) {
      wx.showToast({ title: '加载项目失败', icon: 'error' })
    } finally {
      wx.hideLoading()
    }
  },

  onProjectChange(e) {
    const projectId = this.data.projects[e.detail.value].id
    this.setData({ currentProjectId: projectId })
    this.loadDailyPlan(projectId)
  },

  async loadDailyPlan(projectId) {
    this.setData({ loading: true })
    try {
      const plan = await api.schedules.getDailyPlan(projectId, 60)
      this.setData({ dailyPlan: plan })
    } catch (err) {
      wx.showToast({ title: '加载计划失败', icon: 'error' })
    } finally {
      this.setData({ loading: false })
    }
  },

  goToNode(e) {
    const nodeId = e.currentTarget.dataset.nodeId
    wx.navigateTo({
      url: `/pages/content/content?nodeId=${nodeId}`
    })
  }
})
