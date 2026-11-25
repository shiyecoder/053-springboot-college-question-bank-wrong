<template>
  <div v-if="paper.id">
    <div class="head">
      <div>
        <h1 class="page-title">{{ paper.paperName }}</h1>
        <div class="muted">
          {{ paper.paperNo }} · {{ paper.buildMode }}组卷 · {{ paper.questionCount }} 题 ·
          总分 {{ paper.totalScore }} · 建议 {{ paper.durationMin }} 分钟
        </div>
      </div>
      <div style="display: flex; gap: 8px; align-items: center">
        <el-tag :type="statusType(paper.status)" effect="light">{{ paper.status }}</el-tag>
        <el-button v-if="paper.status === '待审核'" type="primary" @click="publish">发布并冻结快照</el-button>
        <el-button @click="$router.push('/paper')">返回列表</el-button>
      </div>
    </div>

    <el-alert v-if="paper.rejectReason" type="error" :closable="false" style="margin-bottom: 14px"
              :title="'驳回原因：' + paper.rejectReason" />
    <el-alert v-if="paper.randomRule" type="warning" :closable="false" style="margin-bottom: 14px"
              :title="'回补明细：' + paper.randomRule" />

    <div class="grid">
      <div class="card">
        <div class="card-h"><h2>题目明细</h2><span class="sub">快照已冻结，题库改动不影响本卷</span></div>
        <div class="card-b">
          <div v-for="(q, i) in questions" :key="q.id" class="qitem">
            <div class="qhead">
              <b class="num">{{ i + 1 }}.</b>
              <el-tag size="small" effect="light" :type="questionTypeTag(q.questionType)">{{ q.questionType }}</el-tag>
              <span class="muted num">{{ q.score }} 分</span>
              <span class="muted">难度 {{ q.difficulty }}</span>
              <span class="muted" style="margin-left: auto">{{ kpName(q.knowledgePointId) }}</span>
            </div>
            <div class="stem">{{ q.stem }}</div>
            <div v-for="o in q.options" :key="o.id" class="opt">
              <span class="olabel">{{ o.optionLabel }}</span>
              <span>{{ o.optionContent }}</span>
              <img v-if="o.imageUrl" :src="o.imageUrl" class="thumb" alt="" />
            </div>
            <div class="muted" style="margin-top: 6px">
              答案：<b>{{ q.answer }}</b>　解析：{{ q.analysis }}
            </div>
          </div>
        </div>
      </div>
      <div class="card" style="align-self: start">
        <div class="card-h"><h2>覆盖度</h2></div>
        <div class="card-b" v-if="cov.kps">
          <div style="display: flex; gap: 8px; margin-bottom: 12px">
            <el-tag type="success" effect="light">易 {{ cov.distribution.easy }}</el-tag>
            <el-tag type="warning" effect="light">中 {{ cov.distribution.medium }}</el-tag>
            <el-tag type="danger" effect="light">难 {{ cov.distribution.hard }}</el-tag>
          </div>
          <div v-for="k in cov.kps" :key="k.kpId" style="margin-bottom: 10px">
            <div style="display: flex; justify-content: space-between; font-size: 12px">
              <span>{{ k.kpName }}</span><span class="num">{{ k.count }} 题 · {{ k.percent }}%</span>
            </div>
            <div class="bar"><i :style="{ width: Math.min(100, k.percent) + '%' }"></i></div>
          </div>
          <div v-if="cov.gaps && cov.gaps.length" style="margin-top: 12px">
            <el-alert v-for="g in cov.gaps" :key="g" type="warning" :closable="false" :title="g" style="margin-bottom: 6px" />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import request from '@/utils/request'
import { statusType, questionTypeTag } from '@/utils/format'

const route = useRoute()
const paper = ref({})
const questions = ref([])
const cov = ref({})
const kpNames = ref({})

function kpName(id) { return kpNames.value[id] || '-' }

async function load() {
  const d = await request.get('/api/paper/' + route.params.id + '/detail')
  paper.value = d.paper
  questions.value = d.questions || []
  cov.value = await request.get('/api/paper/' + route.params.id + '/coverage')
  const tree = await request.get('/api/knowledge-point/tree', { params: { subjectId: d.paper.subjectId } })
  const map = {}
  const walk = (nodes) => nodes.forEach((n) => { map[n.id] = n.kpName; if (n.children) walk(n.children) })
  walk(tree || [])
  kpNames.value = map
}

async function publish() {
  const d = await request.post('/api/paper/' + route.params.id + '/publish')
  ElMessage.success('已发布，冻结 ' + d.frozen + ' 道题目快照')
  load()
}

onMounted(load)
</script>

<style scoped>
.head { display: flex; align-items: flex-start; justify-content: space-between; margin-bottom: 16px; gap: 16px; }
.grid { display: grid; grid-template-columns: 1fr 340px; gap: 16px; align-items: start; }
.qitem { padding: 14px 0; border-bottom: 1px dashed var(--border); }
.qitem:last-child { border-bottom: 0; }
.qhead { display: flex; align-items: center; gap: 10px; margin-bottom: 8px; font-size: 12px; }
.stem { font-size: 13px; line-height: 1.9; }
.opt { display: flex; align-items: center; gap: 8px; font-size: 12px; padding-left: 4px; margin-top: 5px; }
.olabel { width: 18px; height: 18px; border-radius: 50%; border: 1px solid #C9CED6; display: flex; align-items: center; justify-content: center; font-size: 10px; }
.bar { height: 6px; background: #EDEFF2; border-radius: 3px; overflow: hidden; margin-top: 4px; }
.bar i { display: block; height: 100%; background: var(--primary); }
</style>
