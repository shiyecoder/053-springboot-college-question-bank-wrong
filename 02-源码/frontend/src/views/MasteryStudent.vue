<template>
  <div>
    <div class="head">
      <div>
        <div class="page-title">我的学情诊断</div>
        <div class="muted" style="margin-top: 4px">
          数据截至 {{ formatTime(data.calcTime || '') }} · 规则版本 {{ data.ruleVersion }} ·
          已测 {{ data.measuredCount }}/{{ data.totalCount }} 个知识点
        </div>
      </div>
      <div style="display: flex; gap: 8px">
        <el-button :loading="loading" @click="recompute">重新计算</el-button>
        <el-button type="primary" @click="showRule = true">查看计算口径</el-button>
      </div>
    </div>

    <div class="kpi-grid" style="margin-bottom: 16px">
      <div class="kpi"><div class="t">综合掌握度</div><div class="v num">{{ data.average ?? '-' }}</div>
        <div class="d">{{ levelText(data.average) }}</div></div>
      <div class="kpi"><div class="t">已掌握知识点</div><div class="v num">{{ countLevel('已掌握') }}</div>
        <div class="d">共 {{ data.totalCount }} 个知识点</div></div>
      <div class="kpi"><div class="t">薄弱知识点</div><div class="v num">{{ countLevel('薄弱') + countLevel('严重薄弱') }}</div>
        <div class="d">严重薄弱 {{ countLevel('严重薄弱') }}</div></div>
      <div class="kpi"><div class="t">未测知识点</div><div class="v num">{{ countLevel('未测') }}</div>
        <div class="d">样本不足或没有作答</div></div>
    </div>

    <div class="two">
      <div class="card">
        <div class="card-h"><h2>知识点掌握度</h2><span class="sub">{{ data.subjectName }}</span></div>
        <div class="card-b"><ChartBox :option="radarOption" :height="300" /></div>
      </div>
      <div class="card">
        <div class="card-h"><h2>薄弱知识点与推荐</h2></div>
        <el-table :data="weakList" border size="small" height="300">
          <el-table-column prop="kpName" label="知识点" min-width="120" />
          <el-table-column label="掌握度" width="120">
            <template #default="{ row }">
              <div style="display: flex; align-items: center; gap: 6px">
                <div class="bar" style="width: 50px"><i :style="{ width: row.totalScore + '%', background: masteryColor(row.totalScore) }"></i></div>
                <b class="num">{{ row.totalScore }}</b>
              </div>
            </template>
          </el-table-column>
          <el-table-column prop="sampleCount" label="样本" width="60" align="right" />
          <el-table-column label="等级" width="96">
            <template #default="{ row }"><el-tag size="small" :type="statusType(row.level)" effect="light">{{ row.level }}</el-tag></template>
          </el-table-column>
          <el-table-column label="操作" width="86">
            <template #default="{ row }">
              <el-button link type="primary" @click="practice(row)">练 10 题</el-button>
            </template>
          </el-table-column>
          <template #empty><el-empty description="暂无薄弱知识点，保持得很好" :image-size="60" /></template>
        </el-table>
      </div>
    </div>

    <div class="card">
      <div class="card-h"><h2>诊断结论与建议动作</h2></div>
      <div class="suggest">
        <div v-for=" (s, i) in suggestions " :key="i" class="scard">
          <div class="muted">{{ s.kind }}</div>
          <div style="font-weight: 600; margin: 6px 0 4px">{{ s.title }}</div>
          <div class="muted" style="line-height: 1.7">{{ s.desc }}</div>
        </div>
      </div>
    </div>

    <div class="card">
      <div class="card-h"><h2>各知识点五项因子</h2><span class="sub">正确率 40% · 耗时 15% · 重做 20% · 考纲权重 15% · 复习 10%</span></div>
      <el-table :data="data.items || []" border style="width: 100%" max-height="380">
        <el-table-column prop="kpName" label="知识点" min-width="130" fixed />
        <el-table-column prop="accuracyScore" label="正确率" width="96" align="right" />
        <el-table-column prop="timeScore" label="耗时" width="86" align="right" />
        <el-table-column prop="redoScore" label="重做" width="86" align="right" />
        <el-table-column prop="weightScore" label="考纲权重" width="100" align="right" />
        <el-table-column prop="reviewScore" label="复习" width="86" align="right" />
        <el-table-column label="总分" width="86" align="right">
          <template #default="{ row }"><b class="num" :style="{ color: masteryColor(row.totalScore) }">{{ row.totalScore }}</b></template>
        </el-table-column>
        <el-table-column label="等级" width="100">
          <template #default="{ row }"><el-tag size="small" :type="statusType(row.level)" effect="light">{{ row.level }}</el-tag></template>
        </el-table-column>
        <el-table-column label="建议" min-width="280" show-overflow-tooltip>
          <template #default="{ row }">
            <span v-if="row.insufficient" class="muted">数据不足 · </span>{{ row.suggestion }}
          </template>
        </el-table-column>
      </el-table>
    </div>

    <el-dialog v-model="showRule" title="掌握度计算口径" width="640px">
      <el-table :data="ruleRows" border size="small">
        <el-table-column prop="name" label="因子" width="150" />
        <el-table-column prop="weight" label="权重" width="80" />
        <el-table-column prop="missing" label="缺失处理" />
      </el-table>
      <div class="muted" style="margin-top: 12px; line-height: 1.9">
        掌握度 = Σ(单项归一化得分 × 权重)，权重合计 100；单项按分段线性插值归一化到 0-100。
        样本少于 5 次的知识点标注「数据不足」且不参与薄弱排名；诊断每日凌晨重算一次。
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
/** 我的学情诊断：雷达、薄弱推荐、五项因子与建议 */
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import request from '@/utils/request'
import ChartBox from '@/components/ChartBox.vue'
import { masteryColor, statusType, formatTime } from '@/utils/format'

