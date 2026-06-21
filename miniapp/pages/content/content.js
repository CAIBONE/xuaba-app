// pages/content/content.js
const api = require('../../utils/api')

Page({
  data: {
    nodeId: null,
    content: null,
    estimatedMinutes: 30
  },

  onLoad(options) {
    if (options.nodeId) {
      this.setData({ nodeId: options.nodeId })
      this.loadContent(options.nodeId)
    }
  },

  async loadContent(nodeId) {
    wx.showLoading({ title: '加载中...' })
    try {
      const result = await api.contents.listByNode(nodeId)
      if (result.items && result.items.length > 0) {
        this.setData({ content: result.items[0] })
      }
    } catch (err) {
      wx.showToast({ title: '加载失败', icon: 'error' })
    } finally {
      wx.hideLoading()
    }
  },

  startQuiz() {
    wx.navigateTo({ url: `/pages/quiz/quiz?nodeId=${this.data.nodeId}` })
  },

  markComplete() {
    wx.showToast({ title: '已标记完成', icon: 'success' })
    setTimeout(() => wx.navigateBack(), 1000)
  }
})
