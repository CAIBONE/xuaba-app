// utils/request.js

const app = getApp()

/**
 * 封装请求方法
 */
function request(options) {
  const { url, method = 'GET', data, header = {} } = options

  // 添加 token
  if (app.globalData.token) {
    header['Authorization'] = `Bearer ${app.globalData.token}`
  }

  return new Promise((resolve, reject) => {
    wx.request({
      url: `${app.globalData.baseUrl}${url}`,
      method,
      data,
      header: {
        'Content-Type': 'application/json',
        ...header
      },
      success: (res) => {
        if (res.statusCode === 200 || res.statusCode === 201) {
          resolve(res.data)
        } else if (res.statusCode === 401) {
          // token 过期，重新登录
          app.login().then(() => {
            // 重试请求
            request(options).then(resolve).catch(reject)
          }).catch(reject)
        } else {
          reject(new Error(res.data.detail || '请求失败'))
        }
      },
      fail: (err) => {
        reject(err)
      }
    })
  })
}

// 便捷方法
const get = (url, data) => request({ url, method: 'GET', data })
const post = (url, data) => request({ url, method: 'POST', data })
const put = (url, data) => request({ url, method: 'PUT', data })
const del = (url) => request({ url, method: 'DELETE' })

module.exports = {
  request,
  get,
  post,
  put,
  del
}
