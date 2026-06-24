// pages/chat/chat.js
const api = require('../../utils/api')

Page({
  data: {
    nodeId: null,
    projectId: null,
    messages: [],
    inputValue: '',
    loading: false,
    scrollToView: ''
  },

  onLoad(options) {
    if (options.nodeId) {
      this.setData({ nodeId: options.nodeId })
    }
    if (options.projectId) {
      this.setData({ projectId: options.projectId })
    }
    this.loadHistory()
  },

  async loadHistory() {
    if (!this.data.projectId) return

    try {
      const result = await api.chat.history(this.data.projectId)
      if (result.messages && result.messages.length > 0) {
        const messages = result.messages.map(msg => ({
          role: msg.role,
          content: msg.content,
          time: this.formatTime(new Date())
        }))
        this.setData({ messages })
        this.scrollToBottom()
      }
    } catch (err) {
      console.error('加载历史记录失败', err)
    }
  },

  onInput(e) {
    this.setData({ inputValue: e.detail.value })
  },

  async sendMessage() {
    const content = this.data.inputValue.trim()
    if (!content || this.data.loading) return

    if (!this.data.projectId) {
      wx.showToast({ title: '缺少项目信息', icon: 'none' })
      return
    }

    // 添加用户消息
    const userMsg = {
      role: 'user',
      content,
      time: this.formatTime(new Date())
    }
    this.setData({
      messages: [...this.data.messages, userMsg],
      inputValue: '',
      loading: true
    })
    this.scrollToBottom()

    try {
      const result = await api.chat.send(this.data.projectId, content)

      // 添加 AI 回复
      const assistantMsg = {
        role: 'assistant',
        content: result.reply,
        time: this.formatTime(new Date())
      }
      this.setData({
        messages: [...this.data.messages, assistantMsg],
        loading: false
      })
      this.scrollToBottom()
    } catch (err) {
      console.error('发送消息失败', err)
      wx.showToast({ title: '发送失败', icon: 'error' })
      this.setData({ loading: false })
    }
  },

  scrollToBottom() {
    setTimeout(() => {
      this.setData({
        scrollToView: `msg-${this.data.messages.length - 1}`
      })
    }, 100)
  },

  formatTime(date) {
    const hour = date.getHours().toString().padStart(2, '0')
    const minute = date.getMinutes().toString().padStart(2, '0')
    return `${hour}:${minute}`
  }
})
