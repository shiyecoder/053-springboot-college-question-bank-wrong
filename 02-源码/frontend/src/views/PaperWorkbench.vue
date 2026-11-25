<template>
  <div>
    <div class="filter-bar" style="margin-bottom: 14px">
      <el-input v-model="meta.paperName" placeholder="试卷名称" style="width: 280px" />
      <el-select v-model="meta.subjectId" style="width: 160px" @change="onSubject">
        <el-option v-for="s in subjects" :key="s.id" :value="s.id" :label="s.subjectName" />
      </el-select>
      <el-select v-model="meta.buildMode" style="width: 140px">
        <el-option value="手动" label="手动组卷" /><el-option value="随机" label="随机组卷" />
        <el-option value="错题重练" label="错题重练" />
      </el-select>
      <el-select v-model="meta.durationMin" style="width: 150px">
        <el-option v-for="d in [30, 45, 60, 90, 120]" :key="d" :value="d" :label="'建议时长 ' + d + ' 分钟'" />
      </el-select>
      <el-input-number v-model="meta.totalScore" :min="10" :max="300" :step="10" style="width: 130px" />
      <el-button @click="preview">预览试卷</el-button>
      <el-button type="primary" :loading="saving" @click="saveManual">保存试卷</el-button>
      <span class="muted" style="margin-left: auto">
        总分校验：<b :style="{ color: sumScore === Number(meta.totalScore) ? '#2B7955' : '#B02A37' }">
          {{ sumScore.toFixed(1) }} / {{ meta.totalScore }}</b>
      </span>
    </div>

    <div class="three">
      <div class="card">
        <div class="card-h"><h2>知识点</h2></div>
        <div class="card-b" style="padding: 10px">
          <div v-for="k in kps" :key="k.id" class="kp-row">
            <el-checkbox v-model="k.checked" @change="reloadPool">
              <span style="font-size: 12px">{{ k.kpName }}</span>
            </el-checkbox>
            <el-input-number v-model="k.count" :min="1" :max="20" size="small" style="width: 74px" />
            <span class="muted num" style="width: 46px; text-align: right">{{ k.questionCount }} 题</span>
          </div>
          <el-empty v-if="!kps.length" description="该学科暂无知识点" :image-size="60" />
          <div style="border-top: 1px solid #EEF0F2; margin-top: 10px; padding-top: 10px">
            <div class="muted" style="margin-bottom: 6px">难度区间</div>
            <div style="display: flex; gap: 6px; align-items: center">
              <el-input-number v-model="meta.minDifficulty" :min="0.1" :max="1" :step="0.05" :precision="2" size="small" style="width: 92px" />
              <span class="muted">—</span>
              <el-input-number v-model="meta.maxDifficulty" :min="0.1" :max="1" :step="0.05" :precision="2" size="small" style="width: 92px" />
            </div>
            <el-button type="primary" style="width: 100%; margin-top: 10px" :loading="generating" @click="generate">
              按权重随机抽题
            </el-button>
            <div class="muted" style="margin-top: 6px">题量不足时按缺口比例回补到相邻知识点，并在预览中标注。</div>
          </div>
        </div>
      </div>

      <div class="card">
        <div class="card-h"><h2>题目池</h2><span class="sub">{{ pool.length }} 道候选</span>
          <span class="muted" style="margin-left: auto">难度均值 {{ poolAvg }}</span>
        </div>
        <el-table :data="pool" border height="520" style="width: 100%">
          <el-table-column width="48">
            <template #default="{ row }">
              <el-checkbox :model-value="basket.some((b) => b.id === row.id)"
                           @change="(v) => toggle(row, v)" />
            </template>
          </el-table-column>
          <el-table-column prop="stem" label="题干" min-width="280" show-overflow-tooltip />
          <el-table-column prop="questionType" label="题型" width="80">
            <template #default="{ row }"><el-tag size="small" effect="light" :type="questionTypeTag(row.questionType)">{{ row.questionType }}</el-tag></template>
          </el-table-column>
          <el-table-column prop="difficulty" label="难度" width="76" align="right">
            <template #default="{ row }">{{ Number(row.difficulty).toFixed(2) }}</template>
          </el-table-column>
          <el-table-column label="知识点" width="120">
            <template #default="{ row }">{{ kpName(row.knowledgePointId) }}</template>
          </el-table-column>
          <template #empty><el-empty description="勾选左侧知识点后从题库抽题" /></template>
        </el-table>
      </div>

      <div class="card">
        <div class="card-h"><h2>试卷篮</h2><span class="sub">{{ basket.length }} / {{ meta.questionCount || 20 }} 题</span></div>
        <div class="card-b" style="padding: 12px">
          <div class="basket-stat">
            <div><div class="muted">总分</div><b class="num">{{ sumScore.toFixed(1) }}</b></div>
            <div><div class="muted">难度均值</div><b class="num">{{ basketAvg }}</b></div>
          </div>
          <div v-for="(b, i) in basket" :key="b.id" class="basket-item">
            <b class="num" style="color: var(--muted)">{{ String(i + 1).padStart(2, '0') }}</b>
            <span style="flex: 1; overflow: hidden; text-overflow: ellipsis; white-space: nowrap">{{ b.stem }}</span>
            <span class="num">{{ b.score }}</span>
            <el-icon style="cursor: pointer; color: var(--danger)" @click="toggle(b, false)"><Close /></el-icon>
          </div>
          <el-empty v-if="!basket.length" description="试卷篮为空，从中间题目池勾选" :image-size="60" />
          <el-alert v-if="backfill.length" type="warning" :closable="false" style="margin-top: 10px"
                    :title="'回补明细：' + backfill.join('；')" />
          <el-button type="primary" style="width: 100%; margin-top: 12px" @click="saveManual">提交审核</el-button>
        </div>
      </div>
    </div>

    <el-drawer v-model="drawer" title="试卷预览" size="560px">
      <div v-if="previewData.paper">
        <div style="font-size: 16px; font-weight: 700">{{ previewData.paper.paperName }}</div>
        <div class="muted" style="margin: 6px 0 16px">
          共 {{ previewData.questions.length }} 题 · 总分 {{ previewData.paper.totalScore }} · 建议 {{ previewData.paper.durationMin }} 分钟
        </div>
        <div v-for="(q, i) in previewData.questions" :key="q.id" style="margin-bottom: 16px">
          <div style="font-size: 13px; line-height: 1.8">{{ i + 1 }}. {{ q.stem }}（{{ q.score }} 分）</div>
          <div v-for="o in q.options" :key="o.id" class="muted" style="padding-left: 14px">
            {{ o.optionLabel }}. {{ o.optionContent }}
          </div>
        </div>
      </div>
    </el-drawer>
  </div>
