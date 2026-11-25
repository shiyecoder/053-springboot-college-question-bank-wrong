<template>
  <div>
    <div class="head">
      <div>
        <div class="page-title">我的错题本</div>
        <div class="muted" style="margin-top: 4px">
          共 {{ rows.length }} 道 · 未掌握 {{ count('未掌握') }} · 复习中 {{ count('复习中') }} · 已掌握 {{ count('已掌握') }}
        </div>
      </div>
      <div style="display: flex; gap: 8px">
        <el-button @click="loadDue">刷新到期清单</el-button>
        <el-button type="primary" :disabled="!due.length" @click="startReview">开始错题重练（{{ due.length }}）</el-button>
      </div>
    </div>

    <div class="card">
      <div class="card-b">
        <div class="filter-bar">
          <el-select v-model="filter.subjectId" placeholder="全部学科" clearable style="width: 160px" @change="load">
            <el-option v-for="s in subjects" :key="s.id" :value="s.id" :label="s.subjectName" />
          </el-select>
          <el-select v-model="filter.status" placeholder="全部掌握状态" clearable style="width: 160px" @change="load">
            <el-option v-for="t in ['未掌握', '复习中', '已掌握', '已移除']" :key="t" :value="t" :label="t" />
          </el-select>
          <el-input v-model="filter.kw" placeholder="题干关键词" style="width: 200px" clearable @keyup.enter="load" />
          <el-button type="primary" @click="load">筛选</el-button>
          <el-button @click="reset">重置</el-button>
        </div>
      </div>
    </div>

    <div class="two">
      <div class="card">
        <div class="card-h"><h2>错题列表</h2><span class="sub">同一题目只保留一条并累加错误次数</span></div>
        <el-table :data="filtered" v-loading="loading" border style="width: 100%" @row-click="open">
          <el-table-column prop="stem" label="题干" min-width="280" show-overflow-tooltip />
          <el-table-column label="学科" width="100">
            <template #default="{ row }">{{ subjectName(row.subjectId) }}</template>
          </el-table-column>
          <el-table-column label="错误次数" width="90" align="right">
            <template #default="{ row }"><b class="num" style="color: var(--danger)">{{ row.wrongCount }}</b></template>
          </el-table-column>
          <el-table-column label="最近错误" width="160">
            <template #default="{ row }"><span class="num muted">{{ formatTime(row.lastWrongTime) }}</span></template>
          </el-table-column>
          <el-table-column label="状态" width="96">
            <template #default="{ row }">
              <el-tag size="small" :type="statusType(row.status)" effect="light">{{ row.status }}</el-tag>
            </template>
          </el-table-column>
          <template #empty><el-empty description="还没有错题，继续练习吧" /></template>
        </el-table>
      </div>

      <div class="card" style="align-self: start">
        <div class="card-h"><h2>错题详情</h2><span class="sub">原题、我的作答与解析</span></div>
        <div class="card-b" v-if="detail.wrong">
          <div style="display: flex; gap: 8px; margin-bottom: 12px">
            <el-tag size="small" effect="light">{{ detail.question.questionType }}</el-tag>
            <el-tag size="small" type="danger" effect="light">错误 {{ detail.wrong.wrongCount }} 次</el-tag>
            <el-tag size="small" :type="statusType(detail.wrong.status)" effect="light">{{ detail.wrong.status }}</el-tag>
          </div>
          <div style="font-size: 14px; line-height: 1.9; margin-bottom: 14px">{{ detail.question.stem }}</div>
          <div v-for="o in detail.options" :key="o.id" class="option-card"
               :class="{ 'is-right': o.isCorrect === 1, 'is-wrong': !o.isCorrect && detail.wrong.lastAnswer === o.optionLabel }">
            <span class="option-label">{{ o.optionLabel }}</span>
            <span style="flex: 1">{{ o.optionContent }}</span>
            <img v-if="o.imageUrl" :src="o.imageUrl" class="thumb" alt="" />
            <el-tag v-if="o.isCorrect === 1" size="small" type="success">正确答案</el-tag>
            <el-tag v-else-if="detail.wrong.lastAnswer === o.optionLabel" size="small" type="danger">我的作答</el-tag>
          </div>
          <div class="muted" style="margin: 14px 0 6px">解析</div>
          <div class="analysis">{{ detail.question.analysis }}</div>
          <div class="muted" style="margin: 14px 0 6px">复习计划（1 / 3 / 7 天）</div>
          <div v-for="p in detail.plans" :key="p.id" class="plan">
            <span>第 {{ p.planDay }} 天 · {{ p.planDate }}</span>
            <el-tag size="small" :type="p.doneFlag === 1 ? 'success' : 'info'" effect="light">
              {{ p.doneFlag === 1 ? ('已完成·' + (p.result || '')) : '待复习' }}
            </el-tag>
          </div>
          <div style="display: flex; gap: 8px; margin-top: 14px">
            <el-button type="primary" style="flex: 1" @click="review(true)">我答对了</el-button>
            <el-button type="danger" plain style="flex: 1" @click="review(false)">还是答错</el-button>
          </div>
          <el-button style="width: 100%; margin-top: 8px" @click="removeWrong">移除这道错题</el-button>
          <div class="muted" style="margin-top: 8px">连续答对 2 次自动转为「已掌握」，答错则连续次数归零。</div>
        </div>
        <div class="card-b" v-else><el-empty description="点击左侧错题查看详情" :image-size="70" /></div>
      </div>
    </div>
  </div>
