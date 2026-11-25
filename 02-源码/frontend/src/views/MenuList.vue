<template>
  <div>
    <div class="card">
      <div class="card-h"><h2>菜单与按钮权限</h2><span class="sub">目录 D / 菜单 M / 按钮 B 三级</span>
        <span class="muted" style="margin-left: auto">「菜单管理」本身在各角色授权树中默认隐藏</span>
      </div>
      <el-table :data="rows" border style="width: 100%" row-key="id" default-expand-all
                :tree-props="{ children: 'children' }">
        <el-table-column prop="menuName" label="菜单名称" min-width="200" />
        <el-table-column prop="path" label="路由" min-width="160" />
        <el-table-column prop="component" label="组件" min-width="150" />
        <el-table-column prop="perms" label="权限标识" min-width="150" />
        <el-table-column label="类型" width="90">
          <template #default="{ row }">
            <el-tag size="small" :type="row.menuType === 'D' ? 'info' : (row.menuType === 'M' ? 'primary' : 'warning')" effect="light">
              {{ row.menuType === 'D' ? '目录' : (row.menuType === 'M' ? '菜单' : '按钮') }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="sortNo" label="排序" width="70" align="right" />
        <el-table-column label="状态" width="86">
          <template #default="{ row }">
            <el-tag size="small" :type="row.status === 1 ? 'success' : 'info'">{{ row.status === 1 ? '正常' : '停用' }}</el-tag>
          </template>
        </el-table-column>
      </el-table>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import request from '@/utils/request'

const rows = ref([])

onMounted(async () => {
  const d = await request.get('/api/menu/page', { params: { page: 1, size: 100 } })
  const all = d.list || []
  const build = (pid) => all.filter((m) => m.parentId === pid)
    .map((m) => ({ ...m, children: build(m.id) }))
  rows.value = build(0)
})
</script>
