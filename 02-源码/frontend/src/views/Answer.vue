<template>
  <div v-if="record.id">
    <div class="hd">
      <div style="font-size: 14px; font-weight: 600">{{ record.practiceType }}</div>
      <el-tag size="small" effect="light" type="info">{{ record.recordNo }}</el-tag>
      <div class="timer" v-if="!submitted">
        剩余时间 <b class="num">{{ timeText }}</b><span class="muted">/ {{ duration }} 分钟</span>
      </div>
      <div style="margin-left: auto; display: flex; gap: 8px">
        <el-button v-if="!submitted" @click="saveProgress">保存作答</el-button>
        <el-button v-if="!submitted" type="primary" @click="submit">交卷</el-button>
        <el-button v-else @click="back">返回练习中心</el-button>
      </div>
    </div>

    <div class="body">
      <div>
        <div class="bar"><i :style="{ width: answeredPercent + '%' }"></i></div>
        <div class="muted" style="margin: 10px 0">
          第 {{ index + 1 }} / {{ questions.length }} 题 · 已答 {{ answeredCount }} 题 · 未答 {{ questions.length - answeredCount }} 题
        </div>

        <div class="card" v-if="curQ">
          <div class="card-b">
            <div style="display: flex; gap: 8px; margin-bottom: 14px">
              <el-tag size="small" effect="light">{{ curQ.questionType }}</el-tag>
              <el-tag size="small" type="info" effect="plain">{{ curQ.score }} 分</el-tag>
              <el-tag v-if="submitted" size="small" :type="curQ.isCorrect === 1 ? 'success' : 'danger'" effect="light">
                {{ curQ.isCorrect === 1 ? '答对' : (curQ.isCorrect === 2 ? '部分得分' : '答错') }}
              </el-tag>
            </div>
            <div class="stem">{{ curQ.stem }}</div>

            <template v-if="curQ.options && curQ.options.length">
              <div v-for="o in curQ.options" :key="o.id" class="option-card"
                   :class="optionClass(o)"
                   @click="!submitted && choose(curQ, o.optionLabel)">
                <span class="option-label">{{ o.optionLabel }}</span>
                <span style="flex: 1">{{ o.optionContent }}</span>
                <img v-if="o.imageUrl" :src="o.imageUrl" class="thumb" alt="" />
                <el-tag v-if="submitted && o.isCorrect === 1" size="small" type="success">正确答案</el-tag>
              </div>
            </template>
            <template v-else>
              <el-input v-if="curQ.questionType === '填空'" v-model="answers[curQ.id]" :disabled="submitted"
                        placeholder="填写答案" style="max-width: 420px" />
              <el-input v-else v-model="answers[curQ.id]" type="textarea" :rows="4" :disabled="submitted"
                        placeholder="写出解题过程与结果" />
            </template>

            <div v-if="submitted" class="result">
              <div class="row"><span class="muted">我的作答</span><b>{{ answers[curQ.id] || '未作答' }}</b></div>
              <div class="row"><span class="muted">标准答案</span><b>{{ curQ.answer }}</b></div>
              <div class="row" style="align-items: flex-start">
                <span class="muted">解析</span>
                <span style="flex: 1; line-height: 1.9">{{ curQ.analysis }}</span>
              </div>
            </div>

            <div class="nav">
              <el-button :disabled="index === 0" @click="index--">上一题</el-button>
              <el-button :disabled="index === questions.length - 1" type="primary" @click="index++">下一题</el-button>
            </div>
          </div>
        </div>
      </div>

      <div>
        <div class="card">
          <div class="card-h"><h2>答题卡</h2><span class="sub">{{ answeredCount }}/{{ questions.length }}</span></div>
          <div class="card-b">
            <div class="cards">
              <div v-for="(q, i) in questions" :key="q.id" class="cell" :class="cellClass(q, i)" @click="index = i">
                {{ i + 1 }}
              </div>
            </div>
            <div class="legend">
              <span><i class="dot done"></i>已答</span><span><i class="dot cur"></i>当前</span><span><i class="dot"></i>未答</span>
            </div>
          </div>
        </div>
        <div class="card" v-if="submitted">
          <div class="card-b">
            <div style="text-align: center">
              <div class="muted">本次得分</div>
              <div class="big num">{{ Number(result.gotScore || 0).toFixed(1) }}</div>
              <div class="muted">正确 {{ result.correctCount }} / {{ result.questionCount }}</div>
            </div>
            <el-button type="primary" style="width: 100%; margin-top: 12px" @click="$router.push('/wrong-book')">
              去错题本复习
            </el-button>
          </div>
        </div>
        <div class="card" v-else>
          <div class="card-b muted" style="line-height: 1.9">
            客观题提交后即时判分；填空按去空格比对；简答与计算按关键词命中比例给分，并展示命中项。
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
/** 答题页：逐题保存、答题卡定位、计时与交卷判分（同一练习重复提交返回首次结果） */
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import request from '@/utils/request'

