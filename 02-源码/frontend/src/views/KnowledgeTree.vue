<template>
  <div>
    <div class="filter-bar" style="margin-bottom: 14px">
      <el-select v-model="subjectId" style="width: 200px" @change="loadTree">
        <el-option v-for="s in subjects" :key="s.id" :value="s.id" :label="s.subjectName" />
      </el-select>
      <el-input v-model="kw" placeholder="知识点名称" style="width: 200px" clearable />
      <el-button type="primary" @click="loadTree">查询</el-button>
      <span class="muted" style="margin-left: auto">
        一级节点权重合计 <b :style="{ color: totalWeight > 100 ? '#B02A37' : '#2B7955' }">{{ totalWeight.toFixed(2) }}</b> / 上限 100
      </span>
      <el-button @click="weightDialog = true">批量调整权重</el-button>
      <el-button type="primary" @click="openAdd(null)">新增知识点</el-button>
    </div>

    <div class="two">
      <div class="card">
        <div class="card-h"><h2>知识点树</h2><span class="sub">最多三级，可拖拽调整父级，跨学科与超层级会被拒绝</span></div>
        <div class="card-b" style="padding: 10px">
          <el-tree :data="tree" node-key="id" :props="{ label: 'kpName', children: 'children' }"
                   default-expand-all highlight-current :expand-on-click-node="false"
                   draggable :allow-drop="allowDrop" :allow-drag="allowDrag" @node-drop="onDrop"
                   @node-click="pick">
            <template #default="{ data }">
              <div class="node">
                <span class="kp">{{ data.kpName }}</span>
                <el-tag size="small" type="info" effect="plain">L{{ data.kpLevel }}</el-tag>
                <span class="muted num">权重 {{ data.examWeight }}</span>
                <span class="muted num">题量 {{ data.questionCount }}</span>
                <el-tag size="small" :type="data.status === 1 ? 'success' : 'info'" effect="light">
                  {{ data.status === 1 ? '启用' : '停用' }}
                </el-tag>
                <span class="ops">
                  <el-button link type="primary" @click.stop="openAdd(data)">添加子级</el-button>
                  <el-button link type="primary" @click.stop="openEdit(data)">编辑</el-button>
                </span>
              </div>
            </template>
          </el-tree>
          <el-empty v-if="!tree.length" description="该学科暂无知识点，先新增一级知识点" />
        </div>
      </div>

      <div class="card">
        <div class="card-h"><h2>节点详情</h2><span class="sub">选中节点后可维护权重与掌握阈值</span></div>
        <div class="card-b">
          <template v-if="cur.id">
            <div class="row"><label>知识点编号</label><div class="num">{{ cur.kpNo }}</div></div>
            <div class="row"><label>知识点名称</label><div>{{ cur.kpName }}</div></div>
            <div class="row"><label>层级</label><div><el-tag size="small" type="info">第 {{ cur.kpLevel }} 级</el-tag></div></div>
            <div class="row"><label>考纲权重</label><div class="num">{{ cur.examWeight }} %</div></div>
            <div class="row"><label>掌握阈值</label><div class="num">{{ cur.masteryThreshold }} %</div></div>
            <div class="row"><label>关联题量</label><div class="num">{{ cur.questionCount }} 道</div></div>
            <div class="row"><label>状态</label>
              <div><el-tag size="small" :type="cur.status === 1 ? 'success' : 'info'">{{ cur.status === 1 ? '启用' : '停用' }}</el-tag></div>
            </div>
            <el-alert type="info" :closable="false" style="margin-top: 12px"
                      title="删除前会校验题目与错题引用；有引用时只能停用，停用后组卷可选中但不参与抽题。" />
            <div style="display: flex; gap: 8px; margin-top: 14px">
              <el-button type="primary" @click="openEdit(cur)">编辑</el-button>
              <el-button type="danger" plain @click="remove(cur)">删除</el-button>
            </div>
          </template>
          <el-empty v-else description="在左侧点击一个知识点查看详情" />
        </div>
      </div>
    </div>

    <el-dialog v-model="dialog" :title="form.id ? '编辑知识点' : '新增知识点'" width="560px">
      <el-form :model="form" label-width="110px">
        <el-form-item label="上级知识点">
          <el-input :model-value="parentName" disabled />
        </el-form-item>
        <el-form-item label="知识点编号" required><el-input v-model="form.kpNo" /></el-form-item>
        <el-form-item label="知识点名称" required><el-input v-model="form.kpName" /></el-form-item>
        <el-form-item label="层级">
          <el-input-number v-model="form.kpLevel" :min="1" :max="3" />
        </el-form-item>
        <el-form-item label="考纲权重"><el-input-number v-model="form.examWeight" :min="0" :max="100" :precision="2" /></el-form-item>
        <el-form-item label="掌握阈值"><el-input-number v-model="form.masteryThreshold" :min="0" :max="100" :precision="2" /></el-form-item>
        <el-form-item label="状态">
          <el-select v-model="form.status"><el-option :value="1" label="启用" /><el-option :value="0" label="停用" /></el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialog = false">取消</el-button>
        <el-button type="primary" @click="save">保存</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="weightDialog" title="批量调整一级节点权重" width="560px">
      <el-alert type="warning" :closable="false" style="margin-bottom: 12px"
                title="同一学科一级节点权重合计不得超过 100，保存后自动重算已发布试卷的覆盖度提示。" />
      <el-table :data="l1List" border size="small">
        <el-table-column prop="kpName" label="一级知识点" />
        <el-table-column label="考纲权重" width="160">
          <template #default="{ row }">
            <el-input-number v-model="row.examWeight" :min="0" :max="100" :precision="2" size="small" />
          </template>
        </el-table-column>
      </el-table>
      <div class="muted" style="margin-top: 10px">
        合计 <b :style="{ color: sumWeight > 100 ? '#B02A37' : '#2B7955' }">{{ sumWeight.toFixed(2) }}</b> / 100
      </div>
      <template #footer>
        <el-button @click="weightDialog = false">取消</el-button>
        <el-button type="primary" :disabled="sumWeight > 100" @click="saveWeights">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
