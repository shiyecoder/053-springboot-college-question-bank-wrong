<template>
  <div>
    <div class="card">
      <div class="card-b">
        <div class="filter-bar">
          <el-input v-model="q.kw" placeholder="题目编号 / 题干关键词" style="width: 230px" clearable @keyup.enter="reload" />
          <el-select v-model="q.subjectId" placeholder="全部学科" clearable style="width: 160px" @change="onSubject">
            <el-option v-for="s in subjects" :key="s.id" :value="s.id" :label="s.subjectName" />
          </el-select>
          <el-select v-model="q.knowledgePointId" placeholder="全部知识点" clearable filterable style="width: 190px">
            <el-option v-for="k in kps" :key="k.id" :value="k.id" :label="k.kpName" />
          </el-select>
          <el-select v-model="q.questionType" placeholder="全部题型" clearable style="width: 130px">
            <el-option v-for="t in types" :key="t" :value="t" :label="t" />
          </el-select>
          <el-select v-model="q.status" placeholder="全部状态" clearable style="width: 130px">
            <el-option v-for="t in ['草稿', '待审核', '已入库', '已停用', '已退回']" :key="t" :value="t" :label="t" />
          </el-select>
          <el-button type="primary" @click="reload">查询</el-button>
          <el-button @click="reset">重置</el-button>
          <el-button type="primary" plain style="margin-left: auto" @click="$router.push('/question/edit')">新增题目</el-button>
          <el-button @click="$router.push('/import')">批量导入</el-button>
        </div>
      </div>
    </div>

    <div class="card">
      <div class="card-h"><h2>题目列表</h2><span class="sub">共 {{ total }} 条</span>
        <span class="muted" style="margin-left: auto">题干相似度超过 85% 时保存会提示合并</span>
      </div>
      <el-table :data="rows" v-loading="loading" border style="width: 100%">
        <el-table-column prop="questionNo" label="题目编号" width="120" />
        <el-table-column label="学科" width="110">
          <template #default="{ row }">{{ subjectName(row.subjectId) }}</template>
        </el-table-column>
        <el-table-column label="知识点" width="130">
          <template #default="{ row }">{{ kpName(row.knowledgePointId) }}</template>
        </el-table-column>
        <el-table-column label="题型" width="86">
          <template #default="{ row }"><el-tag size="small" effect="light" :type="questionTypeTag(row.questionType)">{{ row.questionType }}</el-tag></template>
        </el-table-column>
        <el-table-column label="配图" width="88" align="center">
          <template #default="{ row }">
            <el-image v-if="figureIndex[row.id]" :src="figureIndex[row.id]" :preview-src-list="[figureIndex[row.id]]"
                      fit="cover" preview-teleported hide-on-click-modal
                      style="width: 56px; height: 40px; border-radius: 5px; display: block; margin: 0 auto" />
            <span v-else class="muted">—</span>
          </template>
        </el-table-column>
        <el-table-column prop="stem" label="题干" min-width="300" show-overflow-tooltip />
        <el-table-column prop="difficulty" label="难度" width="80" align="right">
          <template #default="{ row }"><span class="num">{{ Number(row.difficulty).toFixed(2) }}</span></template>
        </el-table-column>
        <el-table-column prop="score" label="分值" width="70" align="right">
          <template #default="{ row }"><span class="num">{{ Number(row.score).toFixed(1) }}</span></template>
        </el-table-column>
        <el-table-column label="状态" width="96">
          <template #default="{ row }">
            <el-tag size="small" effect="light" :type="statusType(row.status)">{{ row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="正确率" width="90" align="right">
          <template #default="{ row }">
            <span class="num">{{ row.correctRate > 0 ? Number(row.correctRate).toFixed(1) + '%' : '未测' }}</span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="$router.push('/question/edit/' + row.id)">编辑</el-button>
            <el-button link type="primary" @click="preview(row)">预览</el-button>
          </template>
        </el-table-column>
        <template #empty><el-empty description="当前筛选条件下没有题目，可清空筛选或新增" /></template>
      </el-table>
      <div style="display: flex; justify-content: flex-end; padding: 14px 16px">
        <el-pagination background layout="total, sizes, prev, pager, next" :total="total"
                       v-model:current-page="page" v-model:page-size="size" :page-sizes="[10, 20, 50]"
                       @current-change="load" @size-change="reload" />
      </div>
    </div>

    <el-drawer v-model="drawer" title="题目预览" size="520px">
      <template v-if="detail.question">
        <div style="display: flex; gap: 8px; margin-bottom: 14px">
          <el-tag size="small" effect="light">{{ detail.question.questionType }}</el-tag>
          <el-tag size="small" type="info" effect="plain">难度 {{ detail.question.difficulty }}</el-tag>
          <el-tag size="small" type="info" effect="plain">{{ detail.question.score }} 分</el-tag>
          <el-tag size="small" :type="statusType(detail.question.status)">{{ detail.question.status }}</el-tag>
        </div>
        <div style="font-size: 15px; line-height: 1.9; margin-bottom: 16px">{{ detail.question.stem }}</div>
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
      </template>
    </el-drawer>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import request from '@/utils/request'
import { questionTypeTag, statusType } from '@/utils/format'

const route = useRoute()
const types = ['单选', '多选', '判断', '填空', '简答', '计算']
const subjects = ref([])
const kps = ref([])
const rows = ref([])
const total = ref(0)
const page = ref(1)
const size = ref(10)
const loading = ref(false)
const drawer = ref(false)
const detail = ref({})
const figureIndex = ref({})
const q = reactive({ kw: '', subjectId: null, knowledgePointId: null, questionType: '', status: '' })

function subjectName(id) { return (subjects.value.find((s) => s.id === id) || {}).subjectName || '-' }
function kpName(id) { return (kps.value.find((k) => k.id === id) || {}).kpName || '-' }

async function load() {
  loading.value = true
  try {
    const d = await request.get('/api/question/page', {
      params: { page: page.value, size: size.value, ...q }
    })
    rows.value = d.list || []
    total.value = d.total || 0
  } finally {
    loading.value = false
  }
}
function reload() { page.value = 1; load() }

async function onSubject() {
  kps.value = []
  q.knowledgePointId = null
  if (q.subjectId) {
    const tree = await request.get('/api/knowledge-point/tree', { params: { subjectId: q.subjectId } })
    const flat = []
    const walk = (nodes) => nodes.forEach((n) => { flat.push({ id: n.id, kpName: n.kpName }); if (n.children) walk(n.children) })
    walk(tree || [])
    kps.value = flat
  }
  reload()
}

async function preview(row) {
  detail.value = await request.get('/api/question/' + row.id + '/detail')
  drawer.value = true
}

function reset() {
  Object.assign(q, { kw: '', subjectId: null, knowledgePointId: null, questionType: '', status: '' })
  kps.value = []
  reload()
}

onMounted(async () => {
  subjects.value = (await request.get('/api/subject/list')) || []
  // 图形题的选项配图索引，用于列表缩略图
  figureIndex.value = (await request.get('/api/question/figure-index')) || {}
  if (route.query.subjectId) q.subjectId = Number(route.query.subjectId)
  await onSubject()
  load()
})
</script>

<style scoped>
.answer-box { background: #EAF4EF; border: 1px solid #C6E0D3; border-radius: 8px; padding: 11px; font-size: 13px; }
.analysis { background: #FAFBFC; border-radius: 8px; padding: 12px; font-size: 13px; line-height: 1.9; }
</style>