</template>

<script setup>
/** 组卷工作台：左侧知识点与难度、中间题目池、右侧试卷篮，支持随机抽题与手动组卷 */
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import request from '@/utils/request'
import { questionTypeTag } from '@/utils/format'

const router = useRouter()
const subjects = ref([])
const kps = ref([])
const pool = ref([])
const basket = ref([])
const backfill = ref([])
const drawer = ref(false)
const previewData = ref({})
const saving = ref(false)
const generating = ref(false)
const meta = reactive({
  paperName: '高等数学 随堂测评卷', subjectId: 1, buildMode: '随机',
  durationMin: 60, totalScore: 100, questionCount: 20, minDifficulty: 0.2, maxDifficulty: 0.9
})

const sumScore = computed(() => basket.value.reduce((s, b) => s + Number(b.score || 0), 0))
const basketAvg = computed(() => basket.value.length
  ? (basket.value.reduce((s, b) => s + Number(b.difficulty || 0), 0) / basket.value.length).toFixed(2) : '0.00')
const poolAvg = computed(() => pool.value.length
  ? (pool.value.reduce((s, b) => s + Number(b.difficulty || 0), 0) / pool.value.length).toFixed(2) : '0.00')

function kpName(id) { return (kps.value.find((k) => k.id === id) || {}).kpName || '-' }

async function onSubject() {
  const tree = await request.get('/api/knowledge-point/tree', { params: { subjectId: meta.subjectId } })
  const flat = []
  const walk = (nodes, lv) => nodes.forEach((n) => {
    flat.push({ id: n.id, kpName: n.kpName, questionCount: n.questionCount, examWeight: n.examWeight, checked: lv === 1, count: 3 })
    if (n.children) walk(n.children, lv + 1)
  })
  walk(tree || [], 1)
  kps.value = flat
  basket.value = []
  reloadPool()
}

