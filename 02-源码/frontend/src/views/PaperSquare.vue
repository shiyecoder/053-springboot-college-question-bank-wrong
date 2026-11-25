<template>
  <div>
    <div class="head">
      <div>
        <div class="page-title">试卷库</div>
        <div class="muted" style="margin-top: 4px">可练习的试卷按学科分类，交卷即判分并生成错题</div>
      </div>
      <el-select v-model="subjectId" clearable placeholder="全部学科" style="width: 180px" @change="load">
        <el-option v-for="s in subjects" :key="s.id" :value="s.id" :label="s.subjectName" />
      </el-select>
    </div>

    <div class="grid3">
      <div class="card" v-for="p in papers" :key="p.id">
        <div class="card-b">
          <div style="display: flex; justify-content: space-between; align-items: center">
            <el-tag size="small" effect="light" :type="p.status === '使用中' ? 'primary' : 'success'">{{ p.status }}</el-tag>
            <span class="muted">{{ p.buildMode }}组卷</span>
          </div>
          <div style="font-size: 14px; font-weight: 600; margin: 10px 0 6px">{{ p.paperName }}</div>
          <div class="muted">{{ subjectName(p.subjectId) }} · {{ p.questionCount }} 题 · 总分 {{ p.totalScore }}</div>
          <div class="muted" style="margin-top: 4px">建议时长 {{ p.durationMin }} 分钟 · 难度均值 {{ Number(p.difficultyAvg).toFixed(2) }}</div>
          <div style="display: flex; gap: 8px; margin-top: 14px">
            <el-button type="primary" size="small" @click="start(p)">开始练习</el-button>
          </div>
        </div>
      </div>
      <el-empty v-if="!papers.length" description="暂无可练习的试卷" />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import request from '@/utils/request'

const router = useRouter()
const subjects = ref([])
const subjectId = ref(null)
const papers = ref([])

function subjectName(id) { return (subjects.value.find((s) => s.id === id) || {}).subjectName || '-' }

async function load() {
  const params = { page: 1, size: 30 }
  if (subjectId.value) params.subjectId = subjectId.value
  const [a, b] = await Promise.all([
    request.get('/api/paper/page', { params: { ...params, status: '已发布' } }),
    request.get('/api/paper/page', { params: { ...params, status: '使用中' } })
  ])
  papers.value = [...(a.list || []), ...(b.list || [])]
}

async function start(p) {
  const d = await request.post('/api/practice/start', { paperId: p.id, practiceType: '试卷练习' })
  ElMessage.success(d.resumed ? '已恢复上次作答' : '开始答题')
  router.push('/answer/' + d.recordId)
}

onMounted(async () => {
  subjects.value = (await request.get('/api/subject/list')) || []
  load()
})
</script>

<style scoped>
.head { display: flex; align-items: flex-end; justify-content: space-between; margin-bottom: 16px; gap: 16px; }
.grid3 { display: grid; grid-template-columns: repeat(3, 1fr); gap: 14px; }
.grid3 .card { margin-bottom: 0; }
</style>
