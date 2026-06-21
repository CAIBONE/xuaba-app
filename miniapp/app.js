// app.js
App({
  onLaunch() {
    // 检查登录状态
    this.checkLoginStatus()
  },

  globalData: {
    userInfo: null,
    token: null,
    baseUrl: 'http://localhost:8000/api'  // 开发环境
    // baseUrl: 'https://your-domain.com/api'  // 生产环境
  },

  checkLoginStatus() {
    const token = wx.getStorageSync('token')
    const userInfo = wx.getStorageSync('userInfo')
    if (token && userInfo) {
      this.globalData.token = token
      this.globalData.userInfo = userInfo
    }
  },

  // 登录方法
  login() {
    return new Promise((resolve, reject) => {
      wx.login({
        success: (res) => {
          if (res.code) {
            wx.request({
              url: `${this.globalData.baseUrl}/auth/login`,
              method: 'POST',
              data: { code: res.code },
              success: (response) => {
                if (response.data && response.data.access_token) {
                  this.globalData.token = response.data.access_token
                  this.globalData.userInfo = response.data.user
                  wx.setStorageSync('token', response.data.access_token)
                  wx.setStorageSync('userInfo', response.data.user)
                  resolve(response.data)
                } else {
                  reject(new Error('登录失败'))
                }
              },
              fail: reject
            })
          } else {
            reject(new Error('登录失败：' + res.errMsg))
          }
        },
        fail: reject
      })
    })
  },

  // 登出方法
  logout() {
    this.globalData.token = null
    this.globalData.userInfo = null
    wx.removeStorageSync('token')
    wx.removeStorageSync('userInfo')
  }
})
