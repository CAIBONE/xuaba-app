// pages/projects/projects.js
const api = require('../../utils/api')

Page({
  data: {
    projects: [],
    loading: false
  },

  onLoad() {
    this.loadProjects()
  },

  onShow() {
    this.loadProjects()
  },

  async loadProjects() {
    this.setData({ loading: true })
    try {
      const result = await api.projects.list()
      this.setData({
        projects: result.items.map(p => ({
          ...p,
          completionRate: Math.round((p.tree_total_nodes > 0 ? 50 : 0)) // 模拟数据
        }))
      })
    } catch (err) {
      wx.showToast({ title: '加载失败', icon: 'error' })
    } finally {
      this.setData({ loading: false })
    }
  },

  createProject() {
    wx.navigateTo({ url: '/pages/project-detail/project-detail?mode=create' })
  },

  goToDetail(e) {
    const id = e.currentTarget.dataset.id
    wx.navigateTo({ url: `/pages/project-detail/project-detail?id=${id}` })
  }
})
