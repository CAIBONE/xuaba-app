// pages/quiz/quiz.js
const api = require('../../utils/api')

Page({
  data: {
    nodeId: null,
    quizId: null,
    questions: [],
    currentIndex: 0,
    currentQuestion: null,
    selectedAnswer: null,
    answers: [],
    feedback: {},
    showResult: false,
    result: null,
    feedbackCount: 0,
    feedbackStats: {
      confused: 0,
      familiar: 0,
      unclear: 0
    }
  },

  onLoad(options) {
    if (options.nodeId) {
      this.setData({ nodeId: options.nodeId })
      this.generateQuiz(options.nodeId)
    }
  },

  async generateQuiz(nodeId) {
    wx.showLoading({ title: '生成测验...' })
    try {
      const result = await api.quizzes.generate({ node_id: nodeId, question_count: 5 })
      this.setData({
        quizId: result.id,
        questions: result.questions,
        currentQuestion: result.questions[0]
      })
    } catch (err) {
      wx.showToast({ title: '生成失败', icon: 'error' })
    } finally {
      wx.hideLoading()
    }
  },

  selectAnswer(e) {
    const index = e.currentTarget.dataset.index
    this.setData({ selectedAnswer: index })
    const answers = [...this.data.answers]
    answers[this.data.currentIndex] = index
    this.setData({ answers })
  },

  setFeedback(e) {
    const type = e.currentTarget.dataset.type
    const feedback = { ...this.data.feedback }
    feedback[this.data.currentIndex] = type
    this.setData({ feedback })
    this.updateFeedbackStats()
  },

  updateFeedbackStats() {
    const feedback = this.data.feedback
    const stats = {
      confused: 0,
      familiar: 0,
      unclear: 0
    }
    Object.values(feedback).forEach(type => {
      if (stats[type] !== undefined) {
        stats[type]++
      }
    })
    this.setData({
      feedbackStats: stats,
      feedbackCount: Object.keys(feedback).length
    })
  },

  prevQuestion() {
    if (this.data.currentIndex > 0) {
      const newIndex = this.data.currentIndex - 1
      this.setData({
        currentIndex: newIndex,
        currentQuestion: this.data.questions[newIndex],
        selectedAnswer: this.data.answers[newIndex] || null
      })
    }
  },

  nextQuestion() {
    if (this.data.currentIndex < this.data.questions.length - 1) {
      const newIndex = this.data.currentIndex + 1
      this.setData({
        currentIndex: newIndex,
        currentQuestion: this.data.questions[newIndex],
        selectedAnswer: this.data.answers[newIndex] || null
      })
    }
  },

  async submitQuiz() {
    wx.showLoading({ title: '提交中...' })
    try {
      const answers = this.data.answers.map((a, i) => ({
        question_index: i,
        answer: String.fromCharCode(65 + a)
      }))
      const result = await api.quizzes.submit(this.data.quizId, { answers })
      this.updateFeedbackStats()
      this.setData({ showResult: true, result })
    } catch (err) {
      wx.showToast({ title: '提交失败', icon: 'error' })
    } finally {
      wx.hideLoading()
    }
  },

  async submitFeedback() {
    if (this.data.feedbackCount === 0) {
      wx.showToast({ title: '没有反馈可提交', icon: 'none' })
      return
    }

    wx.showLoading({ title: '提交反馈...' })
    try {
      // 转换反馈格式：{0: 'confused', 1: 'familiar'} -> {'question_0': 'confused', 'question_1': 'familiar'}
      const feedbackData = {}
      Object.entries(this.data.feedback).forEach(([index, type]) => {
        feedbackData[`question_${index}`] = type
      })

      await api.quizzes.feedback(this.data.quizId, feedbackData)
      wx.showToast({ title: '反馈已提交', icon: 'success' })

      setTimeout(() => {
        this.setData({ showResult: false })
        wx.navigateBack()
      }, 1500)
    } catch (err) {
      wx.showToast({ title: '提交失败', icon: 'error' })
    } finally {
      wx.hideLoading()
    }
  },

  goBack() {
    wx.navigateBack()
  }
})