/** 知识点树：三级树维护、权重校验（合计 ≤100）、停用与删除前的引用校验 */
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import request from '@/utils/request'

const subjects = ref([])
const subjectId = ref(1)
const tree = ref([])
const kw = ref('')
const cur = ref({})
const dialog = ref(false)
const weightDialog = ref(false)
const form = ref({})
const parentName = ref('无（一级知识点）')
const l1List = ref([])

const totalWeight = computed(() =>
  tree.value.reduce((s, n) => s + Number(n.examWeight || 0), 0))
const sumWeight = computed(() => l1List.value.reduce((s, n) => s + Number(n.examWeight || 0), 0))

async function loadTree() {
  tree.value = await request.get('/api/knowledge-point/tree', { params: { subjectId: subjectId.value } })
  l1List.value = tree.value.map((n) => ({ kpId: n.id, kpName: n.kpName, examWeight: Number(n.examWeight) }))
}

function pick(data) { cur.value = data }

/** 拖拽子树的最大深度，用于判断拖拽后是否超过三级 */
function subtreeDepth(node) {
  const kids = node.childNodes || []
  if (!kids.length) return 1
  return 1 + Math.max(...kids.map(subtreeDepth))
}

/** 只允许拖拽、拖入同级或作为子节点，且拖拽后层级不超过三级 */
function allowDrop(dragNode, dropNode, type) {
  if (type === 'prev' || type === 'next') {
    // 同级排序：层级不变
    return dropNode.level + subtreeDepth(dragNode) - 1 <= 3
  }
  // inner：成为 dropNode 的子节点
  return dropNode.level + subtreeDepth(dragNode) <= 3
}

function allowDrag(node) { return !node.disabled }

/** 拖拽完成：把新的 parentId 与 kpLevel 同步到后端，失败则回滚树 */
async function onDrop(dragNode, dropNode, type) {
  const parentId = type === 'inner'
    ? dropNode.data.id
    : (dropNode.parent && dropNode.parent.data && dropNode.parent.data.id) || 0
  const newLevel = type === 'inner' ? dropNode.data.kpLevel + 1 : dropNode.level
  try {
    await request.put('/api/knowledge-point/' + dragNode.data.id, {
      ...dragNode.data, parentId, kpLevel: newLevel
    })
    ElMessage.success(`已移动到「${type === 'inner' ? dropNode.data.kpName : '同级'}」，层级更新为 L${newLevel}`)
    await loadTree()
  } catch (e) {
    ElMessage.error('移动失败，已还原')
    await loadTree()
  }
}

function openAdd(parent) {
  form.value = {
    subjectId: subjectId.value,
    parentId: parent ? parent.id : 0,
    kpLevel: parent ? Math.min(3, parent.kpLevel + 1) : 1,
    kpNo: 'ZS' + String(subjectId.value).padStart(2, '0') + String(Date.now()).slice(-4),
    examWeight: 5,
    masteryThreshold: 80,
    status: 1
  }
  parentName.value = parent ? parent.kpName : '无（一级知识点）'
  dialog.value = true
}

function openEdit(data) {
  form.value = { ...data }
  parentName.value = data.parentId ? '上级节点 #' + data.parentId : '无（一级知识点）'
  dialog.value = true
}

async function save() {
  if (!form.value.kpName) return ElMessage.warning('请填写知识点名称')
  if (form.value.id) await request.put('/api/knowledge-point/' + form.value.id, form.value)
  else await request.post('/api/knowledge-point', form.value)
  ElMessage.success('保存成功')
  dialog.value = false
  loadTree()
}

async function remove(data) {
  await ElMessageBox.confirm('删除前将校验题目与错题引用，有引用时只能停用。确认删除？', '删除确认', { type: 'warning' })
  await request.delete('/api/knowledge-point/' + data.id)
  ElMessage.success('已删除')
  cur.value = {}
  loadTree()
}

async function saveWeights() {
  const items = l1List.value.map((n) => ({ kpId: n.kpId, examWeight: n.examWeight }))
  const r = await request.post('/api/knowledge-point/weight-adjust', { subjectId: subjectId.value, items })
  ElMessage.success('权重已保存，合计 ' + r.total + '；' + r.affectedPapers)
  weightDialog.value = false
  loadTree()
}

onMounted(async () => {
  subjects.value = (await request.get('/api/subject/list')) || []
  if (subjects.value.length) subjectId.value = subjects.value[0].id
  loadTree()
})
</script>

<style scoped>
.two { display: grid; grid-template-columns: 1.5fr 1fr; gap: 16px; align-items: start; }
.node { display: flex; align-items: center; gap: 10px; width: 100%; font-size: 13px; }
.node .kp { min-width: 120px; }
.node .ops { margin-left: auto; opacity: 0; transition: opacity 0.15s; }
.node:hover .ops { opacity: 1; }
.row { display: flex; margin-bottom: 12px; font-size: 13px; }
.row label { width: 100px; color: var(--muted); }
</style>
