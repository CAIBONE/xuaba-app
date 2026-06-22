const app = getApp();

Page({
  data: {
    nodeId: 0,
    node: null,
    content: null,
    quiz: null,
    loading: true,
    generating: false,
    activeTab: 'lesson'
  },

  onLoad(options) {
    this.setData({ nodeId: parseInt(options.id) });
    this.loadNode();
  },

  async loadNode() {
    try {
      const node = await app.request({
        url: `/api/nodes/${this.data.nodeId}`,
        method: 'GET'
      });
      
      this.setData({ node, loading: false });
      this.loadContent();
    } catch (e) {
      console.error('加载知识点失败', e);
      this.setData({ loading: false });
      wx.showToast({ title: '加载失败', icon: 'none' });
    }
  },

  async loadContent() {
    try {
      const contents = await app.request({
        url: `/api/contents/node/${this.data.nodeId}`,
        method: 'GET'
      });
      
      if (contents.items && contents.items.length > 0) {
        this.setData({ content: contents.items[0] });
      }
    } catch (e) {
      console.error('加载教材失败', e);
    }
  },

  async generateContent() {
    if (this.data.generating) return;
    
    this.setData({ generating: true });
    wx.showLoading({ title: '生成教材中...', mask: true });

    try {
      const content = await app.request({
        url: '/api/contents/generate',
        method: 'POST',
        data: {
          node_id: this.data.nodeId,
          content_type: 'lesson',
          difficulty: 'normal'
        }
      });
      
      wx.hideLoading();
      wx.showToast({ title: '生成成功', icon: 'success' });
      this.setData({ content });
    } catch (e) {
      wx.hideLoading();
      wx.showToast({ title: '生成失败', icon: 'none' });
    } finally {
      this.setData({ generating: false });
    }
  },

  async generateQuiz() {
    if (this.data.generating) return;
    
    this.setData({ generating: true });
    wx.showLoading({ title: '生成测验中...', mask: true });

    try {
      const quiz = await app.request({
        url: '/api/quizzes/generate',
        method: 'POST',
        data: {
          node_id: this.data.nodeId,
          quiz_type: 'post_test',
          question_count: 5
        }
      });
      
      wx.hideLoading();
      wx.showToast({ title: '生成成功', icon: 'success' });
      this.setData({ quiz });
    } catch (e) {
      wx.hideLoading();
      wx.showToast({ title: '生成失败', icon: 'none' });
    } finally {
      this.setData({ generating: false });
    }
  },

  switchTab(e) {
    const tab = e.currentTarget.dataset.tab;
    this.setData({ activeTab: tab });
  }
});