const route = useRoute()
const router = useRouter()
const record = ref({})
const questions = ref([])
const answers = ref({})
const index = ref(0)
const submitted = ref(false)
const result = ref({})
const now = ref(Date.now())
const duration = ref(60)
let timer = null
let tick = null
const KEY = 'qb_answer_' + route.params.recordId

const curQ = computed(() => questions.value[index.value] || null)
const answeredCount = computed(() => questions.value.filter((q) => answers.value[q.id]).length)
const answeredPercent = computed(() => questions.value.length ? answeredCount.value / questions.value.length * 100 : 0)
const timeText = computed(() => {
  const start = record.value.startTime ? new Date(record.value.startTime.replace(/-/g, '/')).getTime() : Date.now()
  const total = duration.value * 60 - Math.floor((now.value - start) / 1000)
  const left = Math.max(0, total)
  return String(Math.floor(left / 60)).padStart(2, '0') + ':' + String(left % 60).padStart(2, '0')
})

function optionClass(o) {
  const mine = (answers.value[curQ.value.id] || '').includes(o.optionLabel)
  if (submitted.value) {
    if (o.isCorrect === 1) return 'is-right'
    if (mine) return 'is-wrong'
    return ''
  }
  return mine ? 'is-sel' : ''
}
function cellClass(q, i) {
  if (submitted.value) return q.isCorrect === 1 ? 'ok' : 'bad'
  if (i === index.value) return 'cur'
  return answers.value[q.id] ? 'done' : ''
}
function choose(q, label) {
  if (q.questionType === '多选') {
    const set = new Set((answers.value[q.id] || '').split(',').filter(Boolean))
    if (set.has(label)) set.delete(label)
    else set.add(label)
    answers.value[q.id] = [...set].sort().join(',')
  } else {
    answers.value[q.id] = label
  }
  saveProgress(true)
}

function saveProgress(silent) {
  localStorage.setItem(KEY, JSON.stringify(answers.value))
  if (!silent) ElMessage.success('作答已保存，刷新后可恢复')
}

async function submit() {
  const unanswered = questions.value.length - answeredCount.value
  await ElMessageBox.confirm(
    unanswered > 0 ? '还有 ' + unanswered + ' 题未作答，仍要交卷吗？' : '确认交卷？交卷后不可修改。',
    '交卷确认', { type: 'warning' })
  const list = questions.value.map((q) => ({ questionId: q.id, answer: answers.value[q.id] || '' }))
  const used = record.value.startTime
    ? Math.floor((Date.now() - new Date(record.value.startTime.replace(/-/g, '/')).getTime()) / 1000)
    : 0
  result.value = await request.post('/api/practice-record/' + route.params.recordId + '/submit',
    { answers: list, usedSeconds: used })
  submitted.value = true
  localStorage.removeItem(KEY)
  ElMessage.success('交卷完成，得分 ' + result.value.gotScore)
  await load()
}

