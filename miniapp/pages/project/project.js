const app = getApp();
const api = require('../../utils/api');

Page({
  data: {
    projectId: 0,
    project: null,
    nodes: [],
    loading: true,
    generating: false,
    progressPercent: 0,
    selectMode: false,
    selectedNodes: [],
    completedCount: 0,
    hasUnGeneratedNodes: false
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

      // 检查每个节点是否有教材
      const nodes = tree.nodes || [];
      let completedCount = 0;
      let hasUnGeneratedNodes = false;

      for (let i = 0; i < nodes.length; i++) {
        const node = nodes[i];
        if (node.status === 'completed') {
          completedCount++;
        }
        // 检查是否有教材
        try {
          const contents = await api.contents.listByNode(node.id);
          nodes[i].hasContent = contents.items && contents.items.length > 0;
        } catch (e) {
          nodes[i].hasContent = false;
        }
        if (!nodes[i].hasContent) {
          hasUnGeneratedNodes = true;
        }
      }

      this.setData({
        project,
        nodes,
        loading: false,
        completedCount,
        hasUnGeneratedNodes
      });
    } catch (e) {
      console.error('加载项目失败', e);
      this.setData({ loading: false });
      wx.showToast({ title: '加载失败', icon: 'none' });
    }
  },

  async generateTree() {
    if (this.data.generating) return;

    this.setData({ generating: true, progressPercent: 0 });

    // 模拟进度条
    const progressInterval = setInterval(() => {
      const current = this.data.progressPercent;
      if (current < 90) {
        this.setData({ progressPercent: current + 5 });
      }
    }, 1500);

    try {
      await app.request({
        url: `/api/projects/${this.data.projectId}/generate-tree`,
        method: 'POST'
      });

      clearInterval(progressInterval);
      this.setData({ progressPercent: 100, generating: false });
      wx.showToast({ title: '生成成功', icon: 'success' });

      setTimeout(() => {
        this.loadProject();
      }, 500);
    } catch (e) {
      clearInterval(progressInterval);
      this.setData({ generating: false, progressPercent: 0 });
      wx.showToast({ title: '生成失败，请稍后刷新查看', icon: 'none' });
    }
  },

  refreshTree() {
    this.loadProject();
  },

  toggleSelectMode() {
    const selectMode = !this.data.selectMode;
    const nodes = this.data.nodes.map(n => ({ ...n, selected: false }));
    this.setData({
      selectMode,
      nodes,
      selectedNodes: []
    });
  },

  toggleNodeSelect(e) {
    const index = e.currentTarget.dataset.index;
    const nodes = [...this.data.nodes];
    nodes[index].selected = !nodes[index].selected;

    const selectedNodes = nodes.filter(n => n.selected).map(n => n.id);

    this.setData({ nodes, selectedNodes });
  },

  async batchGenerateContent() {
    if (this.data.selectedNodes.length === 0) {
      wx.showToast({ title: '请先选择节点', icon: 'none' });
      return;
    }

    wx.showLoading({ title: `正在生成 ${this.data.selectedNodes.length} 个教材...`, mask: true });

    try {
      const result = await api.contents.batchGenerate(this.data.selectedNodes);
      wx.hideLoading();
      wx.showToast({
        title: `成功生成 ${result.generated} 个教材`,
        icon: 'success'
      });
      this.setData({ selectMode: false, selectedNodes: [] });
      this.loadProject();
    } catch (e) {
      wx.hideLoading();
      wx.showToast({ title: '批量生成失败', icon: 'none' });
    }
  },

  async generateAllContent() {
    const nodeIds = this.data.nodes.map(n => n.id);

    wx.showLoading({ title: `正在生成 ${nodeIds.length} 个教材...`, mask: true });

    try {
      const result = await api.contents.batchGenerate(nodeIds);
      wx.hideLoading();
      wx.showToast({
        title: `成功生成 ${result.generated} 个教材`,
        icon: 'success'
      });
      this.loadProject();
    } catch (e) {
      wx.hideLoading();
      wx.showToast({ title: '批量生成失败', icon: 'none' });
    }
  },

  goToStudy(e) {
    const nodeId = e.currentTarget.dataset.id;
    wx.navigateTo({
      url: `/pages/study/study?id=${nodeId}`
    });
  }
});
