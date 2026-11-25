import { createRouter, createWebHistory } from 'vue-router'

/** 路由：管理端走 MainLayout，学生端走 PortalLayout；meta.title 用于面包屑 */
const routes = [
  { path: '/login', component: () => import('@/views/Login.vue'), meta: { public: true, title: '登录' } },
  {
    path: '/',
    component: () => import('@/layout/MainLayout.vue'),
    redirect: '/dashboard',
    children: [
      { path: 'dashboard', component: () => import('@/views/Dashboard.vue'), meta: { title: '题库统计首页' } },
      { path: 'subject', component: () => import('@/views/Subject.vue'), meta: { title: '学科管理' } },
      { path: 'knowledge', component: () => import('@/views/KnowledgeTree.vue'), meta: { title: '知识点树' } },
      { path: 'question', component: () => import('@/views/QuestionList.vue'), meta: { title: '题库列表' } },
      { path: 'question/edit/:id?', component: () => import('@/views/QuestionEdit.vue'), meta: { title: '题目编辑' } },
      { path: 'paper/workbench', component: () => import('@/views/PaperWorkbench.vue'), meta: { title: '组卷工作台' } },
      { path: 'paper', component: () => import('@/views/PaperList.vue'), meta: { title: '试卷管理' } },
      { path: 'paper/:id', component: () => import('@/views/PaperDetail.vue'), meta: { title: '试卷详情' } },
      { path: 'audit', component: () => import('@/views/Audit.vue'), meta: { title: '题目审核台' } },
      { path: 'import', component: () => import('@/views/Import.vue'), meta: { title: '批量导入' } },
      { path: 'mastery', component: () => import('@/views/Mastery.vue'), meta: { title: '学情诊断' } },
      { path: 'class-stat', component: () => import('@/views/ClassStat.vue'), meta: { title: '班级学情' } },
      { path: 'rule-config', component: () => import('@/views/RuleConfig.vue'), meta: { title: '诊断规则配置' } },
      { path: 'system/user', component: () => import('@/views/UserRole.vue'), meta: { title: '用户与角色' } },
      { path: 'system/menu', component: () => import('@/views/MenuList.vue'), meta: { title: '菜单管理' } },
      { path: 'system/log', component: () => import('@/views/OperLog.vue'), meta: { title: '操作日志' } },
      { path: 'system/notice', component: () => import('@/views/NoticeList.vue'), meta: { title: '公告与消息' } },
      { path: 'message', component: () => import('@/views/MessageList.vue'), meta: { title: '站内消息' } },
      { path: 'profile', component: () => import('@/views/Profile.vue'), meta: { title: '个人信息' } }
    ]
  },
  {
    path: '/practice',
    component: () => import('@/layout/PortalLayout.vue'),
    children: [{ path: '', component: () => import('@/views/PracticeCenter.vue'), meta: { title: '练习中心' } }]
  },
  {
    path: '/answer/:recordId',
    component: () => import('@/layout/PortalLayout.vue'),
    children: [{ path: '', component: () => import('@/views/Answer.vue'), meta: { title: '答题' } }]
  },
  {
    path: '/wrong-book',
    component: () => import('@/layout/PortalLayout.vue'),
    children: [{ path: '', component: () => import('@/views/WrongBook.vue'), meta: { title: '我的错题本' } }]
  },
  {
    path: '/my-mastery',
    component: () => import('@/layout/PortalLayout.vue'),
    children: [{ path: '', component: () => import('@/views/MasteryStudent.vue'), meta: { title: '我的学情诊断' } }]
  },
  {
    path: '/papers',
    component: () => import('@/layout/PortalLayout.vue'),
    children: [{ path: '', component: () => import('@/views/PaperSquare.vue'), meta: { title: '试卷库' } }]
  },
  { path: '/:pathMatch(.*)*', redirect: '/dashboard' }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('qb_token')
  if (!to.meta.public && !token) return next('/login')
  if (to.path === '/login' && token) return next('/dashboard')
  next()
})

export default router
