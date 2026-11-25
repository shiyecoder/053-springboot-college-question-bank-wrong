<template>
  <div>
    <div class="filter-bar" style="margin-bottom: 14px">
      <el-select v-model="subjectId" placeholder="全部学科" clearable style="width: 170px" @change="load">
        <el-option v-for="s in subjects" :key="s.id" :value="s.id" :label="s.subjectName" />
      </el-select>
      <el-select v-model="type" placeholder="全部题型" clearable style="width: 140px" @change="load">
        <el-option v-for="t in ['单选', '多选', '判断', '填空', '简答', '计算']" :key="t" :value="t" :label="t" />
      </el-select>
      <el-button type="primary" @click="load">筛选</el-button>
      <span class="muted" style="margin-left: auto">按学科与题型筛选待审核题目，选中左侧任一条开始审核</span>
    </div>

    <div class="three">
      <div class="card">
        <div class="card-h"><h2>待审核队列</h2></div>
        <div class="card-b" style="padding: 6px; max-height: 560px; overflow: auto">
          <div v-for="q in queue" :key="q.id" class="qrow" :class="{ on: cur.id === q.id }" @click="pick(q)">
            <div style="display: flex; justify-content: space-between; font-size: 12px">
              <b>{{ q.questionNo }}</b><span class="muted">{{ q.questionType }}</span>
            </div>
            <div class="muted" style="margin-top: 4px; font-size: 11px">
              {{ subjectName(q.subjectId) }} · {{ kpName(q.knowledgePointId) }} · {{ formatTime(q.createTime) }}
            </div>
          </div>
          <el-empty v-if="!queue.length" description="没有待审核题目" :image-size="60" />
        </div>
      </div>

      <div class="card">
        <div class="card-h"><h2>题干与选项预览</h2>
          <span class="sub" v-if="cur.id">{{ cur.questionNo }}</span></div>
        <div class="card-b">
          <template v-if="cur.id">
            <div style="display: flex; gap: 8px; margin-bottom: 14px">
              <el-tag size="small" effect="light">{{ detail.question.questionType }}</el-tag>
              <el-tag size="small" type="info" effect="plain">难度 {{ detail.question.difficulty }}</el-tag>
              <el-tag size="small" type="info" effect="plain">{{ detail.question.score }} 分</el-tag>
              <el-tag size="small" type="info" effect="plain">{{ detail.question.sourceType }}</el-tag>
            </div>
            <div class="stem-box">{{ detail.question.stem }}</div>
            <div v-for="o in detail.options" :key="o.id" class="option-card" :class="{ 'is-right': o.isCorrect === 1 }">
              <span class="option-label">{{ o.optionLabel }}</span>
              <span style="flex: 1">{{ o.optionContent }}</span>
              <img v-if="o.imageUrl" :src="o.imageUrl" class="thumb" alt="" />
              <el-tag v-if="o.isCorrect === 1" size="small" type="success">正确</el-tag>
            </div>
            <div class="muted" style="margin: 14px 0 6px">标准答案</div>
            <div class="answer-box">{{ detail.question.answer }}</div>
            <div class="muted" style="margin: 14px 0 6px">解析</div>
            <div class="analysis">{{ detail.question.analysis }}</div>
            <div class="muted" style="margin-top: 12px">
              解析字数 {{ (detail.question.analysis || '').length }} / 要求 ≥ 20
            </div>
            <div class="muted" style="margin-top: 14px; line-height: 1.9">
              <b>历史审核记录</b>
              <div v-for="a in detail.audits" :key="a.id">
                {{ formatTime(a.auditTime) }} · {{ a.auditResult }}
                <span v-if="a.reason">· {{ a.reasonType }}：{{ a.reason }}</span>
              </div>
              <div v-if="!detail.audits || !detail.audits.length">暂无审核记录（首次提交）</div>
            </div>
          </template>
          <el-empty v-else description="从左侧选择一道待审核题目" />
        </div>
      </div>

      <div class="card" style="align-self: start">
        <div class="card-h"><h2>归类与校准</h2></div>
        <div class="card-b">
          <template v-if="cur.id">
            <el-form label-width="76px">
              <el-form-item label="知识点">
                <el-select v-model="cur.knowledgePointId" filterable style="width: 100%" @change="saveClassify">
                  <el-option v-for="k in kps" :key="k.id" :value="k.id" :label="k.kpName" />
                </el-select>
              </el-form-item>
              <el-form-item label="难度">
                <el-input-number v-model="cur.difficulty" :min="0.1" :max="1" :step="0.05" :precision="2"
                                 style="width: 100%" @change="saveClassify" />
              </el-form-item>
              <el-form-item label="来源">
                <el-select v-model="cur.sourceType" style="width: 100%" @change="saveClassify">
                  <el-option v-for="t in ['自建', '真题', '教材', '引进']" :key="t" :value="t" :label="t" />
                </el-select>
              </el-form-item>
            </el-form>
            <div class="muted" style="margin-bottom: 10px">退回原因（退回时必填）</div>
            <el-select v-model="reasonType" placeholder="选择原因分类" style="width: 100%; margin-bottom: 8px">
              <el-option v-for="t in ['题干不清', '答案错误', '解析缺失', '知识点错误']" :key="t" :value="t" :label="t" />
            </el-select>
            <el-input v-model="reason" type="textarea" :rows="3" placeholder="补充说明（5-200 字）" />
            <div style="display: flex; gap: 8px; margin-top: 14px">
              <el-button type="primary" style="flex: 1" :loading="acting" @click="audit('通过')">通过入库</el-button>
              <el-button type="danger" plain style="flex: 1" :loading="acting" @click="audit('退回')">退回修改</el-button>
            </div>
            <el-alert type="info" :closable="false" style="margin-top: 12px"
                      title="审核人不得为创建人；退回原因写入操作日志并通知提交人。" />
          </template>
          <el-empty v-else description="选择题目后可校准归类" :image-size="60" />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
