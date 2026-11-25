<template>
  <div>
    <CrudPage :cfg="cfg">
      <template #row-actions="{ row }">
        <el-button link type="primary" @click="$router.push('/question?subjectId=' + row.id)">题库</el-button>
      </template>
    </CrudPage>
  </div>
</template>

<script setup>
/** 学科管理：通用表格 + 关联题库跳转 */
import CrudPage from '@/components/CrudPage.vue'

const cfg = {
  title: '学科',
  url: '/api/subject',
  statusOptions: [
    { label: '启用', value: '1' },
    { label: '停用', value: '0' }
  ],
  columns: [
    { prop: 'subjectNo', label: '学科编号', minWidth: 100 },
    { prop: 'subjectName', label: '学科名称', minWidth: 140 },
    { prop: 'eduLevel', label: '适用层次', minWidth: 90 },
    { prop: 'deptId', label: '开课院系', minWidth: 90 },
    { prop: 'questionCount', label: '题目总数', type: 'num', minWidth: 90 },
    { prop: 'passRate', label: '默认及格率', type: 'num', minWidth: 100 },
    { prop: 'sortNo', label: '排序', type: 'num', minWidth: 70 },
    { prop: 'status', label: '状态', type: 'switch', minWidth: 80 },
    { prop: 'createTime', label: '创建时间', type: 'time', minWidth: 160 }
  ],
  fields: [
    { prop: 'subjectName', label: '学科名称', required: true },
    { prop: 'subjectNo', label: '学科编号', required: true },
    { prop: 'eduLevel', label: '适用层次', type: 'select', options: ['中职', '高职', '本科', '研究生'].map((v) => ({ label: v, value: v })) },
    { prop: 'deptId', label: '开课院系', type: 'number' },
    { prop: 'ownerId', label: '负责人 ID', type: 'number' },
    { prop: 'passRate', label: '默认及格率', type: 'number', precision: 2 },
    { prop: 'sortNo', label: '排序号', type: 'number' },
    { prop: 'status', label: '状态', type: 'select', options: [{ label: '启用', value: 1 }, { label: '停用', value: 0 }] }
  ]
}
</script>
