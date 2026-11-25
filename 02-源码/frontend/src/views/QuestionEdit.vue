<template>
  <div>
    <div class="steps">
      <div class="s on"><span class="n">1</span>录入题干</div>
      <div class="s" :class="{ on: form.stem && form.answer }"><span class="n">2</span>设置选项与答案</div>
      <div class="s" :class="{ on: form.analysis && form.analysis.length >= 20 }"><span class="n">3</span>解析与知识点</div>
      <div class="s"><span class="n">4</span>提交审核</div>
    </div>

    <div class="two">
      <div class="card">
        <div class="card-h"><h2>录入题目</h2><span class="sub">保存时逐项校验并定位错误项</span></div>
        <div class="card-b">
          <el-form :model="form" label-width="112px">
            <el-form-item label="学科" required>
              <el-select v-model="form.subjectId" style="width: 240px" @change="onSubject">
                <el-option v-for="s in subjects" :key="s.id" :value="s.id" :label="s.subjectName" />
              </el-select>
            </el-form-item>
            <el-form-item label="知识点" required>
              <el-select v-model="form.knowledgePointId" filterable style="width: 380px" placeholder="请选择知识点">
                <el-option v-for="k in kps" :key="k.id" :value="k.id" :label="k.kpName" />
              </el-select>
            </el-form-item>
            <el-form-item label="题型" required>
              <el-select v-model="form.questionType" style="width: 140px" @change="onType">
                <el-option v-for="t in types" :key="t" :value="t" :label="t" />
              </el-select>
              <el-select v-model="form.sourceType" style="width: 140px; margin-left: 8px">
                <el-option v-for="t in ['自建', '真题', '教材', '引进']" :key="t" :value="t" :label="t" />
              </el-select>
            </el-form-item>
            <el-form-item label="题干" required>
              <el-input v-model="form.stem" type="textarea" :rows="4" placeholder="不少于 8 字，公式用文字描述" @input="checkSimilar" />
              <div class="muted">已输入 {{ (form.stem || '').length }} 字</div>
            </el-form-item>

            <el-form-item v-if="hasOptions" label="选项" required>
              <div style="width: 100%">
                <div v-for="(o, i) in form.options" :key="i" class="option-card">
                  <el-radio v-if="form.questionType === '单选'" :model-value="form.answer" :label="o.label"
                            @change="form.answer = o.label"><span></span></el-radio>
                  <el-checkbox v-else :model-value="form.answer.includes(o.label)"
                               @change="(v) => toggleMulti(o.label, v)"><span></span></el-checkbox>
                  <span class="option-label">{{ o.label }}</span>
                  <el-input v-model="o.content" placeholder="选项内容" style="flex: 1" />
                  <el-button link type="danger" @click="removeOption(i)">删除</el-button>
                </div>
                <el-button size="small" @click="addOption">+ 添加选项</el-button>
                <div class="muted" style="margin-top: 8px">
                  单选题必须且只能有一个正确项，多选题至少两个；判断题固定两个选项。
                </div>
              </div>
            </el-form-item>

            <el-form-item label="标准答案" required>
              <el-input v-model="form.answer" :placeholder="answerHint" style="width: 380px" />
            </el-form-item>
            <el-form-item label="难度系数">
              <el-slider v-model="difficulty" :min="10" :max="100" :step="1" style="width: 300px" />
              <span class="num" style="margin-left: 12px">{{ (difficulty / 100).toFixed(2) }}</span>
            </el-form-item>
            <el-form-item label="分值">
              <el-input-number v-model="form.score" :min="1" :max="50" :step="0.5" style="width: 140px" />
            </el-form-item>
            <el-form-item label="解析" required>
              <el-input v-model="form.analysis" type="textarea" :rows="3" placeholder="入库前必填，至少 20 字说明解题步骤" />
              <div class="muted">已输入 {{ (form.analysis || '').length }} 字（要求 ≥20）</div>
            </el-form-item>
          </el-form>
          <div style="display: flex; gap: 8px; padding-left: 112px">
            <el-button type="primary" :loading="saving" @click="save('草稿')">保存草稿</el-button>
            <el-button type="warning" :loading="saving" @click="save('待审核')">提交审核</el-button>
            <el-button @click="$router.back()">返回</el-button>
          </div>
        </div>
      </div>

      <div class="card" style="align-self: start">
        <div class="card-h"><h2>学生端预览</h2><span class="sub">实时</span></div>
        <div class="card-b">
          <div style="display: flex; gap: 8px; margin-bottom: 12px">
            <el-tag size="small" effect="light">{{ form.questionType }}</el-tag>
            <el-tag size="small" type="info" effect="plain">难度 {{ (difficulty / 100).toFixed(2) }}</el-tag>
            <el-tag size="small" type="info" effect="plain">{{ form.score }} 分</el-tag>
          </div>
          <div style="font-size: 14px; line-height: 1.9; margin-bottom: 14px">
            {{ form.stem || '题干预览区，输入后实时显示' }}
          </div>
          <div v-for="o in form.options" :key="o.label" class="option-card"
               :class="{ 'is-right': form.answer.includes(o.label) }">
            <span class="option-label">{{ o.label }}</span>
            <span style="flex: 1">{{ o.content || '选项内容' }}</span>
          </div>
          <el-alert v-if="similar" type="warning" :closable="false" style="margin-top: 12px"
                    :title="'与已有题目相似度 ' + similar + '%，可合并到原题或填写差异说明后强制入库'" />
          <div class="muted" style="margin-top: 12px">相似度检测：与同学科题干比对，保存时自动执行。</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
