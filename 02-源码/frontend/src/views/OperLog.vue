<template>
  <div>
    <div class="card">
      <div class="card-b">
        <div class="filter-bar">
          <el-input v-model="kw" placeholder="模块 / 内容" style="width: 230px" clearable @keyup.enter="reload" />
          <el-button type="primary" @click="reload">查询</el-button>
        </div>
      </div>
    </div>
    <div class="card">
      <div class="card-h"><h2>操作日志</h2><span class="sub">关键写操作留痕</span></div>
      <el-table :data="rows" v-loading="loading" border style="width: 100%">
        <el-table-column prop="module" label="模块" width="120" />
        <el-table-column prop="operType" label="操作" width="110" />
        <el-table-column prop="bizNo" label="业务编号" width="150" />
        <el-table-column prop="content" label="内容" min-width="320" show-overflow-tooltip />
        <el-table-column prop="operName" label="操作人" width="100" />
        <el-table-column label="时间" width="170">
          <template #default="{ row }"><span class="num">{{ formatTime(row.operTime) }}</span></template>
        </el-table-column>
        <el-table-column prop="ip" label="IP" width="120" />
      </el-table>
      <div style="display: flex; justify-content: flex-end; padding: 14px 16px">
        <el-pagination background layout="total, prev, pager, next" :total="total"
                       v-model:current-page="page" :page-size="10" @current-change="load" />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import request from '@/utils/request'
import { formatTime } from '@/utils/format'

const rows = ref([])
const total = ref(0)
const page = ref(1)
const kw = ref('')
const loading = ref(false)

async function load() {
  loading.value = true
  try {
    const d = await request.get('/api/oper-log/page', { params: { page: page.value, size: 10, kw: kw.value } })
    rows.value = d.list || []
    total.value = d.total || 0
  } finally {
    loading.value = false
  }
}
function reload() { page.value = 1; load() }
onMounted(load)
</script>
