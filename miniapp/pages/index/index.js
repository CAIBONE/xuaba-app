const app = getApp();

Page({
  data: {
    projects: [],
    loading: true
  },

  onLoad() {
    this.loadProjects();
  },

  onPullDownRefresh() {
    this.loadProjects().then(() => {
      wx.stopPullDownRefresh();
    });
  },

  async loadProjects() {
    try {
      const resp = await app.request({
        url: '/api/projects',
        method: 'GET'
      });
      this.setData({
        projects: resp.items || [],
        loading: false
      });
    } catch (e) {
      console.error('加载项目失败', e);
      this.setData({ loading: false });
      wx.showToast({ title: '加载失败', icon: 'none' });
    }
  },

  createProject() {
    wx.showModal({
      title: '创建学习项目',
      editable: true,
      placeholderText: '请输入学习目标（如：中级经济师考试）',
      success: async (res) => {
        if (res.confirm && res.content) {
          try {
            await app.request({
              url: '/api/projects',
              method: 'POST',
              data: {
                subject: res.content,
                goal_description: `学习${res.content}`,
                goal_type: 'exam'
              }
            });
            wx.showToast({ title: '创建成功', icon: 'success' });
            this.loadProjects();
          } catch (e) {
            wx.showToast({ title: '创建失败', icon: 'none' });
          }
        }
      }
    });
  },

  goToProject(e) {
    const id = e.currentTarget.dataset.id;
    wx.navigateTo({
      url: `/pages/project/project?id=${id}`
    });
  }
});
