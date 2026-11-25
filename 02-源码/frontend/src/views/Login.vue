<template>
  <div class="login">
    <!-- 主题背景：大学图书馆实景，叠深紫渐变遮罩保证文字可读 -->
    <div class="bg"></div>
    <div class="mask"></div>

    <div class="wrap">
      <div class="left">
        <div class="brand"><i></i>智汇题库</div>
        <h1>让每道错题<br />都变成一次诊断</h1>
        <p>按知识点组卷、在线练习自动判分，交卷即生成错题本；五项因子加权输出掌握度，教师与学生看到同一套口径。</p>
        <div class="pts">
          <div><b>1</b>三级知识点树 · 考纲权重组卷</div>
          <div><b>2</b>交卷秒判 · 错题自动归档</div>
          <div><b>3</b>掌握度诊断 · 结果可追溯可修正</div>
        </div>
        <div class="stats">
          <div><b>26</b><span>数据表</span></div>
          <div><b>5</b><span>角色协同</span></div>
          <div><b>5</b><span>诊断因子</span></div>
        </div>
      </div>

      <div class="right">
        <div class="form">
          <div class="form-h">
            <h2>欢迎回来</h2>
            <span class="badge">统一身份认证</span>
          </div>
          <div class="sub">请使用学校统一账号登录，学生用学号，教师用工号</div>
          <el-form :model="form" @submit.prevent>
            <el-form-item>
              <el-input v-model="form.username" size="large" placeholder="账号 / 学号" :prefix-icon="User" />
            </el-form-item>
            <el-form-item>
              <el-input v-model="form.password" size="large" type="password" show-password
                        placeholder="密码" :prefix-icon="Lock" @keyup.enter="submit" />
            </el-form-item>
            <div class="row"><el-checkbox v-model="remember">记住我</el-checkbox><span>忘记密码？联系教研秘书</span></div>
            <el-button type="primary" size="large" style="width: 100%" :loading="loading" @click="submit">登 录</el-button>
          </el-form>
          <div class="demo">
            演示账号（密码均为 123456）
            <div class="chips">
              <span v-for="d in demo" :key="d.u" @click="quick(d.u)">{{ d.u }} · {{ d.n }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="foot">高校智能题库与错题本系统 · 计算机学院教研组</div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { User, Lock } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import request from '@/utils/request'

const router = useRouter()
const form = ref({ username: '', password: '' })
const remember = ref(true)
const loading = ref(false)
const demo = [
  { u: 'admin', n: '管理员' }, { u: 'auditor', n: '教研员' }, { u: 'teacher01', n: '任课教师' },
  { u: 'secretary', n: '教学秘书' }, { u: '2023010101', n: '学生' }
]

function quick(u) {
  form.value.username = u
  form.value.password = '123456'
  submit()
}

async function submit() {
  if (!form.value.username || !form.value.password) return ElMessage.warning('请输入账号和密码')
  loading.value = true
  try {
    const d = await request.post('/api/auth/login', form.value)
    localStorage.setItem('qb_token', d.token)
    localStorage.setItem('qb_user', JSON.stringify(d.user))
    ElMessage.success('登录成功')
    router.push(d.user.roleCode === 'STUDENT' ? '/practice' : '/dashboard')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login { position: relative; height: 100vh; overflow: hidden; background: #241E38; }
/* 背景图 + 深紫遮罩，突出学术氛围又保证文字对比度 */
.bg {
  position: absolute; inset: 0;
  background: url('/login-bg.jpg') center / cover no-repeat;
  transform: scale(1.03);
}
.mask {
  position: absolute; inset: 0;
  background:
    radial-gradient(120% 90% at 12% 20%, rgba(75, 63, 114, 0.88) 0%, rgba(46, 38, 74, 0.72) 45%, rgba(32, 26, 52, 0.6) 100%),
    linear-gradient(100deg, rgba(36, 30, 56, 0.82) 0%, rgba(36, 30, 56, 0.22) 55%, rgba(36, 30, 56, 0.58) 100%);
}
.wrap {
  position: relative; z-index: 2; height: 100%;
  max-width: 1180px; margin: 0 auto; padding: 0 40px;
  display: flex; align-items: center; justify-content: space-between; gap: 60px;
}
.left { flex: 1; min-width: 0; color: #fff; padding-bottom: 24px; }
.brand { display: flex; align-items: center; gap: 10px; font-size: 17px; font-weight: 600; letter-spacing: 0.5px; }
.brand i {
  width: 26px; height: 26px; border-radius: 8px; display: inline-block;
  background: linear-gradient(135deg, #E0A458, #F0C48A);
  box-shadow: 0 4px 14px rgba(224, 164, 88, 0.42);
}
.left h1 {
  font-size: 40px; line-height: 1.34; margin: 54px 0 0; font-weight: 700;
  letter-spacing: -0.6px; text-shadow: 0 2px 20px rgba(0, 0, 0, 0.28);
}
.left p {
  margin-top: 18px; font-size: 14px; line-height: 2; max-width: 440px;
  color: rgba(255, 255, 255, 0.76);
}
.pts { margin-top: 38px; display: grid; gap: 13px; }
.pts div { display: flex; gap: 10px; align-items: center; font-size: 13px; color: rgba(255, 255, 255, 0.88); }
.pts b {
  width: 24px; height: 24px; border-radius: 7px; background: rgba(255, 255, 255, 0.16);
  display: flex; align-items: center; justify-content: center; font-size: 12px;
  border: 1px solid rgba(255, 255, 255, 0.14);
}
/* 左下角三个关键数字，强化系统定位 */
.stats { display: flex; gap: 34px; margin-top: 46px; }
.stats div { display: flex; align-items: baseline; gap: 7px; }
.stats b { font-size: 26px; font-weight: 700; color: #F0C48A; letter-spacing: -0.5px; }
.stats span { font-size: 12px; color: rgba(255, 255, 255, 0.6); }

.right { width: 402px; flex-shrink: 0; }
.form {
  background: rgba(255, 255, 255, 0.97);
  border-radius: 16px; padding: 34px 32px 26px;
  box-shadow: 0 24px 60px rgba(18, 14, 32, 0.42), 0 2px 0 rgba(255, 255, 255, 0.5) inset;
  backdrop-filter: blur(6px);
}
.form-h { display: flex; align-items: center; justify-content: space-between; }
.form h2 { font-size: 23px; font-weight: 700; margin: 0; color: #241E38; }
.form .badge {
  font-size: 11px; color: #4B3F72; background: #EFEBF8;
  border: 1px solid #DDD6EE; border-radius: 20px; padding: 2px 9px;
}
.form .sub { margin: 9px 0 24px; color: #7C8390; font-size: 12.5px; line-height: 1.7; }
.row {
  display: flex; justify-content: space-between; align-items: center;
  font-size: 12px; color: #7C8390; margin-bottom: 18px;
}
.demo { margin-top: 22px; padding-top: 15px; border-top: 1px dashed #E4E7EB; font-size: 12px; color: #7C8390; }
.chips { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 9px; }
.chips span {
  padding: 3px 10px; border: 1px solid #E4E7EB; border-radius: 20px;
  font-size: 11px; cursor: pointer; color: #4A5160; transition: all 0.16s;
}
.chips span:hover { border-color: #4B3F72; color: #4B3F72; background: #F6F4FB; }

.foot {
  position: absolute; left: 0; right: 0; bottom: 18px; z-index: 2;
  text-align: center; font-size: 11.5px; color: rgba(255, 255, 255, 0.42);
}

@media (max-width: 1080px) {
  .wrap { flex-direction: column; justify-content: center; gap: 26px; padding: 0 24px; }
  .left h1 { font-size: 30px; margin-top: 26px; }
  .left p, .pts, .stats { display: none; }
  .right { width: 100%; max-width: 402px; }
}
</style>
