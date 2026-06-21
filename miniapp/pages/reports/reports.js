// pages/reports/reports.js
const api = require('../../utils/api')

Page({
  data: {
    progress: null,
    heatmap: null,
    heatmapDays: [],
    weakNodes: []
  },

  onLoad() {
    this.loadData()
  },

  async loadData() {
    wx.showLoading({ title: '加载中...' })
    try {
      // 加载热力图
      const heatmap = await api.reports.heatmap(90)
      this.setData({
        heatmap,
        heatmapDays: heatmap.days.slice(-42) // 最近 42 天
      })

      // TODO: 加载其他报表数据
      this.setData({
        progress: { total_nodes: 20, completed_nodes: 8, completion_rate: 40 },
        weakNodes: []
      })
    } catch (err) {
      console.error('加载报表失败:', err)
    } finally {
      wx.hideLoading()
    }
  }
})