/** 题目审核台：左队列、中预览、右归类校准；通过入库或退回并写原因 */
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import request from '@/utils/request'
import { formatTime } from '@/utils/format'

const subjects = ref([])
const kps = ref([])
const queue = ref([])
const total = ref(0)
const cur = ref({})
const detail = ref({})
const subjectId = ref(null)
const type = ref('')
const reasonType = ref('')
const reason = ref('')
const acting = ref(false)

function subjectName(id) { return (subjects.value.find((s) => s.id === id) || {}).subjectName || '-' }
function kpName(id) { return (kps.value.find((k) => k.id === id) || {}).kpName || '-' }

async function load() {
  const d = await request.get('/api/question/page', {
    params: { page: 1, size: 50, status: '待审核', subjectId: subjectId.value, questionType: type.value }
  })
  queue.value = d.list || []
  total.value = d.total || 0
  if (queue.value.length && !queue.value.some((q) => q.id === cur.value.id)) pick(queue.value[0])
}

async function loadKps(sid) {
  const tree = await request.get('/api/knowledge-point/tree', { params: { subjectId: sid } })
  const flat = []
  const walk = (nodes) => nodes.forEach((n) => { flat.push({ id: n.id, kpName: n.kpName }); if (n.children) walk(n.children) })
  walk(tree || [])
  kps.value = flat
}

async function pick(q) {
  cur.value = { ...q }
  detail.value = await request.get('/api/question/' + q.id + '/detail')
  await loadKps(q.subjectId)
  reasonType.value = ''
  reason.value = ''
}

async function saveClassify() {
  await request.put('/api/question/' + cur.value.id, {
    knowledgePointId: cur.value.knowledgePointId,
    difficulty: cur.value.difficulty,
    sourceType: cur.value.sourceType
  })
  ElMessage.success('归类已更新')
  load()
}

async function audit(result) {
  if (result === '退回') {
    if (!reasonType.value) return ElMessage.warning('请选择退回原因分类')
    if (!reason.value || reason.value.trim().length < 5) return ElMessage.warning('退回说明不少于 5 字')
  }
  acting.value = true
  try {
    await request.post('/api/question/' + cur.value.id + '/audit', {
      result, reasonType: reasonType.value, reason: reason.value
    })
    ElMessage.success(result === '通过' ? '已通过并入库' : '已退回并通知提交人')
    cur.value = {}
    load()
  } finally {
    acting.value = false
  }
}

onMounted(async () => {
  subjects.value = (await request.get('/api/subject/list')) || []
  load()
})
</script>

<style scoped>
.three { display: grid; grid-template-columns: 260px 1fr 320px; gap: 16px; align-items: start; }
.three .card { margin-bottom: 0; }
.qrow { padding: 10px; border-radius: 8px; cursor: pointer; border-bottom: 1px solid #F2F4F6; }
.qrow:hover { background: #FAFBFC; }
.qrow.on { background: #F7F5FC; border-left: 3px solid var(--primary); }
.stem-box { font-size: 15px; line-height: 1.9; padding: 14px; background: #FAFBFC; border-radius: 8px; margin-bottom: 14px; }
.answer-box { background: #EAF4EF; border: 1px solid #C6E0D3; border-radius: 8px; padding: 11px; font-size: 13px; }
.analysis { font-size: 13px; line-height: 1.9; color: #3D4752; }
</style>
