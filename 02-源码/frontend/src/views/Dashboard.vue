<template>
  <div class="dash">
    <div class="head">
      <div>
        <h1 class="page-title">题库统计首页</h1>
        <div class="muted">数据口径：统计区间内已交卷练习，作废记录不计入</div>
      </div>
      <div class="filter-bar">
        <el-select v-model="days" style="width: 140px" @change="load">
          <el-option :value="30" label="最近 30 天" /><el-option :value="90" label="本学期" />
          <el-option :value="180" label="本学年" />
        </el-select>
        <el-select v-model="subjectId" style="width: 160px" clearable placeholder="全部学科" @change="load">
          <el-option v-for="s in subjects" :key="s.id" :value="s.id" :label="s.subjectName" />
        </el-select>
        <el-button type="primary" @click="load">查询</el-button>
        <el-button @click="exportReport">导出报表</el-button>
      </div>
    </div>

    <div class="kpi-grid k8">
      <div class="kpi" v-for="k in kpis" :key="k.label">
        <div class="t">{{ k.label }}</div>
        <div class="v num">{{ k.value }}</div>
        <div class="d">{{ k.desc }}</div>
      </div>
    </div>

    <div class="grid c2">
      <div class="card">
        <div class="card-h"><h2>近 30 天练习量与正确率</h2><span class="sub">双轴</span></div>
        <div class="card-b"><ChartBox :option="trendOption" :height="176" /></div>
      </div>
      <div class="card">
        <div class="card-h"><h2>学科题量占比</h2><span class="sub">环形</span></div>
        <div class="card-b"><ChartBox :option="pieOption" :height="176" /></div>
      </div>
    </div>

    <div class="grid c3">
      <div class="card">
        <div class="card-h"><h2>题目难度分布</h2></div>
        <div class="card-b"><ChartBox :option="barOption" :height="150" /></div>
      </div>
      <div class="card">
        <div class="card-h"><h2>知识点掌握度</h2><span class="sub">雷达</span></div>
        <div class="card-b"><ChartBox :option="radarOption" :height="150" /></div>
      </div>
      <div class="card">
        <div class="card-h"><h2>错题重练转化</h2><span class="sub">漏斗</span></div>
        <div class="card-b"><ChartBox :option="funnelOption" :height="150" /></div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import request from '@/utils/request'
import ChartBox from '@/components/ChartBox.vue'

const days = ref(30)
const subjectId = ref(null)
const subjects = ref([])
const overview = ref({})
const charts = ref({})
const COLOR = ['#4B3F72', '#7A6BA8', '#E0A458', '#2B7955', '#98A2B3']

const kpis = computed(() => {
  const o = overview.value
  return [
    { label: '题库题目总数', value: o.questionTotal ?? '-', desc: '含各状态题目' },
    { label: '待审核题目', value: o.pendingAudit ?? '-', desc: '需教研员处理' },
    { label: '本月新增题目', value: o.monthNew ?? '-', desc: '本月入库与待审' },
    { label: '练习人次', value: o.practiceCount ?? '-', desc: '累计已交卷' },
    { label: '平均正确率', value: (o.avgCorrectRate ?? '-') + '%', desc: '近 ' + days.value + ' 天' },
    { label: '错题总量', value: o.wrongTotal ?? '-', desc: '不含已移除' },
    { label: '薄弱知识点', value: o.weakKp ?? '-', desc: '掌握度低于 70' },
    { label: '活跃学生', value: o.activeStudents ?? '-', desc: '近 ' + days.value + ' 天有练习' }
  ]
})

const trendOption = computed(() => {
  const t = charts.value.trend || { axis: [], counts: [], rates: [] }
  return {
    color: COLOR,
    grid: { left: 38, right: 42, top: 30, bottom: 26 },
    tooltip: { trigger: 'axis' },
    legend: { data: ['练习量', '正确率'], right: 0, top: 0, itemWidth: 10, itemHeight: 10, textStyle: { fontSize: 11 } },
    xAxis: { type: 'category', data: t.axis, axisLabel: { fontSize: 10, color: '#5B6770' }, axisLine: { lineStyle: { color: '#E4E7EB' } } },
    yAxis: [
      { type: 'value', axisLabel: { fontSize: 10, color: '#5B6770' }, splitLine: { lineStyle: { color: '#EEF0F2' } } },
      { type: 'value', max: 100, axisLabel: { fontSize: 10, color: '#5B6770', formatter: '{value}%' }, splitLine: { show: false } }
    ],
    series: [
      { name: '练习量', type: 'bar', data: t.counts, barMaxWidth: 14, itemStyle: { borderRadius: [3, 3, 0, 0] } },
      { name: '正确率', type: 'line', yAxisIndex: 1, data: t.rates, smooth: true, symbolSize: 4, lineStyle: { width: 2 } }
    ]
  }
})

