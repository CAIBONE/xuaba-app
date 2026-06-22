const app = getApp();

Page({
  data: {
    projectId: 0,
    project: null,
    nodes: [],
    loading: true,
    generating: false
  },

  onLoad(options) {
    this.setData({ projectId: parseInt(options.id) });
    this.loadProject();
  },

  async loadProject() {
    try {
      const project = await app.request({
        url: `/api/projects/${this.data.projectId}`,
        method: 'GET'
      });
      
      const tree = await app.request({
        url: `/api/nodes/project/${this.data.projectId}/tree`,
        method: 'GET'
      });

      this.setData({
        project,
        nodes: tree.nodes || [],
        loading: false
      });
    } catch (e) {
      console.error('加载项目失败', e);
      this.setData({ loading: false });
      wx.showToast({ title: '加载失败', icon: 'none' });
    }
  },

  async generateTree() {
    if (this.data.generating) return;
    
    this.setData({ generating: true });
    wx.showLoading({ title: '生成知识图谱中...', mask: true });

    try {
      await app.request({
        url: `/api/projects/${this.data.projectId}/generate-tree`,
        method: 'POST'
      });
      
      wx.hideLoading();
      wx.showToast({ title: '生成成功', icon: 'success' });
      this.loadProject();
    } catch (e) {
      wx.hideLoading();
      wx.showToast({ title: '生成失败', icon: 'none' });
    } finally {
      this.setData({ generating: false });
    }
  },

  goToStudy(e) {
    const nodeId = e.currentTarget.dataset.id;
    wx.navigateTo({
      url: `/pages/study/study?id=${nodeId}`
    });
  }
});