async function reloadPool() {
  const checked = kps.value.filter((k) => k.checked)
  if (!checked.length) { pool.value = []; return }
  // 题目池按勾选知识点过滤（后端按知识点等值查询，这里合并多次结果）
  const seen = new Set()
  const out = []
  for (const k of checked) {
    const d = await request.get('/api/question/page', {
      params: { page: 1, size: 50, status: '已入库', subjectId: meta.subjectId, knowledgePointId: k.id }
    })
    for (const q of d.list || []) {
      if (!seen.has(q.id)) { seen.add(q.id); out.push(q) }
    }
  }
  pool.value = out
}

function toggle(row, add) {
  if (add) {
    if (!basket.value.some((b) => b.id === row.id)) basket.value.push({ ...row })
  } else {
    basket.value = basket.value.filter((b) => b.id !== row.id)
  }
}

async function generate() {
  generating.value = true
  try {
    const rules = kps.value.filter((k) => k.checked).map((k) => ({ kpId: k.id, count: k.count }))
    if (!rules.length) return ElMessage.warning('请至少勾选一个知识点')
    const d = await request.post('/api/paper/generate-random', {
      paperName: meta.paperName, subjectId: meta.subjectId, totalScore: meta.totalScore,
      durationMin: meta.durationMin, minDifficulty: meta.minDifficulty, maxDifficulty: meta.maxDifficulty,
      rules
    })
    backfill.value = d.backfill || []
    ElMessage.success('已生成试卷 ' + d.paperNo + '，共 ' + d.questionCount + ' 题')
    router.push('/paper/' + d.id)
  } finally {
    generating.value = false
  }
}

async function saveManual() {
  if (!basket.value.length) return ElMessage.warning('试卷篮为空，先勾选题目或使用随机抽题')
  if (sumScore.value !== Number(meta.totalScore)) {
    return ElMessage.warning('题目分值合计 ' + sumScore.value + ' 与总分 ' + meta.totalScore + ' 不一致，请调整后再保存')
  }
  saving.value = true
  try {
    const p = await request.post('/api/paper', {
      paperName: meta.paperName, subjectId: meta.subjectId, buildMode: meta.buildMode,
      questionCount: basket.value.length, totalScore: meta.totalScore, durationMin: meta.durationMin,
      difficultyAvg: Number(basketAvg.value), creatorId: JSON.parse(localStorage.getItem('qb_user') || '{}').id,
      status: '待审核'
    })
    for (let i = 0; i < basket.value.length; i++) {
      const b = basket.value[i]
      await request.post('/api/paper-question', {
        paperId: p.id, questionId: b.id, sectionNo: 1, sortNo: i + 1,
        score: b.score, questionType: b.questionType, knowledgePointId: b.knowledgePointId, stemSnapshot: b.stem
      })
    }
    ElMessage.success('试卷已保存并提交审核')
    router.push('/paper/' + p.id)
  } finally {
    saving.value = false
  }
}

async function preview() {
  if (basket.value.length) {
    previewData.value = { paper: { paperName: meta.paperName, totalScore: meta.totalScore, durationMin: meta.durationMin }, questions: basket.value }
  } else {
    previewData.value = await request.get('/api/paper/1/detail')
  }
  drawer.value = true
}

onMounted(async () => {
  subjects.value = (await request.get('/api/subject/list')) || []
  meta.subjectId = subjects.value[0]?.id || 1
  await onSubject()
})
</script>

<style scoped>
.three { display: grid; grid-template-columns: 240px 1fr 350px; gap: 16px; align-items: start; }
.three .card { margin-bottom: 0; }
.kp-row { display: flex; align-items: center; gap: 8px; padding: 4px 0; }
.basket-stat { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-bottom: 12px; }
.basket-stat > div { background: #F7F5FC; border-radius: 8px; padding: 9px 11px; }
.basket-stat b { font-size: 19px; color: var(--primary); }
.basket-item {
  display: flex; gap: 8px; padding: 8px 0; border-bottom: 1px dashed #EEF0F2; font-size: 12px; align-items: center;
}
</style>
