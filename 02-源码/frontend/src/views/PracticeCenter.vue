<template>
  <div>
    <div class="head">
      <div>
        <div class="page-title">练习中心</div>
        <div class="muted" style="margin-top: 4px">按学科与知识点推荐，交卷即时判分并自动归档错题</div>
      </div>
      <div class="filter-bar">
        <el-select v-model="subjectId" style="width: 170px" clearable placeholder="全部学科" @change="load">
          <el-option v-for="s in subjects" :key="s.id" :value="s.id" :label="s.subjectName" />
        </el-select>
        <el-button type="primary" @click="load">刷新</el-button>
      </div>
    </div>

    <div class="kpi-grid" style="margin-bottom: 16px">
      <div class="kpi"><div class="t">可练习试卷</div><div class="v num">{{ papers.length }}</div><div class="d">已发布与使用中</div></div>
      <div class="kpi"><div class="t">进行中练习</div><div class="v num">{{ ongoing.length }}</div><div class="d">可继续作答</div></div>
      <div class="kpi"><div class="t">我的练习次数</div><div class="v num">{{ records.length }}</div><div class="d">含知识点与错题重练</div></div>
      <div class="kpi"><div class="t">待复习错题</div><div class="v num">{{ dueCount }}</div><div class="d">今日到期 {{ dueCount }} 道</div></div>
    </div>

    <div class="h3">继续上次练习</div>
    <div class="card" v-if="ongoing.length" style="margin-bottom: 18px">
      <div class="card-b" v-for="r in ongoing" :key="r.id" style="display: flex; align-items: center; gap: 16px">
        <div class="icon">✎</div>
        <div style="flex: 1">
          <div style="font-weight: 600">练习 {{ r.recordNo }} · {{ r.practiceType }}</div>
          <div class="muted" style="margin-top: 4px">
            共 {{ r.questionCount }} 题 · 开始于 {{ formatTime(r.startTime) }}
          </div>
          <div class="bar" style="margin-top: 8px; max-width: 420px"><i style="width: 40%"></i></div>
        </div>
        <el-button type="primary" @click="$router.push('/answer/' + r.id)">继续答题</el-button>
      </div>
    </div>
    <div class="card" v-else style="margin-bottom: 18px">
      <div class="card-b"><el-empty description="暂无进行中的练习，从下方选择一份试卷开始" :image-size="70" /></div>
    </div>

    <div class="h3">可练习试卷</div>
    <div class="grid3">
      <div class="card pcard" v-for="p in papers" :key="p.id">
        <div class="card-b">
          <div style="display: flex; justify-content: space-between; align-items: center">
            <el-tag size="small" effect="light" :type="p.buildMode === '随机' ? 'primary' : 'info'">{{ p.buildMode }}组卷</el-tag>
            <span class="muted">{{ p.durationMin }} 分钟</span>
          </div>
          <div class="pname">{{ p.paperName }}</div>
          <div class="muted">{{ subjectName(p.subjectId) }} · {{ p.questionCount }} 题 · 总分 {{ p.totalScore }}</div>
          <div class="pfoot">
            <span class="muted">难度均值 {{ Number(p.difficultyAvg).toFixed(2) }}</span>
            <el-button type="primary" size="small" @click="start(p)">开始答题</el-button>
          </div>
        </div>
      </div>
      <el-empty v-if="!papers.length" description="该学科暂无可练习试卷" />
    </div>

    <div class="h3" style="margin-top: 18px">我的练习记录</div>
    <div class="card">
      <el-table :data="records" border style="width: 100%">
        <el-table-column prop="recordNo" label="练习编号" width="160" />
        <el-table-column prop="practiceType" label="类型" width="110" />
        <el-table-column label="开始时间" width="170">
          <template #default="{ row }"><span class="num">{{ formatTime(row.startTime) }}</span></template>
        </el-table-column>
        <el-table-column label="用时" width="100">
          <template #default="{ row }"><span class="num">{{ Math.round(row.usedSeconds / 60) }} 分钟</span></template>
        </el-table-column>
        <el-table-column label="得分" width="90">
          <template #default="{ row }"><b class="num">{{ Number(row.gotScore).toFixed(1) }}</b></template>
        </el-table-column>
        <el-table-column label="正确" width="110">
          <template #default="{ row }">{{ row.correctCount }} / {{ row.questionCount }}</template>
        </el-table-column>
        <el-table-column label="状态" width="100">
          <template #default="{ row }"><el-tag size="small" :type="statusType(row.status)" effect="light">{{ row.status }}</el-tag></template>
        </el-table-column>
        <el-table-column label="操作" width="120">
          <template #default="{ row }">
            <el-button v-if="row.status === '进行中'" link type="primary" @click="$router.push('/answer/' + row.id)">继续</el-button>
            <el-button v-else link type="primary" @click="$router.push('/answer/' + row.id)">看解析</el-button>
          </template>
        </el-table-column>
        <template #empty><el-empty description="还没有练习记录" /></template>
      </el-table>
    </div>
  </div>
</template>

<script setup>
/** 练习中心：可练试卷、进行中练习、记录与错题重练入口 */
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import request from '@/utils/request'
import { formatTime, statusType } from '@/utils/format'

const router = useRouter()
const subjects = ref([])
const subjectId = ref(null)
const papers = ref([])
const records = ref([])
const ongoing = ref([])
const dueCount = ref(0)

function subjectName(id) { return (subjects.value.find((s) => s.id === id) || {}).subjectName || '-' }

async function load() {
  const params = { page: 1, size: 30 }
  if (subjectId.value) params.subjectId = subjectId.value
  const [pub, using] = await Promise.all([
    request.get('/api/paper/page', { params: { ...params, status: '已发布' } }),
    request.get('/api/paper/page', { params: { ...params, status: '使用中' } })
  ])
  papers.value = [...(pub.list || []), ...(using.list || [])]
  records.value = (await request.get('/api/practice-record/my')) || []
  ongoing.value = records.value.filter((r) => r.status === '进行中')
  const due = await request.get('/api/wrong-book/due')
  dueCount.value = (due || []).length
}

async function start(p) {
  const d = await request.post('/api/practice/start', { paperId: p.id, practiceType: '试卷练习' })
  ElMessage.success(d.resumed ? '已恢复上次作答进度' : '已开始答题，交卷后即时判分')
  router.push('/answer/' + d.recordId)
}

onMounted(async () => {
  subjects.value = (await request.get('/api/subject/list')) || []
  load()
})
</script>

<style scoped>
.head { display: flex; align-items: flex-end; justify-content: space-between; margin-bottom: 16px; gap: 16px; }
.h3 { font-size: 14px; font-weight: 600; margin: 0 0 10px; }
.icon {
  width: 44px; height: 44px; border-radius: 10px; background: #F0EEF7;
  display: flex; align-items: center; justify-content: center; font-size: 18px;
}
.bar { height: 7px; background: #EDEFF2; border-radius: 4px; overflow: hidden; }
.bar i { display: block; height: 100%; background: var(--primary); }
.grid3 { display: grid; grid-template-columns: repeat(3, 1fr); gap: 14px; }
.pcard { margin-bottom: 0; }
.pname { font-size: 14px; font-weight: 600; margin: 10px 0 6px; }
.pfoot { display: flex; justify-content: space-between; align-items: center; margin-top: 14px; }
</style>
