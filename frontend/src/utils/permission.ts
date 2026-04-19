import { USER_ROLE_ADMIN } from '@/constants/user'

/**
 * 权限判断工具
 */

/**
 * 判断用户是否为管理员
 */
export const isAdmin = (user?: API.LoginUserVO): boolean => {
    return user?.userRole === USER_ROLE_ADMIN
}

/**
 * 判断用户是否有配额
 * 管理员不受限制，普通用户检查配额是否大于 0
 */
export const hasQuota = (user?: API.LoginUserVO): boolean => {
    if (isAdmin(user)) {
        return true
    }
    return (user?.quota ?? 0) > 0
}