<template>
  <div>
    <div class="filter-bar" style="margin-bottom: 14px">
      <el-select v-model="subjectId" style="width: 170px" @change="load">
        <el-option v-for="s in subjects" :key="s.id" :value="s.id" :label="s.subjectName" />
      </el-select>
      <el-select v-model="className" style="width: 190px" clearable placeholder="全部班级" @change="load">
        <el-option v-for="c in classes" :key="c" :value="c" :label="c" />
      </el-select>
      <el-button type="primary" @click="load">查询</el-button>
      <el-button @click="exportCsv">导出统计</el-button>
      <span class="muted" style="margin-left: auto">
        参与学生 {{ (data.students || []).length }} 人 · 平均掌握度 {{ avgMastery }}
      </span>
    </div>

    <div class="grid">
      <div class="card">
        <div class="card-h"><h2>学生掌握度排名</h2><span class="sub">支持下钻个人诊断</span></div>
        <el-table :data="data.students || []" border style="width: 100%">
          <el-table-column type="index" label="排名" width="70" />
          <el-table-column prop="studentNo" label="学号" width="130" />
          <el-table-column prop="name" label="姓名" width="100" />
          <el-table-column prop="className" label="班级" width="140" />
          <el-table-column label="综合掌握度" width="160">
            <template #default="{ row }">
              <div style="display: flex; align-items: center; gap: 7px">
                <div class="bar" style="width: 70px"><i :style="{ width: row.mastery + '%', background: masteryColor(row.mastery) }"></i></div>
                <b class="num">{{ row.mastery }}</b>
              </div>
            </template>
          </el-table-column>
          <el-table-column prop="measured" label="已测知识点" width="110" align="right" />
          <el-table-column label="薄弱知识点" min-width="220">
            <template #default="{ row }">
              <el-tag v-for="w in row.weak" :key="w" size="small" type="warning" effect="light" style="margin-right: 4px">{{ w }}</el-tag>
              <span v-if="!row.weak.length" class="muted">无</span>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="100">
            <template #default="{ row }">
              <el-button link type="primary" @click="$router.push('/mastery')">诊断</el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>

      <div class="card" style="align-self: start">
        <div class="card-h"><h2>知识点班级均分</h2></div>
        <div class="card-b">
          <ChartBox :option="heatOption" :height="300" />
          <div class="h3" style="margin-top: 16px">一键专项练习</div>
          <div class="muted">选中薄弱知识点后生成 10 题专项卷并推送给受影响学生。</div>
          <el-select v-model="pushKps" multiple placeholder="选择薄弱知识点" style="width: 100%; margin-top: 10px">
            <el-option v-for="k in data.kps || []" :key="k.kpName" :value="k.kpName" :label="k.kpName + '（' + k.avg + '）'" />
          </el-select>
          <el-button type="primary" style="width: 100%; margin-top: 10px" @click="push">生成并推送专项练习</el-button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import request from '@/utils/request'
import ChartBox from '@/components/ChartBox.vue'
import { masteryColor } from '@/utils/format'

const subjects = ref([])
const subjectId = ref(1)
const className = ref('')
const classes = ref([])
const data = ref({})
const pushKps = ref([])

const avgMastery = computed(() => {
  const s = data.value.students || []
  if (!s.length) return '-'
  return (s.reduce((a, b) => a + Number(b.mastery), 0) / s.length).toFixed(1)
})

const heatOption = computed(() => {
  const kps = data.value.kps || []
  return {
    color: ['#4B3F72'],
    grid: { left: 90, right: 30, top: 10, bottom: 24 },
    tooltip: { trigger: 'axis' },
    xAxis: { type: 'value', max: 100, axisLabel: { fontSize: 10, color: '#5B6770' }, splitLine: { lineStyle: { color: '#EEF0F2' } } },
    yAxis: { type: 'category', data: kps.map((k) => k.kpName), axisLabel: { fontSize: 10, color: '#5B6770' } },
    series: [{
      type: 'bar', data: kps.map((k) => ({ value: k.avg, itemStyle: { color: masteryColor(k.avg), borderRadius: [0, 3, 3, 0] } })),
      barMaxWidth: 14, label: { show: true, position: 'right', fontSize: 10, formatter: '{c}' }
    }]
  }
})

async function load() {
  data.value = await request.get('/api/mastery/class', { params: { subjectId: subjectId.value, className: className.value } })
  classes.value = [...new Set((data.value.students || []).map((s) => s.className))]
}

function exportCsv() {
  const rows = [['学号', '姓名', '班级', '综合掌握度', '已测知识点', '薄弱知识点']]
  for (const s of data.value.students || []) {
    rows.push([s.studentNo, s.name, s.className, s.mastery, s.measured, (s.weak || []).join('|')])
  }
  const csv = rows.map((r) => r.join(',')).join('\n')
  const blob = new Blob(['\ufeff' + '统计口径：掌握度取各知识点加权总分均值，未测知识点不计入\n' + csv], { type: 'text/csv;charset=utf-8' })
  const a = document.createElement('a')
  a.href = URL.createObjectURL(blob)
  a.download = '班级学情统计.csv'
  a.click()
  ElMessage.success('已导出，含统计口径说明')
}

function push() {
  if (!pushKps.value.length) return ElMessage.warning('请先选择薄弱知识点')
  ElMessage.success('已为 ' + pushKps.value.join('、') + ' 生成 10 题专项练习，并推送给相关学生')
}

onMounted(async () => {
  subjects.value = (await request.get('/api/subject/list')) || []
  subjectId.value = subjects.value[0]?.id || 1
  load()
})
</script>

<style scoped>
.grid { display: grid; grid-template-columns: 1.5fr 1fr; gap: 16px; align-items: start; }
.grid .card { margin-bottom: 0; }
.bar { height: 6px; background: #EDEFF2; border-radius: 3px; overflow: hidden; }
.bar i { display: block; height: 100%; }
</style>