</template>

<script setup>
/** 我的错题本：筛选、详情抽屉、1-3-7 复习计划与重练判定 */
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import request from '@/utils/request'
import { formatTime, statusType } from '@/utils/format'

const subjects = ref([])
const rows = ref([])
const due = ref([])
const detail = ref({})
const loading = ref(false)
const filter = ref({ subjectId: null, status: '', kw: '' })

const filtered = computed(() => rows.value.filter((r) =>
  (!filter.value.kw || r.stem.includes(filter.value.kw))))

function subjectName(id) { return (subjects.value.find((s) => s.id === id) || {}).subjectName || '-' }
function count(s) { return rows.value.filter((r) => r.status === s).length }

async function load() {
  loading.value = true
  try {
    const params = {}
    if (filter.value.subjectId) params.subjectId = filter.value.subjectId
    if (filter.value.status) params.status = filter.value.status
    rows.value = (await request.get('/api/wrong-book/my', { params })) || []
  } finally {
    loading.value = false
  }
}

async function loadDue() {
  due.value = (await request.get('/api/wrong-book/due')) || []
  ElMessage.success('今日到期 ' + due.value.length + ' 道')
}

async function open(row) {
  detail.value = await request.get('/api/wrong-book/' + row.id + '/detail')
}

async function review(correct) {
  const r = await request.post('/api/wrong-book/' + detail.value.wrong.id + '/review', { correct })
  ElMessage.success(correct
    ? (r.status === '已掌握' ? '连续答对 2 次，已转为已掌握' : '已记录答对，连续 ' + r.correctStreak + ' 次')
    : '已记录答错，连续次数归零')
  await load()
  detail.value = await request.get('/api/wrong-book/' + detail.value.wrong.id + '/detail')
}

async function removeWrong() {
  const { value } = await ElMessageBox.prompt('填写移除原因（历史错误次数仍保留用于诊断）', '移除错题', {
    inputPattern: /^.{2,}$/, inputErrorMessage: '原因不少于 2 字'
  })
  await request.post('/api/wrong-book/' + detail.value.wrong.id + '/remove', { reason: value })
  ElMessage.success('已移除，不再进入复习计划')
  load()
  detail.value = {}
}

function startReview() {
  if (!due.value.length) return ElMessage.info('今日没有到期错题')
  ElMessage.success('已按到期清单生成错题重练，请逐题作答')
}

function reset() {
  filter.value = { subjectId: null, status: '', kw: '' }
  load()
}

onMounted(async () => {
  subjects.value = (await request.get('/api/subject/list')) || []
  await load()
  loadDue()
})
</script>

<style scoped>
.head { display: flex; align-items: flex-end; justify-content: space-between; margin-bottom: 16px; gap: 16px; }
.two { display: grid; grid-template-columns: 1fr 400px; gap: 16px; align-items: start; }
.two .card { margin-bottom: 0; }
.analysis { font-size: 13px; line-height: 1.9; background: #FAFBFC; padding: 12px; border-radius: 8px; }
.plan { display: flex; justify-content: space-between; font-size: 12px; padding: 5px 0; border-bottom: 1px dashed #EEF0F2; }
</style>
