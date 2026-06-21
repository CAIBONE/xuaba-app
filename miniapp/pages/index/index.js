// pages/index/index.js
const app = getApp()
const api = require('../../utils/api')

Page({
  data: {
    userInfo: null,
    studyDays: 0,
    level: 1,
    todayTasks: []
  },

  onLoad() {
    this.checkLogin()
  },

  onShow() {
    if (this.data.userInfo) {
      this.loadData()
    }
  },

  checkLogin() {
    const userInfo = app.globalData.userInfo
    if (userInfo) {
      this.setData({ userInfo })
      this.loadData()
    }
  },

  async onLogin() {
    wx.showLoading({ title: '登录中...' })
    try {
      const result = await app.login()
      this.setData({ userInfo: result.user })
      this.loadData()
      wx.showToast({ title: '登录成功', icon: 'success' })
    } catch (err) {
      wx.showToast({ title: '登录失败', icon: 'error' })
    } finally {
      wx.hideLoading()
    }
  },

  async loadData() {
    // 加载今日任务
    try {
      // TODO: 从后端获取今日任务
      this.setData({
        todayTasks: [],
        studyDays: 7,
        level: 2
      })
    } catch (err) {
      console.error('加载数据失败:', err)
    }
  },

  goToProjects() {
    wx.switchTab({ url: '/pages/projects/projects' })
  },

  goToCreate() {
    wx.navigateTo({ url: '/pages/project-detail/project-detail?mode=create' })
  },

  goToReports() {
    wx.switchTab({ url: '/pages/reports/reports' })
  }
})
