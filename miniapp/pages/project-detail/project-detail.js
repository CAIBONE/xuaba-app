// pages/project-detail/project-detail.js
const api = require('../../utils/api')

Page({
  data: {
    mode: 'create', // create | detail
    projectId: null,
    project: null,
    subject: '',
    goal: '',
    goalTypes: ['技能掌握', '考试通过', '兴趣探索'],
    goalTypeIndex: 0,
    progress: {
      totalNodes: 0,
      completedNodes: 0,
      completionRate: 0
    }
  },

  onLoad(options) {
    if (options.id) {
      this.setData({ mode: 'detail', projectId: options.id })
      this.loadProject(options.id)
    }
  },

  async loadProject(id) {
    wx.showLoading({ title: '加载中...' })
    try {
      const project = await api.projects.get(id)
      this.setData({ project })
    } catch (err) {
      wx.showToast({ title: '加载失败', icon: 'error' })
    } finally {
      wx.hideLoading()
    }
  },

  onSubjectInput(e) {
    this.setData({ subject: e.detail.value })
  },

  onGoalInput(e) {
    this.setData({ goal: e.detail.value })
  },

  onGoalTypeChange(e) {
    this.setData({ goalTypeIndex: e.detail.value })
  },

  async createProject() {
    wx.showLoading({ title: '创建中...' })
    try {
      const goalTypeMap = ['skill', 'exam', 'interest']
      const result = await api.projects.create({
        subject: this.data.subject,
        goal_description: this.data.goal,
        goal_type: goalTypeMap[this.data.goalTypeIndex]
      })
      wx.showToast({ title: '创建成功', icon: 'success' })
      setTimeout(() => {
        wx.redirectTo({ url: `/pages/project-detail/project-detail?id=${result.id}` })
      }, 1000)
    } catch (err) {
      wx.showToast({ title: '创建失败', icon: 'error' })
    } finally {
      wx.hideLoading()
    }
  },

  goToTree() {
    wx.navigateTo({ url: `/pages/knowledge-tree/knowledge-tree?projectId=${this.data.projectId}` })
  },

  async generateContent() {
    wx.showToast({ title: '功能开发中', icon: 'none' })
  }
})
