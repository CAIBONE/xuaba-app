// pages/project-detail/project-detail.js
const api = require('../../utils/api')

Page({
  data: {
    mode: 'create', // create | detail | refinement
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
    },
    // 目标梳理对话相关
    conversationHistory: [],
    followUpQuestions: [],
    goalRefinementReady: false,
    refinementInput: '',
    refinedGoal: '',
    baselineLevel: ''
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
    if (!this.data.subject || !this.data.goal) {
      wx.showToast({ title: '请填写科目和目标', icon: 'none' })
      return
    }

    wx.showLoading({ title: '创建中...' })
    try {
      const goalTypeMap = ['skill', 'exam', 'interest']
      const result = await api.projects.create({
        subject: this.data.subject,
        goal_description: this.data.goal,
        goal_type: goalTypeMap[this.data.goalTypeIndex]
      })

      this.setData({
        projectId: result.id,
        project: result,
        mode: 'refinement' // 进入目标梳理模式
      })

      wx.hideLoading()

      // 开始目标梳理
      this.startGoalRefinement()
    } catch (err) {
      wx.hideLoading()
      wx.showToast({ title: '创建失败', icon: 'error' })
    }
  },

  async startGoalRefinement() {
    wx.showLoading({ title: 'AI 正在分析您的目标...' })
    try {
      const result = await api.projects.refineGoal(this.data.projectId, {
        raw_goal: this.data.goal,
        conversation_history: []
      })

      this.setData({
        conversationHistory: [{ role: 'assistant', content: JSON.stringify(result) }],
        followUpQuestions: result.follow_up_questions || [],
        goalRefinementReady: result.ready,
        refinedGoal: result.refined_goal || '',
        baselineLevel: result.baseline_level || ''
      })

      wx.hideLoading()
    } catch (err) {
      wx.hideLoading()
      wx.showToast({ title: '分析失败，请稍后重试', icon: 'error' })
      // 失败时直接进入详情模式
      this.setData({ mode: 'detail' })
    }
  },

  onRefinementInput(e) {
    this.setData({ refinementInput: e.detail.value })
  },

  async answerFollowUp() {
    const answer = this.data.refinementInput.trim()
    if (!answer) {
      wx.showToast({ title: '请输入您的回答', icon: 'none' })
      return
    }

    wx.showLoading({ title: 'AI 正在思考...' })
    try {
      const conversationHistory = [...this.data.conversationHistory]
      conversationHistory.push({ role: 'user', content: answer })

      const result = await api.projects.refineGoal(this.data.projectId, {
        raw_goal: this.data.goal,
        conversation_history: conversationHistory
      })

      conversationHistory.push({ role: 'assistant', content: JSON.stringify(result) })

      this.setData({
        conversationHistory,
        followUpQuestions: result.follow_up_questions || [],
        goalRefinementReady: result.ready,
        refinementInput: '',
        refinedGoal: result.refined_goal || this.data.refinedGoal,
        baselineLevel: result.baseline_level || this.data.baselineLevel
      })

      wx.hideLoading()

      if (result.ready) {
        wx.showToast({ title: '目标梳理完成！', icon: 'success' })
      }
    } catch (err) {
      wx.hideLoading()
      wx.showToast({ title: '回答失败，请重试', icon: 'error' })
    }
  },

  confirmGoalRefinement() {
    this.setData({ mode: 'detail' })
    wx.showToast({ title: '可以开始生成知识图谱了', icon: 'success' })
  },

  skipGoalRefinement() {
    this.setData({ mode: 'detail' })
  },

  goToTree() {
    wx.navigateTo({ url: `/pages/knowledge-tree/knowledge-tree?projectId=${this.data.projectId}` })
  },

  async generateContent() {
    wx.showToast({ title: '功能开发中', icon: 'none' })
  }
})
