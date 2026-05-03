import { useLoginUserStore } from '@/stores/loginUser'
import { message } from 'ant-design-vue'
import router from '@/router'
import { USER_ROLE_ADMIN } from '@/constants/user'

/**
 * 首次打开网站时，全局状态中还没有用户信息，需要先等后端返回用户数据后再做权限判断，否则所有用户都会被当成未登录
 */

// 是否为首次获取登录用户
let firstFetchLoginUser = true

/**
 * 全局权限校验
 */
router.beforeEach(async (to, from) => {
    const loginUserStore = useLoginUserStore()
    let loginUser = loginUserStore.loginUser

    // 首次加载时，等后端返回用户信息后再校验权限
    if (firstFetchLoginUser) {
        await loginUserStore.fetchLoginUser()
        loginUser = loginUserStore.loginUser
        firstFetchLoginUser = false
    }

    const toUrl = to.fullPath
    // 管理员页面权限校验
    if (toUrl.startsWith('/admin')) {
        if (!loginUser || loginUser.userRole !== USER_ROLE_ADMIN) {
            message.error('没有权限')
            return `/user/login?redirect=${to.fullPath}`  // 普通用户访问 /admin 路由页面时拦截并跳转登录页面
        }
    }
})
