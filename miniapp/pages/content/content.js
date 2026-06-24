// pages/content/content.js
const api = require('../../utils/api')

Page({
  data: {
    nodeId: null,
    content: null,
    estimatedMinutes: 30,
    notes: [],
    newNote: '',
    chatMessages: [],
    showChat: false
  },

  async onLoad(options) {
    if (options.nodeId) {
      this.setData({ nodeId: options.nodeId })
      this.loadContent(options.nodeId)
      this.loadNotes(options.nodeId)
      // 标记为学习中
      try {
        await api.nodes.update(options.nodeId, { status: 'in_progress' })
      } catch (err) {
        console.error('更新状态失败', err)
      }
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

  async loadNotes(nodeId) {
    try {
      const result = await api.notes.listByContent(nodeId)
      this.setData({ notes: result.items || [] })
    } catch (err) {
      console.error('加载笔记失败', err)
    }
  },

  onNoteInput(e) {
    this.setData({ newNote: e.detail.value })
  },

  async addNote() {
    if (!this.data.newNote.trim()) {
      wx.showToast({ title: '请输入笔记内容', icon: 'none' })
      return
    }

    wx.showLoading({ title: '添加中...' })
    try {
      await api.notes.create(this.data.nodeId, {
        note_type: 'note',
        text: this.data.newNote
      })
      this.setData({ newNote: '' })
      await this.loadNotes(this.data.nodeId)
      wx.showToast({ title: '添加成功', icon: 'success' })
    } catch (err) {
      wx.showToast({ title: '添加失败', icon: 'error' })
    } finally {
      wx.hideLoading()
    }
  },

  onTextTap(e) {
    // 文本选中时显示操作菜单
    wx.showActionSheet({
      itemList: ['添加划线', '添加笔记', '提问 AI'],
      success: (res) => {
        if (res.tapIndex === 0) {
          this.addHighlight()
        } else if (res.tapIndex === 1) {
          // 已经在笔记区域添加
        } else if (res.tapIndex === 2) {
          this.askAI()
        }
      }
    })
  },

  async addHighlight() {
    wx.showModal({
      title: '添加划线',
      placeholderText: '选中的文本...',
      editable: true,
      success: async (res) => {
        if (res.confirm && res.content) {
          try {
            await api.notes.create(this.data.nodeId, {
              note_type: 'highlight',
              text: res.content
            })
            await this.loadNotes(this.data.nodeId)
            wx.showToast({ title: '划线成功', icon: 'success' })
          } catch (err) {
            wx.showToast({ title: '添加失败', icon: 'error' })
          }
        }
      }
    })
  },

  openChat() {
    wx.navigateTo({
      url: `/pages/chat/chat?nodeId=${this.data.nodeId}&contentId=${this.data.content?.id}`
    })
  },

  async askAI() {
    wx.showModal({
      title: '提问 AI',
      placeholderText: '输入你的问题...',
      editable: true,
      success: async (res) => {
        if (res.confirm && res.content) {
          wx.showLoading({ title: '思考中...' })
          try {
            const result = await api.chat.send(this.data.nodeId, res.content)
            wx.hideLoading()
            wx.showModal({
              title: 'AI 回答',
              content: result.reply,
              showCancel: false
            })
          } catch (err) {
            wx.hideLoading()
            wx.showToast({ title: '提问失败', icon: 'error' })
          }
        }
      }
    })
  },

  startQuiz() {
    wx.navigateTo({ url: `/pages/quiz/quiz?nodeId=${this.data.nodeId}` })
  },

  async markComplete() {
    wx.showLoading({ title: '提交中...' })
    try {
      await api.nodes.update(this.data.nodeId, {
        status: 'completed',
        mastery_level: 0.8
      })
      wx.hideLoading()
      wx.showToast({ title: '已标记完成', icon: 'success' })
      setTimeout(() => wx.navigateBack(), 1000)
    } catch (err) {
      wx.hideLoading()
      wx.showToast({ title: '提交失败', icon: 'error' })
    }
  }
})
