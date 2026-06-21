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
    showResult: false,
    result: null
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
      this.setData({ showResult: true, result })
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
