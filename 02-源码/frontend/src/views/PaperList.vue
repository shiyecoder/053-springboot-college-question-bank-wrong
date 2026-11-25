<template>
  <div>
    <div class="card">
      <div class="card-b">
        <div class="filter-bar">
          <el-input v-model="q.kw" placeholder="试卷编号 / 名称" style="width: 220px" clearable @keyup.enter="reload" />
          <el-select v-model="q.subjectId" placeholder="全部学科" clearable style="width: 160px">
            <el-option v-for="s in subjects" :key="s.id" :value="s.id" :label="s.subjectName" />
          </el-select>
          <el-select v-model="q.buildMode" placeholder="全部组卷方式" clearable style="width: 150px">
            <el-option v-for="t in ['手动', '随机', '错题重练']" :key="t" :value="t" :label="t" />
          </el-select>
          <el-select v-model="q.status" placeholder="全部状态" clearable style="width: 140px">
            <el-option v-for="t in ['草稿', '待审核', '已发布', '使用中', '已归档', '已驳回']" :key="t" :value="t" :label="t" />
          </el-select>
          <el-button type="primary" @click="reload">查询</el-button>
          <el-button @click="reset">重置</el-button>
          <el-button type="primary" plain style="margin-left: auto" @click="$router.push('/paper/workbench')">新建试卷</el-button>
        </div>
      </div>
    </div>

    <div class="card">
      <div class="card-h"><h2>试卷列表</h2><span class="sub">共 {{ total }} 条</span></div>
      <el-table :data="rows" v-loading="loading" border style="width: 100%">
        <el-table-column prop="paperNo" label="试卷编号" width="130" />
        <el-table-column prop="paperName" label="试卷名称" min-width="230" show-overflow-tooltip />
        <el-table-column label="学科" width="110">
          <template #default="{ row }">{{ subjectName(row.subjectId) }}</template>
        </el-table-column>
        <el-table-column label="组卷方式" width="100">
          <template #default="{ row }"><el-tag size="small" effect="plain" type="info">{{ row.buildMode }}</el-tag></template>
        </el-table-column>
        <el-table-column prop="questionCount" label="题数" width="70" align="right" />
        <el-table-column prop="totalScore" label="总分" width="76" align="right">
          <template #default="{ row }">{{ Number(row.totalScore).toFixed(1) }}</template>
        </el-table-column>
        <el-table-column prop="durationMin" label="时长" width="80" align="right">
          <template #default="{ row }">{{ row.durationMin }} 分钟</template>
        </el-table-column>
        <el-table-column label="状态" width="96">
          <template #default="{ row }"><el-tag size="small" effect="light" :type="statusType(row.status)">{{ row.status }}</el-tag></template>
        </el-table-column>
        <el-table-column label="操作" width="210" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="$router.push('/paper/' + row.id)">查看</el-button>
            <el-button link type="primary" @click="coverage(row)">覆盖度</el-button>
            <el-dropdown @command="(c) => transition(row, c)">
              <el-button link type="primary">流转<el-icon><ArrowDown /></el-icon></el-button>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item v-for="t in allowed(row.status)" :key="t" :command="t">{{ t }}</el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </template>
        </el-table-column>
        <template #empty><el-empty description="当前筛选条件下没有试卷" /></template>
      </el-table>
      <div style="display: flex; justify-content: flex-end; padding: 14px 16px">
        <el-pagination background layout="total, sizes, prev, pager, next" :total="total"
                       v-model:current-page="page" v-model:page-size="size" :page-sizes="[10, 20, 50]"
                       @current-change="load" @size-change="reload" />
      </div>
    </div>

    <el-drawer v-model="drawer" title="知识点覆盖度" size="460px">
      <div v-if="cov.paperName">
        <div style="font-weight: 600">{{ cov.paperName }}</div>
        <div class="muted" style="margin: 6px 0 14px">
          共 {{ cov.questionCount }} 题 · 总分 {{ cov.totalScore }} · 难度均值 {{ cov.difficultyAvg }}
        </div>
        <div style="display: flex; gap: 10px; margin-bottom: 14px">
          <el-tag type="success" effect="light">易 {{ cov.distribution?.easy }}</el-tag>
          <el-tag type="warning" effect="light">中 {{ cov.distribution?.medium }}</el-tag>
          <el-tag type="danger" effect="light">难 {{ cov.distribution?.hard }}</el-tag>
        </div>
        <el-table :data="cov.kps" border size="small">
          <el-table-column prop="kpName" label="知识点" />
          <el-table-column prop="count" label="题数" width="70" align="right" />
          <el-table-column label="占比" width="110" align="right">
            <template #default="{ row }">{{ row.percent }}%</template>
          </el-table-column>
        </el-table>
        <div class="muted" style="margin-top: 12px">考纲权重对比</div>
        <div v-if="cov.gaps && cov.gaps.length" style="margin-top: 8px">
          <el-alert v-for="g in cov.gaps" :key="g" type="warning" :closable="false" :title="g" style="margin-bottom: 6px" />
        </div>
        <el-alert v-else type="success" :closable="false" title="各知识点占比均不低于考纲权重" style="margin-top: 8px" />
      </div>
    </el-drawer>
  </div>
</template>

<script setup>
/** 试卷管理：状态机流转（草稿→待审核→已发布→使用中→已归档，待审核→已驳回） */
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import request from '@/utils/request'
import { statusType } from '@/utils/format'

const subjects = ref([])
const rows = ref([])
const total = ref(0)
const page = ref(1)
const size = ref(10)
const loading = ref(false)
const drawer = ref(false)
const cov = ref({})
const q = reactive({ kw: '', subjectId: null, buildMode: '', status: '' })

const FLOW = {
  草稿: ['待审核'], 待审核: ['已发布', '已驳回'], 已驳回: ['待审核'],
  已发布: ['使用中', '已归档'], 使用中: ['已归档'], 已归档: []
}
function allowed(s) { return FLOW[s] || [] }
function subjectName(id) { return (subjects.value.find((s) => s.id === id) || {}).subjectName || '-' }

async function load() {
  loading.value = true
  try {
    const d = await request.get('/api/paper/page', { params: { page: page.value, size: size.value, ...q } })
    rows.value = d.list || []
    total.value = d.total || 0
  } finally {
    loading.value = false
  }
}
function reload() { page.value = 1; load() }
function reset() { Object.assign(q, { kw: '', subjectId: null, buildMode: '', status: '' }); reload() }

async function transition(row, target) {
  let reason = ''
  if (target === '已驳回') {
    const r = await ElMessageBox.prompt('驳回必须填写不少于 5 字的原因', '驳回试卷', {
      inputPattern: /^.{5,}$/, inputErrorMessage: '原因不少于 5 字'
    })
    reason = r.value
  } else {
    await ElMessageBox.confirm('确认将试卷流转为「' + target + '」？', '状态流转', { type: 'warning' })
  }
  await request.post('/api/paper/' + row.id + '/transition', { targetStatus: target, reason })
  ElMessage.success('已流转为 ' + target)
  load()
}

async function coverage(row) {
  cov.value = await request.get('/api/paper/' + row.id + '/coverage')
  drawer.value = true
}

onMounted(async () => {
  subjects.value = (await request.get('/api/subject/list')) || []
  load()
})
</script>
