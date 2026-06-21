// pages/knowledge-tree/knowledge-tree.js
const api = require('../../utils/api')

Page({
  data: {
    projectId: null,
    nodes: [],
    totalHours: 0
  },

  onLoad(options) {
    if (options.projectId) {
      this.setData({ projectId: options.projectId })
      this.loadTree(options.projectId)
    }
  },

  async loadTree(projectId) {
    wx.showLoading({ title: '加载中...' })
    try {
      const result = await api.nodes.getTree(projectId)
      this.setData({
        nodes: result.nodes,
        totalHours: result.total_hours
      })
    } catch (err) {
      wx.showToast({ title: '加载失败', icon: 'error' })
    } finally {
      wx.hideLoading()
    }
  },

  selectNode(e) {
    const nodeId = e.currentTarget.dataset.id
    wx.navigateTo({ url: `/pages/content/content?nodeId=${nodeId}` })
  }
})
