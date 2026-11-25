<template>
  <div class="grid">
    <div class="card">
      <div class="card-h"><h2>批量导入题目</h2><span class="sub">粘贴 CSV，逐行校验题型、选项、答案与知识点</span></div>
      <div class="card-b">
        <div class="filter-bar" style="margin-bottom: 12px">
          <el-select v-model="subjectId" style="width: 200px">
            <el-option v-for="s in subjects" :key="s.id" :value="s.id" :label="s.subjectName" />
          </el-select>
          <el-button @click="fillTemplate">填充示例数据</el-button>
          <el-button @click="downloadTpl">下载模板</el-button>
          <el-button type="primary" :loading="importing" style="margin-left: auto" @click="doImport">
            开始导入
          </el-button>
        </div>
        <el-input v-model="csv" type="textarea" :rows="12" placeholder="表头：题型,题干,答案,解析,知识点,难度,分值
单选,设 f(x)=x²+2x，则 f'(1)=（ ）,B,求导后代入得 4，注意不要漏项,导数定义与计算,0.40,4.0" />
        <div class="muted" style="margin-top: 8px">
          校验规则：① 题型合法 ② 单选答案单字母、多选至少两项 ③ 题干 ≥8 字 ④ 解析 ≥20 字可入库 ⑤ 知识点须存在
        </div>
        <el-upload :show-file-list="false" :before-upload="onFile" style="margin-top: 10px">
          <el-button size="small">或选择 .csv/.txt 文件</el-button>
        </el-upload>
      </div>
    </div>

    <div class="card" style="align-self: start">
      <div class="card-h"><h2>导入结果</h2></div>
      <div class="card-b" v-if="result.taskId">
        <div style="display: flex; gap: 16px; margin-bottom: 12px">
          <div class="stat"><div class="muted">总行数</div><b class="num">{{ result.total }}</b></div>
          <div class="stat"><div class="muted">成功</div><b class="num" style="color: var(--ok)">{{ result.success }}</b></div>
          <div class="stat"><div class="muted">失败</div><b class="num" style="color: var(--danger)">{{ result.fail }}</b></div>
        </div>
        <div class="bar"><i :style="{ width: (result.success / Math.max(1, result.total)) * 100 + '%' }"></i></div>
        <div class="muted" style="margin: 10px 0 6px">失败行明细</div>
        <div v-if="result.fails && result.fails.length" class="fails">
          <div v-for="f in result.fails" :key="f">{{ f }}</div>
        </div>
        <el-alert v-else type="success" :closable="false" title="全部行导入成功，题目已进入待审核队列" />
        <el-button style="width: 100%; margin-top: 12px" @click="$router.push('/audit')">去审核台处理</el-button>
      </div>
      <div class="card-b" v-else>
        <el-empty description="粘贴数据并点击开始导入后展示结果" :image-size="70" />
      </div>
      <div class="card-h" style="border-top: 1px solid #EEF0F2"><h2>最近导入任务</h2></div>
      <div class="card-b" style="padding: 0">
        <div v-for="t in tasks" :key="t.id" class="task">
          <div style="display: flex; justify-content: space-between; font-size: 12px">
            <b>{{ t.fileName }}</b>
            <el-tag size="small" :type="statusType(t.status)" effect="light">{{ t.status }}</el-tag>
          </div>
          <div class="muted" style="margin-top: 4px">
            {{ formatTime(t.finishTime || t.createTime) }} · 成功 {{ t.successRows }} / 失败 {{ t.failRows }}
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
/** 批量导入：粘贴 CSV → 逐行校验 → 返回成功/失败明细，失败原因可直接修正后重传 */
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import request from '@/utils/request'
import { formatTime, statusType } from '@/utils/format'

const subjects = ref([])
const subjectId = ref(1)
const csv = ref('')
const importing = ref(false)
const result = ref({})
const tasks = ref([])

const SAMPLE = `题型,题干,答案,解析,知识点,难度,分值
单选,设 f(x)=x²+2x，则 f'(1) 的值为（ ）,B,f'(x)=2x+2，代入 x=1 得 4；也可用导数定义取极限验证。,导数定义与计算,0.40,4.0
多选,下列积分中可以使用分部积分法求解的有（ ）,"A,C",被积函数为代数乘超越函数时适用，A 与 C 均符合；B 宜用降幂公式。,分部积分法,0.62,5.0
填空,lim(x→0) sin3x/x = ____,3,利用重要极限，等价无穷小 sin3x ~ 3x，极限为 3。,两个重要极限,0.35,4.0`

function fillTemplate() { csv.value = SAMPLE }

function downloadTpl() {
  const blob = new Blob(['\ufeff' + SAMPLE], { type: 'text/csv;charset=utf-8' })
  const a = document.createElement('a')
  a.href = URL.createObjectURL(blob)
  a.download = '题目导入模板.csv'
  a.click()
}

function onFile(file) {
  const reader = new FileReader()
  reader.onload = () => { csv.value = String(reader.result || '') }
  reader.readAsText(file, 'utf-8')
  return false
}

function parseCsv(text) {
  const lines = text.split(/\r?\n/).filter((l) => l.trim())
  if (lines.length < 2) return []
  const rows = []
  for (const line of lines.slice(1)) {
    const cells = []
    let cur = ''
    let quoted = false
    for (let i = 0; i < line.length; i++) {
      const c = line[i]
      if (c === '"') quoted = !quoted
      else if (c === ',' && !quoted) { cells.push(cur); cur = '' }
      else cur += c
    }
    cells.push(cur)
    rows.push({
      questionType: cells[0]?.trim(),
      stem: cells[1]?.trim(),
      answer: cells[2]?.trim(),
      analysis: cells[3]?.trim(),
      knowledgePoint: cells[4]?.trim(),
      difficulty: cells[5]?.trim() || '0.60',
      score: cells[6]?.trim() || '5.0',
      sourceType: '自建'
    })
  }
  return rows
}

async function doImport() {
  const rows = parseCsv(csv.value)
  if (!rows.length) return ElMessage.warning('请粘贴至少一行数据')
  importing.value = true
  try {
    result.value = await request.post('/api/question/import', { subjectId: subjectId.value, fileName: '粘贴导入-' + Date.now() + '.csv', rows })
    ElMessage.success('导入完成：成功 ' + result.value.success + ' 行，失败 ' + result.value.fail + ' 行')
    loadTasks()
  } finally {
    importing.value = false
  }
}

async function loadTasks() {
  const d = await request.get('/api/import-task/page', { params: { page: 1, size: 5 } })
  tasks.value = d.list || []
}

onMounted(async () => {
  subjects.value = (await request.get('/api/subject/list')) || []
  subjectId.value = subjects.value[0]?.id || 1
  loadTasks()
})
</script>

<style scoped>
.grid { display: grid; grid-template-columns: 1fr 400px; gap: 16px; align-items: start; }
.grid .card { margin-bottom: 0; }
.stat b { font-size: 20px; color: var(--primary); }
.bar { height: 8px; background: #EDEFF2; border-radius: 4px; overflow: hidden; }
.bar i { display: block; height: 100%; background: var(--primary); }
.fails { max-height: 150px; overflow: auto; font-size: 11px; color: var(--danger); line-height: 1.9; }
.task { padding: 11px 16px; border-bottom: 1px solid #F2F4F6; }
</style>
