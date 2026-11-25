<template>
  <div>
    <el-tabs v-model="tab">
      <el-tab-pane label="公告管理" name="notice">
        <div class="card">
          <div class="card-h"><h2>公告列表</h2>
            <span style="margin-left: auto"><el-button type="primary" size="small" @click="openAdd">发布公告</el-button></span>
          </div>
          <el-table :data="notices" border style="width: 100%">
            <el-table-column prop="title" label="标题" min-width="260" show-overflow-tooltip />
            <el-table-column prop="content" label="内容" min-width="320" show-overflow-tooltip />
            <el-table-column label="发布时间" width="170">
              <template #default="{ row }"><span class="num">{{ formatTime(row.publishTime) }}</span></template>
            </el-table-column>
            <el-table-column label="状态" width="90">
              <template #default="{ row }">
                <el-tag size="small" :type="row.status === 1 ? 'success' : 'info'">{{ row.status === 1 ? '已发布' : '草稿' }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="110">
              <template #default="{ row }">
                <el-button link type="danger" @click="remove(row)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </el-tab-pane>
      <el-tab-pane label="我的消息" name="message">
        <div class="card">
          <div class="card-h"><h2>站内消息</h2><span class="sub">待办、审核、超时提醒</span></div>
          <div v-for="m in messages" :key="m.id" class="msg" :class="{ unread: m.readFlag === 0 }">
            <div style="display: flex; justify-content: space-between">
              <b>{{ m.title }}</b>
              <span class="muted num">{{ formatTime(m.createTime) }}</span>
            </div>
            <div class="muted" style="margin-top: 5px">{{ m.content }}</div>
          </div>
          <el-empty v-if="!messages.length" description="暂无站内消息" />
        </div>
      </el-tab-pane>
    </el-tabs>

    <el-dialog v-model="dialog" title="发布公告" width="600px">
      <el-form label-width="80px">
        <el-form-item label="标题"><el-input v-model="form.title" /></el-form-item>
        <el-form-item label="内容"><el-input v-model="form.content" type="textarea" :rows="4" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialog = false">取消</el-button>
        <el-button type="primary" @click="save">发布</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import request from '@/utils/request'
import { formatTime } from '@/utils/format'

const tab = ref('notice')
const notices = ref([])
const messages = ref([])
const dialog = ref(false)
const form = ref({})

async function load() {
  const n = await request.get('/api/notice/page', { params: { page: 1, size: 20 } })
  notices.value = n.list || []
  const user = JSON.parse(localStorage.getItem('qb_user') || '{}')
  const m = await request.get('/api/message/page', { params: { page: 1, size: 20, receiverId: user.id } })
  messages.value = m.list || []
}
function openAdd() { form.value = { status: 1 }; dialog.value = true }

async function save() {
  if (!form.value.title) return ElMessage.warning('请填写标题')
  await request.post('/api/notice', { ...form.value, publishTime: new Date().toISOString().slice(0, 19).replace('T', ' ') })
  ElMessage.success('公告已发布')
  dialog.value = false
  load()
}

async function remove(row) {
  await ElMessageBox.confirm('确认删除该公告？', '删除确认', { type: 'warning' })
  await request.delete('/api/notice/' + row.id)
  ElMessage.success('已删除')
  load()
}

onMounted(load)
</script>

<style scoped>
.msg { padding: 12px 16px; border-bottom: 1px solid #F2F4F6; }
.msg.unread { background: #F7F5FC; }
</style>
