<template>
  <div class="two">
    <div class="card">
      <div class="card-h"><h2>个人资料</h2><span class="sub">头像上传后右上角同步显示</span></div>
      <div class="card-b">
        <el-form label-width="100px">
          <el-form-item label="头像">
            <div style="display: flex; align-items: center; gap: 14px">
              <img v-if="form.avatar" :src="form.avatar" class="big-avatar" alt="" />
              <div v-else class="big-avatar ph">{{ (form.realName || 'U').slice(0, 1) }}</div>
              <el-upload :show-file-list="false" :http-request="uploadAvatar">
                <el-button size="small">上传头像</el-button>
              </el-upload>
            </div>
          </el-form-item>
          <el-form-item label="账号"><el-input :model-value="form.username" disabled style="width: 300px" /></el-form-item>
          <el-form-item label="姓名"><el-input v-model="form.realName" style="width: 300px" /></el-form-item>
          <el-form-item label="手机"><el-input v-model="form.phone" style="width: 300px" /></el-form-item>
          <el-form-item label="邮箱"><el-input v-model="form.email" style="width: 300px" /></el-form-item>
          <el-form-item label="角色">
            <el-tag effect="light" type="info">{{ user.roleName }}</el-tag>
          </el-form-item>
          <div style="padding-left: 100px">
            <el-button type="primary" :loading="saving" @click="save">保存资料</el-button>
          </div>
        </el-form>
      </div>
    </div>

    <div class="card" style="align-self: start">
      <div class="card-h"><h2>修改密码</h2></div>
      <div class="card-b">
        <el-form label-width="90px">
          <el-form-item label="原密码"><el-input v-model="pwd.oldPassword" type="password" show-password /></el-form-item>
          <el-form-item label="新密码"><el-input v-model="pwd.newPassword" type="password" show-password /></el-form-item>
          <el-form-item label="确认密码"><el-input v-model="pwd.confirm" type="password" show-password /></el-form-item>
          <div style="padding-left: 90px">
            <el-button type="primary" @click="changePwd">提交修改</el-button>
          </div>
        </el-form>
        <el-alert type="info" :closable="false" style="margin-top: 14px"
                  title="密码使用 BCrypt 存储，修改后下次登录生效。" />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import request from '@/utils/request'

const form = ref({})
const pwd = ref({ oldPassword: '', newPassword: '', confirm: '' })
const saving = ref(false)
const user = JSON.parse(localStorage.getItem('qb_user') || '{}')

async function load() {
  form.value = await request.get('/api/profile')
}

async function uploadAvatar(opt) {
  const fd = new FormData()
  fd.append('file', opt.file)
  fd.append('bizType', 'avatar')
  const d = await request.post('/api/file/upload', fd, { headers: { 'Content-Type': 'multipart/form-data' } })
  form.value.avatar = d.path
  await request.put('/api/profile', { avatar: d.path })
  const u = JSON.parse(localStorage.getItem('qb_user') || '{}')
  u.avatar = d.path
  localStorage.setItem('qb_user', JSON.stringify(u))
  ElMessage.success('头像已更新，刷新后右上角同步显示')
  window.location.reload()
}

async function save() {
  saving.value = true
  try {
    await request.put('/api/profile', form.value)
    const u = JSON.parse(localStorage.getItem('qb_user') || '{}')
    u.realName = form.value.realName
    u.avatar = form.value.avatar
    localStorage.setItem('qb_user', JSON.stringify(u))
    ElMessage.success('资料已保存')
  } finally {
    saving.value = false
  }
}

async function changePwd() {
  if (!pwd.value.newPassword || pwd.value.newPassword.length < 6) return ElMessage.warning('新密码不少于 6 位')
  if (pwd.value.newPassword !== pwd.value.confirm) return ElMessage.warning('两次输入的新密码不一致')
  await request.post('/api/auth/password', pwd.value)
  ElMessage.success('密码已修改')
  pwd.value = { oldPassword: '', newPassword: '', confirm: '' }
}

onMounted(load)
</script>

<style scoped>
.two { display: grid; grid-template-columns: 1.2fr 1fr; gap: 16px; align-items: start; }
.two .card { margin-bottom: 0; }
.big-avatar { width: 64px; height: 64px; border-radius: 50%; object-fit: cover; }
.big-avatar.ph { background: var(--sub); color: #fff; display: flex; align-items: center; justify-content: center; font-size: 22px; }
</style>
