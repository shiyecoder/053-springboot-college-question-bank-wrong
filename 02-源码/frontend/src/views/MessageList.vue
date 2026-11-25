<template>
  <div>
    <div class="card">
      <div class="card-h"><h2>站内消息</h2><span class="sub">审核、待办与到期提醒</span>
        <span style="margin-left: auto" class="muted">未读 {{ unreadCount }} 条</span>
      </div>
      <div v-for="m in rows" :key="m.id" class="msg" :class="{ unread: m.readFlag === 0 }" @click="markRead(m)">
        <div style="display: flex; justify-content: space-between">
          <b>{{ m.title }}</b>
          <span class="muted num">{{ formatTime(m.createTime) }}</span>
        </div>
        <div class="muted" style="margin-top: 5px">{{ m.content }}</div>
      </div>
      <el-empty v-if="!rows.length" description="暂无消息" />
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import request from '@/utils/request'
import { formatTime } from '@/utils/format'

const rows = ref([])
const user = JSON.parse(localStorage.getItem('qb_user') || '{}')
const unreadCount = computed(() => rows.value.filter((r) => r.readFlag === 0).length)

async function load() {
  const d = await request.get('/api/message/page', { params: { page: 1, size: 30, receiverId: user.id } })
  rows.value = d.list || []
}

async function markRead(m) {
  if (m.readFlag === 0) {
    await request.put('/api/message/' + m.id, { ...m, readFlag: 1 })
    load()
  }
}

onMounted(load)
</script>

<style scoped>
.msg { padding: 12px 16px; border-bottom: 1px solid #F2F4F6; cursor: pointer; }
.msg:hover { background: #FAFBFC; }
.msg.unread { background: #F7F5FC; }
</style>