async function load() {
  const d = await request.get('/api/practice-record/' + route.params.recordId + '/detail')
  record.value = d.record
  questions.value = d.questions || []
  for (const q of questions.value) {
    if (q.myAnswer) answers.value[q.id] = q.myAnswer
    if (q.isCorrect !== null && q.isCorrect !== undefined) submitted.value = true
  }
  if (!submitted.value) {
    const saved = localStorage.getItem(KEY)
    if (saved) {
      try {
        Object.assign(answers.value, JSON.parse(saved))
        ElMessage.info('已恢复上次作答进度')
      } catch (e) { /* 忽略损坏的本地缓存 */ }
    }
  } else {
    result.value = { gotScore: record.value.gotScore, correctCount: record.value.correctCount, questionCount: record.value.questionCount }
  }
}

function back() { router.push('/practice') }

onMounted(async () => {
  await load()
  tick = setInterval(() => { now.value = Date.now() }, 1000)
  // 超过建议时长 2 倍自动交卷
  timer = setInterval(() => {
    if (submitted.value) return
    const start = record.value.startTime ? new Date(record.value.startTime.replace(/-/g, '/')).getTime() : Date.now()
    if (Date.now() - start > duration.value * 2 * 60 * 1000) {
      ElMessage.warning('已超过建议时长 2 倍，系统自动交卷')
      submit()
    }
  }, 30000)
})
onBeforeUnmount(() => {
  clearInterval(tick)
  clearInterval(timer)
})
</script>

<style scoped>
.hd {
  height: 56px; background: #fff; border-radius: 10px; border: 1px solid var(--border);
  display: flex; align-items: center; padding: 0 18px; gap: 12px; margin-bottom: 14px;
}
.timer { margin-left: 16px; font-size: 13px; }
.timer b { font-size: 18px; color: var(--primary); margin: 0 4px; }
.body { display: grid; grid-template-columns: 1fr 268px; gap: 16px; align-items: start; }
.stem { font-size: 15px; line-height: 1.95; margin-bottom: 16px; }
.nav { display: flex; gap: 10px; margin-top: 20px; }
.nav .el-button:last-child { margin-left: auto; }
.result { margin-top: 16px; background: #FAFBFC; border-radius: 8px; padding: 12px; }
.result .row { display: flex; gap: 14px; font-size: 13px; margin-bottom: 8px; }
.result .row .muted { width: 64px; flex: none; }
.cards { display: grid; grid-template-columns: repeat(5, 1fr); gap: 7px; }
.cell {
  height: 30px; border-radius: 6px; display: flex; align-items: center; justify-content: center;
  font-size: 12px; border: 1px solid var(--border); cursor: pointer; background: #fff; color: var(--muted);
}
.cell.done { background: #EAF4EF; border-color: #C6E0D3; color: var(--ok); }
.cell.cur { background: var(--primary); border-color: var(--primary); color: #fff; }
.cell.ok { background: #EAF4EF; border-color: #C6E0D3; color: var(--ok); }
.cell.bad { background: #FBEBED; border-color: #EFC9CE; color: var(--danger); }
.legend { display: flex; gap: 14px; margin-top: 14px; font-size: 11px; color: var(--muted); align-items: center; }
.dot { width: 10px; height: 10px; border-radius: 3px; border: 1px solid var(--border); display: inline-block; margin-right: 4px; }
.dot.done { background: #EAF4EF; border-color: #C6E0D3; }
.dot.cur { background: var(--primary); border-color: var(--primary); }
.bar { height: 8px; background: #EDEFF2; border-radius: 4px; overflow: hidden; }
.bar i { display: block; height: 100%; background: var(--accent); }
.big { font-size: 30px; font-weight: 700; color: var(--primary); margin: 4px 0; }
</style>
