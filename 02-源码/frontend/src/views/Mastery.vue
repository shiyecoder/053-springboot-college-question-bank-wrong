<template>
  <div>
    <div class="filter-bar" style="margin-bottom: 14px">
      <el-select v-model="subjectId" style="width: 170px" @change="load">
        <el-option v-for="s in subjects" :key="s.id" :value="s.id" :label="s.subjectName" />
      </el-select>
      <el-select v-model="studentId" style="width: 220px" filterable @change="load">
        <el-option v-for="s in students" :key="s.id" :value="s.id" :label="s.realName + '（' + (s.username) + '）'" />
      </el-select>
      <el-button type="primary" @click="load">查询</el-button>
      <el-button :loading="recomputing" @click="recompute">重新计算</el-button>
      <el-button v-if="isAdmin" :loading="batchRunning" @click="recomputeAll">全量重算</el-button>
      <span class="muted" style="margin-left: auto">
        规则版本 {{ data.ruleVersion }} · 样本 {{ data.measuredCount }}/{{ data.totalCount }} 个知识点
      </span>
    </div>

    <div class="grid">
      <div class="card">
        <div class="card-h"><h2>知识点掌握度雷达</h2><span class="sub">{{ data.studentName }} · {{ data.subjectName }}</span></div>
        <div class="card-b"><ChartBox :option="radarOption" :height="270" /></div>
      </div>
      <div class="card">
        <div class="card-h"><h2>薄弱知识点清单</h2>
          <span class="sub" v-if="data.weak">共 {{ data.weak.length }} 项</span>
        </div>
        <el-table :data="data.weak || []" border size="small" height="270">
          <el-table-column prop="kpName" label="知识点" min-width="120" />
          <el-table-column label="掌握度" width="130">
            <template #default="{ row }">
              <div style="display: flex; align-items: center; gap: 6px">
                <div class="bar" style="width: 54px"><i :style="{ width: row.totalScore + '%', background: masteryColor(row.totalScore) }"></i></div>
                <b class="num">{{ row.totalScore }}</b>
              </div>
            </template>
          </el-table-column>
          <el-table-column prop="sampleCount" label="样本" width="66" align="right" />
          <el-table-column label="等级" width="96">
            <template #default="{ row }">
              <el-tag size="small" :type="statusType(row.level)" effect="light">{{ row.level }}</el-tag>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </div>

    <div class="card">
      <div class="card-h"><h2>五项因子计算留痕</h2>
        <span class="sub">掌握度 = Σ(单项归一化得分 × 权重)，权重合计 100</span>
        <span style="margin-left: auto"><el-button size="small" @click="$router.push('/rule-config')">规则配置</el-button></span>
      </div>
      <el-table :data="data.items || []" border style="width: 100%" max-height="420">
        <el-table-column prop="kpName" label="知识点" min-width="130" fixed />
        <el-table-column label="正确率 40%" width="120" align="right">
          <template #default="{ row }"><span class="num">{{ row.accuracyScore }}</span>
            <div class="muted">{{ row.accuracyRate }}% · {{ row.sampleCount }} 次</div></template>
        </el-table-column>
        <el-table-column prop="timeScore" label="耗时 15%" width="96" align="right" />
        <el-table-column prop="redoScore" label="重做 20%" width="96" align="right" />
        <el-table-column prop="weightScore" label="考纲权重 15%" width="120" align="right" />
        <el-table-column label="复习 10%" width="110" align="right">
          <template #default="{ row }"><span class="num">{{ row.reviewScore }}</span>
            <div class="muted">{{ row.planDone }}/{{ row.planTotal }}</div></template>
        </el-table-column>
        <el-table-column label="总分" width="90" align="right">
          <template #default="{ row }"><b class="num" :style="{ color: masteryColor(row.totalScore) }">{{ row.totalScore }}</b></template>
        </el-table-column>
        <el-table-column label="等级" width="110">
          <template #default="{ row }">
            <el-tag size="small" :type="statusType(row.level)" effect="light">{{ row.level }}</el-tag>
            <el-tag v-if="row.manual" size="small" type="warning" effect="plain" style="margin-left: 4px">已修正</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="结论与建议" min-width="280" show-overflow-tooltip>
          <template #default="{ row }">
            <span v-if="row.insufficient" class="muted">数据不足（样本 {{ row.sampleCount }} 次）· </span>{{ row.suggestion }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="110" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" :disabled="!row.resultId" @click="openManual(row)">人工修正</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <el-dialog v-model="dialog" title="人工修正掌握等级" width="520px">
      <el-alert type="warning" :closable="false" style="margin-bottom: 12px"
                title="原始计算结果保留不被覆盖，修正原因不少于 5 字，将写入变更记录。" />
      <el-form label-width="90px">
        <el-form-item label="知识点">{{ cur.kpName }}</el-form-item>
        <el-form-item label="系统结论">
          {{ cur.rawLevel }}（{{ cur.totalScore }} 分）
        </el-form-item>
        <el-form-item label="修正为">
          <el-select v-model="manualLevel" style="width: 200px">
            <el-option v-for="l in ['已掌握', '基本掌握', '薄弱', '严重薄弱']" :key="l" :value="l" :label="l" />
          </el-select>
        </el-form-item>
        <el-form-item label="修正原因">
          <el-input v-model="manualReason" type="textarea" :rows="3" placeholder="不少于 5 字，例如：教学进度滞后导致正确率偏低" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialog = false">取消</el-button>
        <el-button type="primary" @click="saveManual">提交修正</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
/** 学情诊断（教师端）：雷达 + 薄弱清单 + 五因子留痕 + 人工修正 */
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import request from '@/utils/request'
import ChartBox from '@/components/ChartBox.vue'
import { masteryColor, statusType } from '@/utils/format'

const subjects = ref([])
const students = ref([])
const subjectId = ref(1)
const studentId = ref(null)
const data = ref({})
const dialog = ref(false)
const cur = ref({})
const manualLevel = ref('')
const manualReason = ref('')
const recomputing = ref(false)
const batchRunning = ref(false)
const isAdmin = (JSON.parse(localStorage.getItem('qb_user') || '{}').roleCode === 'ADMIN')

const radarOption = computed(() => {
  const items = (data.value.items || []).filter((i) => i.level !== '未测').slice(0, 6)
  return {
    color: ['#4B3F72'],
    tooltip: {},
    radar: {
      radius: '64%', center: ['50%', '55%'],
      indicator: items.length ? items.map((i) => ({ name: i.kpName, max: 100 })) : [{ name: '暂无数据', max: 100 }],
      axisName: { fontSize: 10, color: '#5B6770' },
      splitLine: { lineStyle: { color: '#E4E7EB' } }, splitArea: { show: false },
      axisLine: { lineStyle: { color: '#E4E7EB' } }
    },
    series: [{
      type: 'radar', data: [{ value: items.map((i) => i.totalScore), name: '掌握度' }],
      areaStyle: { opacity: 0.2 }, symbolSize: 4, lineStyle: { width: 2 }
    }]
  }
})

async function load() {
  if (!studentId.value) return
  data.value = await request.get('/api/student/' + studentId.value + '/mastery', { params: { subjectId: subjectId.value } })
}

/** 全量重算：等同于每日 02:00 的定时任务，变化超过 10 分的知识点会给负责教师推送复核消息 */
async function recomputeAll() {
  batchRunning.value = true
  try {
    const r = await request.post('/api/mastery/recompute-all')
    ElMessage.success(`已重算 ${r.students} 名学生、${r.rows} 条诊断，${r.changed} 个知识点变化超过 10 分`)
    load()
  } finally {
    batchRunning.value = false
  }
}

async function recompute() {
  if (!studentId.value) return ElMessage.warning('请先选择学生')
  recomputing.value = true
  try {
    const r = await request.post('/api/mastery/recompute', { studentId: studentId.value, subjectId: subjectId.value })
    ElMessage.success('已按 ' + r.ruleVersion + ' 重算 ' + r.count + ' 个知识点')
    load()
  } finally {
    recomputing.value = false
  }
}

function openManual(row) {
  cur.value = row
  manualLevel.value = row.level
  manualReason.value = ''
  dialog.value = true
}

async function saveManual() {
  if (!manualReason.value || manualReason.value.trim().length < 5) return ElMessage.warning('修正原因不少于 5 字')
  await request.post('/api/mastery/' + cur.value.resultId + '/manual', {
    level: manualLevel.value, reason: manualReason.value
  })
  ElMessage.success('已提交人工修正，原始结果保留')
  dialog.value = false
  load()
}

onMounted(async () => {
  subjects.value = (await request.get('/api/subject/list')) || []
  const d = await request.get('/api/user/page', { params: { page: 1, size: 50, roleCode: 'STUDENT' } })
  students.value = d.list || []
  studentId.value = students.value[0]?.id || null
  subjectId.value = subjects.value[0]?.id || 1
  load()
})
</script>

<style scoped>
.grid { display: grid; grid-template-columns: 1fr 1.15fr; gap: 16px; margin-bottom: 16px; }
.grid .card { margin-bottom: 0; }
.bar { height: 6px; background: #EDEFF2; border-radius: 3px; overflow: hidden; }
.bar i { display: block; height: 100%; }
</style>