/** 题目编辑：左录入右预览，选项按题型动态校验，保存后写草稿或提交审核 */
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import request from '@/utils/request'

const route = useRoute()
const router = useRouter()
const types = ['单选', '多选', '判断', '填空', '简答', '计算']
const subjects = ref([])
const kps = ref([])
const saving = ref(false)
const similar = ref(0)
const diffNote = ref('')
const difficulty = ref(60)
const form = ref({
  subjectId: null, knowledgePointId: null, questionType: '单选', stem: '', answer: '',
  analysis: '', score: 5, sourceType: '自建', options: []
})

const hasOptions = computed(() => ['单选', '多选', '判断'].includes(form.value.questionType))
const answerHint = computed(() => ({
  单选: '单选填 A', 多选: '按字母升序，逗号分隔，如 A,C', 判断: '填 对 或 错',
  填空: '多个空用分号分隔', 简答: '关键词用逗号分隔，用于命中判分', 计算: '写出最终结果与关键步骤'
}[form.value.questionType] || ''))

function addOption() {
  const label = String.fromCharCode(65 + form.value.options.length)
  form.value.options.push({ label, content: '' })
}
function removeOption(i) {
  form.value.options.splice(i, 1)
  form.value.options.forEach((o, idx) => { o.label = String.fromCharCode(65 + idx) })
}
function toggleMulti(label, checked) {
  const set = new Set((form.value.answer || '').split(',').filter(Boolean))
  if (checked) set.add(label)
  else set.delete(label)
  form.value.answer = [...set].sort().join(',')
}
function onType(t) {
  if (['单选', '多选', '判断'].includes(t)) {
    if (!form.value.options.length) {
      if (t === '判断') {
        form.value.options = [{ label: 'A', content: '对' }, { label: 'B', content: '错' }]
      } else {
        form.value.options = ['A', 'B', 'C', 'D'].map((l) => ({ label: l, content: '' }))
      }
    }
    if (t === '判断') form.value.options = [{ label: 'A', content: '对' }, { label: 'B', content: '错' }]
  } else {
    form.value.options = []
  }
  form.value.answer = ''
}

async function onSubject() {
  const tree = await request.get('/api/knowledge-point/tree', { params: { subjectId: form.value.subjectId } })
  const flat = []
  const walk = (nodes) => nodes.forEach((n) => { flat.push({ id: n.id, kpName: n.kpName, level: n.kpLevel }); if (n.children) walk(n.children) })
  walk(tree || [])
  kps.value = flat
}

/** 题干相似度校验：与同学科已有题目比对，超过 85% 时提示合并或填写差异说明 */
let simTimer = null
const similarInfo = ref(null)
function checkSimilar() {
  clearTimeout(simTimer)
  simTimer = setTimeout(async () => {
    const f = form.value
    if (!f.stem || f.stem.trim().length < 8 || !f.subjectId) {
      similar.value = 0
      similarInfo.value = null
      return
    }
    try {
      const r = await request.get('/api/question/similar', {
        params: { stem: f.stem, subjectId: f.subjectId, excludeId: route.params.id || undefined }
      })
      similarInfo.value = r
      similar.value = r && r.rate >= 60 ? Number(r.rate) : 0
    } catch (e) {
      similar.value = 0
    }
  }, 500)
}

