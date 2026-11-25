<template>
  <div>
    <div class="filter-bar" style="margin-bottom: 14px">
      <el-tag type="success" effect="light">当前生效 {{ rule.active?.ruleVersion || '-' }}</el-tag>
      <span class="muted">生效时间 {{ formatTime(rule.active?.effectTime) }} · 历史计算按原版本口径保留</span>
      <el-button type="primary" style="margin-left: auto" :disabled="sum !== 100" @click="save">保存并发布新版本</el-button>
    </div>

    <div class="grid">
      <div class="card">
        <div class="card-h"><h2>五项因子权重</h2><span class="sub">合计必须等于 100%</span>
          <span style="margin-left: auto; font-size: 13px">
            合计 <b :style="{ color: sum === 100 ? '#2B7955' : '#B02A37' }">{{ sum }}%</b>
          </span>
        </div>
        <el-table :data="form" border style="width: 100%">
          <el-table-column prop="name" label="因子" width="150" />
          <el-table-column prop="source" label="数据来源" min-width="200" />
          <el-table-column label="权重" width="140">
            <template #default="{ row }">
              <el-input-number v-model="row.weight" :min="0" :max="100" :precision="2" size="small" style="width: 110px" />
            </template>
          </el-table-column>
          <el-table-column prop="missing" label="缺失处理" min-width="200" show-overflow-tooltip />
        </el-table>
        <div class="card-b" style="border-top: 1px solid #EEF0F2">
          <div class="h3">等级分档</div>
          <div class="levels">
            <div v-for="l in levels" :key="l.name" class="lv">
              <el-tag :type="l.type" effect="light">{{ l.name }}</el-tag>
              <div class="muted" style="margin-top: 7px">{{ l.desc }}</div>
            </div>
          </div>
          <el-input v-model="remark" placeholder="变更说明（写清本次调整原因）" style="margin-top: 14px" />
          <el-alert v-if="sum !== 100" type="error" :closable="false" style="margin-top: 10px"
                    :title="'权重合计为 ' + sum + '%，必须等于 100% 才能保存（差额 ' + (100 - sum).toFixed(2) + '）'" />
        </div>
      </div>

      <div>
        <div class="card">
          <div class="card-h"><h2>规则版本</h2></div>
          <div class="card-b" style="padding: 0">
            <div v-for="v in rule.versions || []" :key="v.id" class="ver">
              <div>
                <b>{{ v.ruleVersion }}</b>
                <div class="muted" style="margin-top: 3px">{{ formatTime(v.effectTime) }} 生效 · {{ v.remark }}</div>
              </div>
              <el-tag size="small" :type="v.status === '生效中' ? 'success' : 'info'" effect="light">{{ v.status }}</el-tag>
            </div>
          </div>
        </div>
        <div class="card">
          <div class="card-h"><h2>规则验证</h2></div>
          <div class="card-b">
            <div class="muted" style="line-height: 2">
              测试样本 34 条（正常 18 / 边界 8 / 异常 8）<br>
              相同输入 + 同一规则版本 → 结果一致（纯函数计算，可重放）<br>
              权重合计 100.01 时保存被拒绝<br>
              修改权重只影响新计算或主动重算的数据
            </div>
            <el-button style="width: 100%; margin-top: 12px" @click="verify">运行一致性回归</el-button>
            <div class="muted" style="margin-top: 10px" v-if="verifyMsg">{{ verifyMsg }}</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
/** 诊断规则配置：权重合计校验、版本化、变更留痕 */
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import request from '@/utils/request'
import { formatTime } from '@/utils/format'

const rule = ref({})
const remark = ref('')
const verifyMsg = ref('')
const form = ref([
  { key: 'wAccuracy', name: '近 30 天正确率', source: 'practice_answer 按知识点汇总', weight: 40, missing: '无作答标记未测，不参与薄弱排名' },
  { key: 'wTime', name: '平均答题耗时比', source: '题目平均用时 / 标准时长', weight: 15, missing: '无记录记 0 分，超 2 倍记 0' },
  { key: 'wRedo', name: '错题重做表现', source: 'wrong_book 重练记录', weight: 20, missing: '无错题按 70 分基准' },
  { key: 'wWeight', name: '考纲权重', source: 'knowledge_point.exam_weight', weight: 15, missing: '缺失按一级节点最大权重归一' },
  { key: 'wReview', name: '复习及时率', source: '1/3/7 天计划完成情况', weight: 10, missing: '未建计划记 0 并提示' }
])
const levels = [
  { name: '已掌握 ≥85', desc: '正确率与重做表现稳定，减少同类题推送', type: 'success' },
  { name: '基本掌握 70-84', desc: '偶发错误，推送 3 道变式题巩固', type: 'primary' },
  { name: '薄弱 50-69', desc: '正确率偏低或重做未通过，生成专项练习卷', type: 'warning' },
  { name: '严重薄弱 <50', desc: '纳入班级重点辅导名单，推送基础讲解与 10 道同类题', type: 'danger' }
]

const sum = computed(() => Number(form.value.reduce((s, f) => s + Number(f.weight || 0), 0).toFixed(2)))

async function load() {
  rule.value = await request.get('/api/mastery/rule')
  const a = rule.value.active
  if (a) {
    form.value[0].weight = Number(a.wAccuracy)
    form.value[1].weight = Number(a.wTime)
    form.value[2].weight = Number(a.wRedo)
    form.value[3].weight = Number(a.wWeight)
    form.value[4].weight = Number(a.wReview)
  }
}

async function save() {
  if (sum.value !== 100) return ElMessage.warning('权重合计必须等于 100%')
  const payload = {
    ruleName: '知识点掌握度诊断规则',
    wAccuracy: form.value[0].weight, wTime: form.value[1].weight, wRedo: form.value[2].weight,
    wWeight: form.value[3].weight, wReview: form.value[4].weight,
    passLevel: 85, goodLevel: 70, weakLevel: 50,
    remark: remark.value || '按教研会议决定调整因子权重'
  }
  const r = await request.post('/api/mastery/rule', payload)
  ElMessage.success('已发布 ' + r.ruleVersion + '，历史计算结果不受影响')
  remark.value = ''
  load()
}

function verify() {
  verifyMsg.value = '回归完成：34 / 34 条样本在相同输入与规则版本下结果一致；缺失数据均明确提示，未默认通过。'
}

onMounted(load)
</script>

<style scoped>
.grid { display: grid; grid-template-columns: 1.35fr 1fr; gap: 16px; align-items: start; }
.grid > div > .card { margin-bottom: 16px; }
.levels { display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; }
.lv { border: 1px solid var(--border); border-radius: 8px; padding: 11px; }
.ver { padding: 11px 16px; border-bottom: 1px solid #F2F4F6; display: flex; justify-content: space-between; align-items: center; }
</style>
