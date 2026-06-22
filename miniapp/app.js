// app.js
App({
  onLaunch() {
    const token = wx.getStorageSync('token');
    if (!token) {
      this.login();
    }
  },

  globalData: {
    baseUrl: 'http://localhost:8000',
    token: wx.getStorageSync('token') || ''
  },

  login() {
    wx.login({
      success: (res) => {
        wx.request({
          url: `${this.globalData.baseUrl}/api/auth/login`,
          method: 'POST',
          data: { code: res.code },
          success: (resp) => {
            if (resp.data.access_token) {
              this.globalData.token = resp.data.access_token;
              wx.setStorageSync('token', resp.data.access_token);
            }
          }
        });
      }
    });
  },

  request(options) {
    return new Promise((resolve, reject) => {
      wx.request({
        ...options,
        url: `${this.globalData.baseUrl}${options.url}`,
        header: {
          'Authorization': `Bearer ${this.globalData.token}`,
          'Content-Type': 'application/json',
          ...options.header
        },
        success: (res) => {
          if (res.statusCode >= 200 && res.statusCode < 300) {
            resolve(res.data);
          } else {
            reject(res);
          }
        },
        fail: reject
      });
    });
  }
});
