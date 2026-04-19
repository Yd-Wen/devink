import { createRouter, createWebHistory } from 'vue-router'
import HomePage from '@/pages/HomePage.vue'
import UserLoginPage from '@/pages/user/UserLoginPage.vue'
import UserRegisterPage from '@/pages/user/UserRegisterPage.vue'
import UserManagePage from '@/pages/admin/UserManagePage.vue'

const router = createRouter({
    history: createWebHistory(import.meta.env.BASE_URL),
    routes: [
        {
            path: '/',
            name: '主页',
            component: HomePage,
        },
        {
            path: '/create',
            name: '创作博客',
            component: () => import('@/pages/blog/BlogCreatePage.vue'),
        },
        {
            path: '/blog/list',
            name: '博客列表',
            component: () => import('@/pages/blog/BlogListPage.vue'),
        },
        {
            path: '/blog/:taskId',
            name: '博客详情',
            component: () => import('@/pages/blog/BlogDetailPage.vue'),
        },
        {
            path: '/user/login',
            name: '用户登录',
            component: UserLoginPage,
        },
        {
            path: '/user/register',
            name: '用户注册',
            component: UserRegisterPage,
        },
        {
            path: '/admin/userManage',
            name: '用户管理',
            component: UserManagePage,
        },
        {
            path: '/admin/statistics',
            name: '数据分析',
            component: () => import('@/pages/admin/StatisticsPage.vue'),
        },
    ],
})

export default router