const data = ref({})
const loading = ref(false)
const showRule = ref(false)
const user = JSON.parse(localStorage.getItem('qb_user') || '{}')

const ruleRows = [
  { name: '近 30 天正确率', weight: '40%', missing: '无作答标记未测，不参与排名' },
  { name: '平均答题耗时比', weight: '15%', missing: '无记录记 0，超标准 2 倍记 0' },
  { name: '错题重做表现', weight: '20%', missing: '无错题按 70 分基准' },
  { name: '考纲权重', weight: '15%', missing: '缺失按一级节点最大权重归一' },
  { name: '复习及时率', weight: '10%', missing: '未建计划记 0' }
]

const weakList = computed(() => (data.value.items || [])
  .filter((i) => ['薄弱', '严重薄弱'].includes(i.level))
  .sort((a, b) => a.totalScore - b.totalScore))

const suggestions = computed(() => {
  const w = weakList.value[0]
  const list = []
  if (w) {
    list.push({ kind: '优先攻克', title: w.kpName + '（' + w.totalScore + ' 分）', desc: w.suggestion })
  }
  list.push({ kind: '今日计划', title: '完成到期错题复习', desc: '按 1/3/7 天计划完成复习可提升复习及时率因子' })
  list.push({ kind: '系统推荐', title: '专项练习 10 题', desc: '按薄弱知识点生成，约 20 分钟' })
  return list
})

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
      areaStyle: { opacity: 0.2 }, symbolSize: 4
    }]
  }
})

function countLevel(l) { return (data.value.items || []).filter((i) => i.level === l).length }
function levelText(v) {
  const n = Number(v)
  if (!n) return '暂无数据'
  if (n >= 85) return '已掌握'
  if (n >= 70) return '基本掌握'
  if (n >= 50) return '薄弱'
  return '严重薄弱'
}

async function load() {
  const s = await request.get('/api/subject/list')
  const subjectId = (s && s[0] && s[0].id) || 1
  data.value = await request.get('/api/student/' + user.id + '/mastery', { params: { subjectId } })
}

async function recompute() {
  loading.value = true
  try {
    const s = await request.get('/api/subject/list')
    const subjectId = (s && s[0] && s[0].id) || 1
    await request.post('/api/mastery/recompute', { studentId: user.id, subjectId })
    await load()
    ElMessage.success('已重新计算，结果已留痕')
  } finally {
    loading.value = false
  }
}

function practice(row) { ElMessage.success('已加入专项练习：' + row.kpName + ' 10 题') }

onMounted(load)
</script>

<style scoped>
.head { display: flex; align-items: flex-end; justify-content: space-between; margin-bottom: 16px; gap: 16px; }
.two { display: grid; grid-template-columns: 1fr 1.1fr; gap: 16px; margin-bottom: 16px; }
.two .card { margin-bottom: 0; }
.bar { height: 6px; background: #EDEFF2; border-radius: 3px; overflow: hidden; }
.bar i { display: block; height: 100%; }
.suggest { display: grid; grid-template-columns: repeat(3, 1fr); gap: 14px; padding: 16px; }
.scard { border: 1px solid var(--border); border-radius: 9px; padding: 13px; }
</style>