const pieOption = computed(() => ({
  color: COLOR,
  tooltip: { trigger: 'item', formatter: '{b}: {c} 道 ({d}%)' },
  legend: { orient: 'vertical', right: 0, top: 'center', itemWidth: 9, itemHeight: 9, textStyle: { fontSize: 11 } },
  series: [{
    type: 'pie', radius: ['46%', '70%'], center: ['34%', '50%'],
    data: charts.value.subjectPie || [],
    label: { show: false }, itemStyle: { borderColor: '#fff', borderWidth: 2 }
  }]
}))

const barOption = computed(() => ({
  color: ['#4B3F72'],
  grid: { left: 34, right: 12, top: 18, bottom: 34 },
  tooltip: { trigger: 'axis' },
  xAxis: { type: 'category', data: (charts.value.difficulty || []).map((d) => d.name), axisLabel: { fontSize: 9, color: '#5B6770', interval: 0, rotate: 12 }, axisLine: { lineStyle: { color: '#E4E7EB' } } },
  yAxis: { type: 'value', axisLabel: { fontSize: 10, color: '#5B6770' }, splitLine: { lineStyle: { color: '#EEF0F2' } } },
  series: [{ type: 'bar', data: (charts.value.difficulty || []).map((d) => d.value), barMaxWidth: 18, itemStyle: { borderRadius: [3, 3, 0, 0] } }]
}))

const radarOption = computed(() => {
  const r = charts.value.radar || []
  return {
    color: ['#4B3F72'],
    tooltip: {},
    radar: {
      radius: '62%', center: ['50%', '54%'],
      indicator: r.length ? r.map((x) => ({ name: x.name, max: 100 })) : [{ name: '暂无数据', max: 100 }],
      axisName: { fontSize: 9, color: '#5B6770' },
      splitLine: { lineStyle: { color: '#E4E7EB' } }, splitArea: { show: false },
      axisLine: { lineStyle: { color: '#E4E7EB' } }
    },
    series: [{
      type: 'radar', data: [{ value: r.map((x) => x.value), name: '掌握度' }],
      areaStyle: { opacity: 0.18 }, symbolSize: 3, lineStyle: { width: 2 }
    }]
  }
})

const funnelOption = computed(() => ({
  color: ['#4B3F72', '#7A6BA8', '#2B7955'],
  tooltip: { trigger: 'item' },
  legend: { bottom: 0, itemWidth: 9, itemHeight: 9, textStyle: { fontSize: 10 } },
  series: [{
    type: 'funnel', left: '8%', right: '8%', top: 12, bottom: 34, minSize: '24%',
    label: { fontSize: 10, color: '#fff' },
    data: charts.value.funnel || []
  }]
}))

async function load() {
  const [o, c] = await Promise.all([
    request.get('/api/stats/overview', { params: { days: days.value } }),
    request.get('/api/stats/charts', { params: { days: days.value, subjectId: subjectId.value } })
  ])
  overview.value = o
  charts.value = c
}

function exportReport() {
  const o = overview.value
  const lines = [
    '统计口径：统计区间内已交卷练习，作废记录不计入',
    '导出时间：' + new Date().toLocaleString('zh-CN'),
    '题库题目总数,' + o.questionTotal + ',待审核题目,' + o.pendingAudit + ',本月新增,' + o.monthNew,
    '练习人次,' + o.practiceCount + ',平均正确率,' + o.avgCorrectRate + '%,错题总量,' + o.wrongTotal,
    '薄弱知识点,' + o.weakKnowledge + o.weakKp + ',活跃学生,' + o.activeStudents
  ]
  const blob = new Blob(['\ufeff' + lines.join('\n')], { type: 'text/csv;charset=utf-8' })
  const a = document.createElement('a')
  a.href = URL.createObjectURL(blob)
  a.download = '题库统计报表.csv'
  a.click()
  ElMessage.success('报表已导出，含统计口径说明')
}

onMounted(async () => {
  const s = await request.get('/api/subject/list')
  subjects.value = s || []
  load()
})
</script>

<style scoped>
.head { display: flex; align-items: flex-end; justify-content: space-between; margin-bottom: 14px; gap: 16px; flex-wrap: wrap; }
.k8 { grid-template-columns: repeat(4, 1fr); gap: 12px; margin-bottom: 14px; }
.k8 .kpi { padding: 10px 14px; }
.k8 .kpi .v { font-size: 21px; margin-top: 3px; }
.grid { display: grid; gap: 14px; margin-bottom: 14px; }
.grid.c2 { grid-template-columns: 1.32fr 1fr; }
.grid.c3 { grid-template-columns: 1fr 1fr 1fr; margin-bottom: 0; }
.grid .card { margin-bottom: 0; }
.grid .card-b { padding: 10px 12px; }
</style>
