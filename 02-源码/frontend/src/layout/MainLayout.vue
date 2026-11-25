<template>
  <div class="shell">
    <aside class="side">
      <div class="logo"><i></i><span>智汇题库</span></div>
      <el-scrollbar class="nav">
        <template v-for="m in menus" :key="m.id">
          <div class="group">{{ m.name }}</div>
          <router-link v-for="c in m.children" :key="c.id" :to="c.path" class="item"
                       :class="{ on: isActive(c.path) }">
            <span class="dot"></span>{{ c.name }}
          </router-link>
        </template>
        <div v-if="!menus.length" class="group">暂无授权菜单</div>
      </el-scrollbar>
      <div class="foot">2026 春季学期 · 教研版</div>
    </aside>
    <div class="main">
      <header class="top">
        <div class="crumb">首页 / <b>{{ current }}</b></div>
        <div class="sp"></div>
        <el-badge :value="unread" :hidden="!unread" class="bell">
          <el-icon :size="17" style="cursor: pointer" @click="$router.push('/message')"><Bell /></el-icon>
        </el-badge>
        <el-tooltip content="折叠菜单" placement="bottom">
          <el-icon :size="17" style="cursor: pointer" @click="collapsed = !collapsed"><Fold /></el-icon>
        </el-tooltip>
        <el-dropdown @command="onCommand">
          <div class="who">
            <img v-if="user.avatar" class="avatar" :src="user.avatar" alt="" />
            <div class="ava" v-else>{{ (user.realName || 'U').slice(0, 1) }}</div>
            <div class="name">
              {{ user.realName || '未登录' }}
              <span>{{ user.roleName }} · {{ user.className || deptName }}</span>
            </div>
          </div>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="profile">个人信息</el-dropdown-item>
              <el-dropdown-item command="logout">退出登录</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </header>
      <main class="body">
        <router-view v-slot="{ Component }">
          <component :is="Component" />
        </router-view>
      </main>
    </div>
  </div>
</template>

<script setup>
/** 管理端骨架：220px 侧边栏 + 56px 顶栏，菜单按角色权限动态获取 */
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import request from '@/utils/request'

const route = useRoute()
const router = useRouter()
const menus = ref([])
const user = ref(JSON.parse(localStorage.getItem('qb_user') || '{}'))
const unread = ref(0)
const collapsed = ref(false)

const current = computed(() => route.meta.title || '工作台')
const deptName = computed(() => {
  const map = { 1: '教务处', 2: '数学教研室', 3: '计算机学院', 4: '物理教研室' }
  return map[user.value.deptId] || '校本部'
})

function isActive(path) {
  if (!path) return false
  if (path === '/question') return route.path === '/question'
  return route.path === path || route.path.startsWith(path + '/')
}

async function loadInfo() {
  const d = await request.get('/api/auth/info')
  menus.value = d.menus || []
  user.value = d.user
  unread.value = d.unread || 0
  localStorage.setItem('qb_user', JSON.stringify(d.user))
}

function onCommand(cmd) {
  if (cmd === 'profile') router.push('/profile')
  else {
    localStorage.removeItem('qb_token')
    localStorage.removeItem('qb_user')
    router.push('/login')
  }
}

onMounted(loadInfo)
</script>

<style scoped>
.shell { min-height: 100vh; }
.side {
  position: fixed; left: 0; top: 0; bottom: 0; width: 220px;
  background: var(--primary); color: #fff; display: flex; flex-direction: column; z-index: 10;
}
.logo {
  height: 56px; display: flex; align-items: center; gap: 9px; padding: 0 18px;
  font-size: 15px; font-weight: 600; letter-spacing: 0.5px; border-bottom: 1px solid rgba(255,255,255,.12);
}
.logo i { width: 22px; height: 22px; border-radius: 6px; background: var(--accent); display: inline-block; }
.nav { flex: 1; padding: 8px 0; }
.group { padding: 12px 18px 6px; font-size: 11px; color: rgba(255,255,255,.45); letter-spacing: 1px; }
.item {
  display: flex; align-items: center; gap: 9px; padding: 9px 18px; font-size: 13px;
  color: rgba(255,255,255,.82); border-left: 3px solid transparent;
}
.item:hover { background: rgba(255,255,255,.08); color: #fff; }
.item.on { background: rgba(255,255,255,.14); color: #fff; border-left-color: var(--accent); font-weight: 600; }
.dot { width: 5px; height: 5px; border-radius: 50%; background: rgba(255,255,255,.4); }
.item.on .dot { background: var(--accent); }
.foot { padding: 14px 18px; border-top: 1px solid rgba(255,255,255,.12); font-size: 11px; color: rgba(255,255,255,.5); }
.main { margin-left: 220px; min-height: 100vh; }
.top {
  height: 56px; background: #fff; border-bottom: 1px solid var(--border); display: flex;
  align-items: center; padding: 0 24px; gap: 16px; position: sticky; top: 0; z-index: 9;
}
.crumb { font-size: 12px; color: var(--muted); }
.crumb b { color: var(--text); font-weight: 600; }
.sp { margin-left: auto; }
.who { display: flex; align-items: center; gap: 8px; cursor: pointer; }
.avatar { width: 30px; height: 30px; border-radius: 50%; object-fit: cover; }
.ava {
  width: 30px; height: 30px; border-radius: 50%; background: var(--sub); color: #fff;
  display: flex; align-items: center; justify-content: center; font-size: 11px;
}
.name { font-size: 12px; line-height: 1.3; }
.name span { display: block; color: var(--muted); font-size: 11px; }
.body { padding: 24px; }
</style>
