<template>
  <div>
    <header class="portal">
      <div class="brand"><i></i>智汇题库 · 学生端</div>
      <nav>
        <router-link to="/practice" :class="{ on: route.path === '/practice' }">练习中心</router-link>
        <router-link to="/wrong-book" :class="{ on: route.path === '/wrong-book' }">我的错题本</router-link>
        <router-link to="/my-mastery" :class="{ on: route.path === '/my-mastery' }">我的学情诊断</router-link>
        <router-link to="/papers" :class="{ on: route.path === '/papers' }">试卷库</router-link>
      </nav>
      <div class="right">
        <span>{{ user.realName }} · {{ user.className || '学生' }}</span>
        <el-dropdown @command="onCommand">
          <img v-if="user.avatar" class="avatar" :src="user.avatar" alt="" />
          <div v-else class="ava">{{ (user.realName || 'S').slice(0, 1) }}</div>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="profile">个人信息</el-dropdown-item>
              <el-dropdown-item command="logout">退出登录</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </header>
    <div class="wrap">
      <router-view />
    </div>
  </div>
</template>

<script setup>
/** 学生门户骨架：顶部导航 + 1240px 居中内容区，与后台明显区分 */
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'

const route = useRoute()
const router = useRouter()
const user = ref(JSON.parse(localStorage.getItem('qb_user') || '{}'))

function onCommand(cmd) {
  if (cmd === 'profile') router.push('/profile')
  else {
    localStorage.removeItem('qb_token')
    localStorage.removeItem('qb_user')
    router.push('/login')
  }
}

onMounted(() => { user.value = JSON.parse(localStorage.getItem('qb_user') || '{}') })
</script>

<style scoped>
.portal {
  height: 60px; background: var(--primary); color: #fff; display: flex; align-items: center;
  padding: 0 40px; gap: 26px; position: sticky; top: 0; z-index: 9;
}
.brand { font-size: 16px; font-weight: 600; display: flex; align-items: center; gap: 9px; }
.brand i { width: 22px; height: 22px; border-radius: 6px; background: var(--accent); display: inline-block; }
nav { display: flex; gap: 4px; }
nav a { padding: 7px 14px; border-radius: 7px; font-size: 13px; color: rgba(255,255,255,.8); }
nav a.on { background: rgba(255,255,255,.16); color: #fff; font-weight: 600; }
.right { margin-left: auto; display: flex; align-items: center; gap: 10px; font-size: 12px; }
.avatar { width: 30px; height: 30px; border-radius: 50%; object-fit: cover; cursor: pointer; }
.ava {
  width: 30px; height: 30px; border-radius: 50%; background: var(--sub); color: #fff;
  display: flex; align-items: center; justify-content: center; font-size: 11px; cursor: pointer;
}
.wrap { max-width: 1240px; margin: 0 auto; padding: 24px; }
</style>
