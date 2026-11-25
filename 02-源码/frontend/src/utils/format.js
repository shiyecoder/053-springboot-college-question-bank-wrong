/** 全局时间格式化：全系统统一调用，禁止各页面自行拼接 */
export function formatTime(v, dateOnly = false) {
  if (!v) return '-'
  const s = String(v).replace('T', ' ')
  const m = s.match(/^(\d{4})-(\d{2})-(\d{2})[ ]?(\d{2}):(\d{2}):(\d{2})/)
  if (m) {
    return dateOnly ? `${m[1]}-${m[2]}-${m[3]}` : `${m[1]}-${m[2]}-${m[3]} ${m[4]}:${m[5]}:${m[6]}`
  }
  return s.substring(0, dateOnly ? 10 : 19)
}

export function formatDate(v) {
  return formatTime(v, true)
}

export function percent(v, digits = 1) {
  if (v === null || v === undefined || v === '') return '-'
  return Number(v).toFixed(digits) + '%'
}

export function score(v) {
  if (v === null || v === undefined || v === '') return '0.0'
  return Number(v).toFixed(1)
}

/** 状态 → 中文标签（后端直接存中文，集中在此处便于统一与兜底） */
export const STATUS_TEXT = {
  草稿: '草稿', 待审核: '待审核', 已入库: '已入库', 已停用: '已停用', 已退回: '已退回',
  已发布: '已发布', 使用中: '使用中', 已归档: '已归档', 已驳回: '已驳回',
  进行中: '进行中', 已交卷: '已交卷', 已批阅: '已批阅', 已作废: '已作废',
  未掌握: '未掌握', 复习中: '复习中', 已掌握: '已掌握', 已移除: '已移除',
  已测试: '已测试', 未测: '未测', 基本掌握: '基本掌握', 薄弱: '薄弱', 严重薄弱: '严重薄弱',
  生效中: '生效中', 已完成: '已完成', 部分失败: '部分失败', 执行中: '执行中', 待执行: '待执行', 已失败: '已失败'
}

export function statusText(s) {
  return STATUS_TEXT[s] || s || '-'
}

export function statusType(s) {
  if (['已入库', '已发布', '已掌握', '已完成', '生效中', '通过'].includes(s)) return 'success'
  if (['使用中', '进行中', '已批阅', '复习中'].includes(s)) return 'primary'
  if (['待审核', '薄弱', '未掌握', '部分失败', '执行中', '待执行'].includes(s)) return 'warning'
  if (['已驳回', '已退回', '严重薄弱', '已失败', '已作废'].includes(s)) return 'danger'
  return 'info'
}

/** 掌握度分档对应的颜色（首页/诊断页统一） */
export function masteryColor(v) {
  const n = Number(v)
  if (n >= 85) return '#2B7955'
  if (n >= 70) return '#4B3F72'
  if (n >= 50) return '#E0A458'
  return '#B02A37'
}

export function questionTypeTag(t) {
  return { 单选: 'info', 多选: 'warning', 判断: 'success', 填空: '', 简答: 'danger', 计算: 'danger' }[t] || 'info'
}
