import axios from 'axios'
import { ElMessage } from 'element-plus'
import router from '@/router'

/** 统一请求：自动带 token，按业务码分流（401 跳登录，其余弹提示） */
const service = axios.create({ baseURL: '', timeout: 30000 })

service.interceptors.request.use((cfg) => {
  const token = localStorage.getItem('qb_token')
  if (token) cfg.headers.Authorization = 'Bearer ' + token
  return cfg
})

service.interceptors.response.use(
  (res) => {
    const body = res.data
    if (body && typeof body.code !== 'undefined') {
      if (body.code === 0) return body.data
      if (body.code === 401 || body.code === 4010) {
        localStorage.removeItem('qb_token')
        localStorage.removeItem('qb_user')
        router.push('/login')
        ElMessage.error(body.msg || '登录已过期，请重新登录')
        return Promise.reject(new Error(body.msg))
      }
      ElMessage.error(body.msg || '请求失败')
      return Promise.reject(new Error(body.msg || '请求失败'))
    }
    return body
  },
  (err) => {
    if (err.response && err.response.status === 401) {
      localStorage.removeItem('qb_token')
      router.push('/login')
    }
    ElMessage.error(err.message || '网络异常')
    return Promise.reject(err)
  }
)

export default service