async function save(status) {  const f = form.value
  if (!f.subjectId) return ElMessage.warning('请选择学科')
  if (!f.knowledgePointId) return ElMessage.warning('请选择知识点')
  if (!f.stem || f.stem.length < 8) return ElMessage.warning('题干不少于 8 字')
  if (hasOptions.value) {
    const filled = f.options.filter((o) => o.content.trim())
    if (filled.length < 2) return ElMessage.warning('至少填写 2 个选项')
    if (f.questionType === '单选' && f.answer.split(',').filter(Boolean).length !== 1)
      return ElMessage.warning('单选题必须且只能有一个正确项')
    if (f.questionType === '多选' && f.answer.split(',').filter(Boolean).length < 2)
      return ElMessage.warning('多选题至少两个正确项')
  }
  if (!f.answer) return ElMessage.warning('请填写标准答案')
  // 相似度超过 85% 时要求确认：合并到原题或填写差异说明后强制入库
  if (similar.value >= 85 && similarInfo.value) {
    const act = await ElMessageBox.confirm(
      `与题目「${similarInfo.value.questionNo}」题干相似度 ${similar.value}%，疑似重复，请选择处理方式。`,
      '疑似重复题目',
      { confirmButtonText: '填写差异说明并继续入库', cancelButtonText: '合并到原题', distinguishCancelAndClose: true, type: 'warning' }
    ).then(() => 'force').catch((a) => (a === 'cancel' ? 'merge' : 'abort'))
    if (act === 'abort') return
    if (act === 'merge') {
      router.push('/question/edit/' + similarInfo.value.id)
      return
    }
    const r = await ElMessageBox.prompt('请说明本题与原题的区别（不少于 5 字），将记入操作日志', '差异说明', {
      inputValidator: (v) => (v && v.trim().length >= 5) || '至少填写 5 个字'
    }).catch(() => null)
    if (!r || !r.value) return
    diffNote.value = r.value.trim()
  }
  if (status === '待审核' && (!f.analysis || f.analysis.length < 20))
    return ElMessage.warning('提交审核前解析不少于 20 字')
  saving.value = true
  try {
    const payload = {
      ...f,
      difficulty: Number((difficulty.value / 100).toFixed(2)),
      status,
      correctRate: 0,
      options: undefined
    }
    let id = route.params.id
    if (id) await request.put('/api/question/' + id, payload)
    else {
      const created = await request.post('/api/question', payload)
      id = created.id
    }
    // 选项单独维护，先删后插保证一致性
    const old = await request.get('/api/question/' + id + '/detail')
    for (const o of old.options || []) await request.delete('/api/question-option/' + o.id)
    for (let i = 0; i < f.options.length; i++) {
      const o = f.options[i]
      if (!o.content.trim()) continue
      await request.post('/api/question-option', {
        questionId: Number(id),
        optionLabel: o.label,
        optionContent: o.content,
        isCorrect: f.answer.includes(o.label) ? 1 : 0,
        sortNo: i + 1
      })
    }
    // 差异说明记入操作日志，便于事后追溯重复题判断依据
    if (diffNote.value) await request.post('/api/question/' + id + '/diff-note', { note: diffNote.value })
    ElMessage.success(status === '草稿' ? '草稿已保存' : '已提交审核，等待教研员处理')
    router.push('/question')
  } finally {
    saving.value = false
  }
}

onMounted(async () => {
  subjects.value = (await request.get('/api/subject/list')) || []
  form.value.subjectId = subjects.value[0]?.id || null
  await onSubject()
  onType('单选')
  if (subjects.value[0]?.id) form.value.knowledgePointId = kps.value[0]?.id || null
  if (route.params.id) {
    const d = await request.get('/api/question/' + route.params.id + '/detail')
    const q = d.question
    form.value = {
      ...q,
      options: (d.options || []).map((o) => ({ label: o.optionLabel, content: o.optionContent }))
    }
    difficulty.value = Math.round(Number(q.difficulty) * 100)
    await onSubject()
    checkSimilar()
  }
})
</script>

<style scoped>
.steps { display: flex; margin-bottom: 16px; }
.steps .s { flex: 1; display: flex; align-items: center; gap: 8px; font-size: 12px; color: var(--muted); }
.steps .s .n {
  width: 22px; height: 22px; border-radius: 50%; border: 1px solid #D6DAE0;
  display: flex; align-items: center; justify-content: center; font-size: 11px;
}
.steps .s.on { color: var(--primary); font-weight: 600; }
.steps .s.on .n { background: var(--primary); border-color: var(--primary); color: #fff; }
.steps .s::after { content: ''; flex: 1; height: 1px; background: var(--border); margin: 0 10px; }
.steps .s:last-child::after { display: none; }
.two { display: grid; grid-template-columns: 1fr 400px; gap: 16px; align-items: start; }
</style>
