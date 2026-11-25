<template>
  <div>
    <div class="filter-bar" style="margin-bottom: 14px">
      <el-input v-model="kw" placeholder="账号 / 姓名" style="width: 200px" clearable @keyup.enter="reload" />
      <el-select v-model="roleCode" placeholder="全部角色" clearable style="width: 170px" @change="reload">
        <el-option v-for="r in roles" :key="r.roleCode" :value="r.roleCode" :label="r.roleName" />
      </el-select>
      <el-button type="primary" @click="reload">查询</el-button>
      <el-button type="primary" plain style="margin-left: auto" @click="openAdd">新建用户</el-button>
    </div>

    <div class="grid">
      <div class="card">
        <div class="card-h"><h2>用户列表</h2><span class="sub">共 {{ total }} 条</span></div>
        <el-table :data="rows" v-loading="loading" border style="width: 100%">
          <el-table-column label="头像" width="72" align="center">
            <template #default="{ row }">
              <el-avatar :size="34" :src="row.avatar || ''">{{ (row.realName || '?').slice(0, 1) }}</el-avatar>
            </template>
          </el-table-column>
          <el-table-column prop="username" label="账号" width="126" />
          <el-table-column prop="realName" label="姓名" width="96" />
          <el-table-column prop="roleName" label="角色" width="120">
            <template #default="{ row }"><el-tag size="small" effect="light" type="info">{{ row.roleName }}</el-tag></template>
          </el-table-column>
          <el-table-column prop="className" label="班级" width="130" />
          <el-table-column prop="dataScope" label="数据范围" width="100" />
          <el-table-column label="状态" width="86">
            <template #default="{ row }">
              <el-tag size="small" :type="row.status === 1 ? 'success' : 'info'" effect="light">{{ row.status === 1 ? '正常' : '停用' }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column label="最近登录" width="160">
            <template #default="{ row }"><span class="num muted">{{ formatTime(row.lastLogin) }}</span></template>
          </el-table-column>
          <el-table-column label="操作" width="190" fixed="right">
            <template #default="{ row }">
              <el-button link type="primary" @click="openEdit(row)">编辑</el-button>
              <el-button link type="primary" @click="resetPwd(row)">重置密码</el-button>
            </template>
          </el-table-column>
        </el-table>
        <div style="display: flex; justify-content: flex-end; padding: 14px 16px">
          <el-pagination background layout="total, prev, pager, next" :total="total"
                         v-model:current-page="page" :page-size="10" @current-change="load" />
        </div>
      </div>

      <div class="card" style="align-self: start">
        <div class="card-h"><h2>为角色分配菜单</h2></div>
        <div class="card-b">
          <el-select v-model="assignRole" style="width: 100%; margin-bottom: 12px" @change="loadRoleMenus">
            <el-option v-for="r in roles" :key="r.id" :value="r.id" :label="r.roleName + '（' + r.dataScope + '）'" />
          </el-select>
          <el-tree ref="treeRef" :data="menuTree" node-key="id" show-checkbox default-expand-all
                   :props="{ label: 'name', children: 'children' }" style="font-size: 12px" />
          <div style="display: flex; gap: 8px; margin-top: 14px">
            <el-button type="primary" style="flex: 1" @click="saveRoleMenus">保存授权</el-button>
            <el-button @click="loadRoleMenus">重置</el-button>
          </div>
          <div class="muted" style="margin-top: 10px">
            权限按「菜单 + 按钮 + 数据范围」三层控制；前端隐藏按钮不等于授权，写接口后端复核。
          </div>
        </div>
      </div>
    </div>

    <el-dialog v-model="dialog" :title="form.id ? '编辑用户' : '新建用户'" width="560px">
      <el-form :model="form" label-width="100px">
        <el-form-item label="账号" required><el-input v-model="form.username" :disabled="!!form.id" /></el-form-item>
        <el-form-item label="姓名" required><el-input v-model="form.realName" /></el-form-item>
        <el-form-item label="角色">
          <el-select v-model="form.roleId" style="width: 220px">
            <el-option v-for="r in roles" :key="r.id" :value="r.id" :label="r.roleName" />
          </el-select>
        </el-form-item>
        <el-form-item label="班级"><el-input v-model="form.className" placeholder="学生填写班级，如 计算机 2301" /></el-form-item>
        <el-form-item label="手机"><el-input v-model="form.phone" /></el-form-item>
        <el-form-item label="邮箱"><el-input v-model="form.email" /></el-form-item>
        <el-form-item label="状态">
          <el-select v-model="form.status"><el-option :value="1" label="正常" /><el-option :value="0" label="停用" /></el-select>
        </el-form-item>
        <el-alert v-if="!form.id" type="info" :closable="false" title="新建用户默认密码 123456，首次登录后请提醒修改。" />
      </el-form>
      <template #footer>
        <el-button @click="dialog = false">取消</el-button>
        <el-button type="primary" @click="save">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
/** 用户与角色：用户 CRUD、重置密码、角色菜单授权（树形） */
import { ref, onMounted, nextTick } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import request from '@/utils/request'
import { formatTime } from '@/utils/format'

const rows = ref([])
const total = ref(0)
const page = ref(1)
const kw = ref('')
const roleCode = ref('')
const loading = ref(false)
const roles = ref([])
const assignRole = ref(2)
const menuTree = ref([])
const treeRef = ref(null)
const dialog = ref(false)
const form = ref({})

async function load() {
  loading.value = true
  try {
    const d = await request.get('/api/user/page', {
      params: { page: page.value, size: 10, kw: kw.value, roleCode: roleCode.value }
    })
    rows.value = d.list || []
    total.value = d.total || 0
  } finally {
    loading.value = false
  }
}
function reload() { page.value = 1; load() }

function openAdd() {
  form.value = { status: 1, roleId: 5 }
  dialog.value = true
}
function openEdit(row) {
  form.value = { ...row }
  dialog.value = true
}

async function save() {
  if (!form.value.username) return ElMessage.warning('请填写账号')
  if (form.value.id) await request.put('/api/user/' + form.value.id, form.value)
  else await request.post('/api/user', form.value)
  ElMessage.success('保存成功')
  dialog.value = false
  load()
}

async function resetPwd(row) {
  await ElMessageBox.confirm('将 ' + row.realName + ' 的密码重置为 123456？', '重置密码', { type: 'warning' })
  await request.post('/api/user/' + row.id + '/reset-password')
  ElMessage.success('已重置为 123456')
}

async function loadMenuTree() {
  const tree = await request.get('/api/menu/page', { params: { page: 1, size: 100 } })
  const all = tree.list || []
  const build = (pid) => all.filter((m) => m.parentId === pid)
    .map((m) => ({ id: m.id, name: m.menuName, children: build(m.id) }))
  menuTree.value = build(0)
}

async function loadRoleMenus() {
  const checked = await request.get('/api/user/role/' + assignRole.value + '/menus')
  await nextTick()
  if (treeRef.value) treeRef.value.setCheckedKeys(checked || [])
}

async function saveRoleMenus() {
  const ids = [...treeRef.value.getCheckedKeys(), ...treeRef.value.getHalfCheckedKeys()]
  await request.put('/api/user/role/' + assignRole.value + '/menus', ids)
  ElMessage.success('授权已保存，该角色下次登录生效')
}

onMounted(async () => {
  const r = await request.get('/api/role/page', { params: { page: 1, size: 20 } })
  roles.value = r.list || []
  await loadMenuTree()
  await loadRoleMenus()
  load()
})
</script>

<style scoped>
.grid { display: grid; grid-template-columns: 1.55fr 1fr; gap: 16px; align-items: start; }
.grid .card { margin-bottom: 0; }
</style>
