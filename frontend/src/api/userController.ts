// @ts-ignore
/* eslint-disable */
import request from '@/request'

/** Add User 添加用户（管理员） POST /user/add */
export async function addUser(
    // 叠加生成的Param类型 (非body参数swagger默认没有生成对象)
    params: API.addUserParams,
    body: API.UserAddRequest,
    options?: { [key: string]: any }
) {
    return request<API.BaseResponseInt_>('/user/add', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        params: { ...params },
        data: body,
        ...(options || {}),
    })
}

/** Delete User 删除用户（管理员） POST /user/delete */
export async function deleteUser(
    // 叠加生成的Param类型 (非body参数swagger默认没有生成对象)
    params: API.deleteUserParams,
    body: API.DeleteRequest,
    options?: { [key: string]: any }
) {
    return request<API.BaseResponseBool_>('/user/delete', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        params: { ...params },
        data: body,
        ...(options || {}),
    })
}

/** Get User By Id 根据 ID 获取用户 GET /user/get */
export async function getUserById(
    // 叠加生成的Param类型 (非body参数swagger默认没有生成对象)
    params: API.getUserByIdParams,
    options?: { [key: string]: any }
) {
    return request<API.BaseResponseUserVO_>('/user/get', {
        method: 'GET',
        params: {
            ...params,
        },
        ...(options || {}),
    })
}

/** Get Login User 获取当前登录用户 GET /user/get/login */
export async function getLoginUser(
    // 叠加生成的Param类型 (非body参数swagger默认没有生成对象)
    params: API.getLoginUserParams,
    options?: { [key: string]: any }
) {
    return request<API.BaseResponseLoginUserVO_>('/user/get/login', {
        method: 'GET',
        params: { ...params },
        ...(options || {}),
    })
}

/** List Users By Page 分页查询用户列表（管理员） POST /user/list/page */
export async function listUsersByPage(
    // 叠加生成的Param类型 (非body参数swagger默认没有生成对象)
    params: API.listUsersByPageParams,
    body: API.UserQueryRequest,
    options?: { [key: string]: any }
) {
    return request<API.BaseResponseDict_>('/user/list/page', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        params: { ...params },
        data: body,
        ...(options || {}),
    })
}

/** Login 用户登录 POST /user/login */
export async function login(body: API.UserLoginRequest, options?: { [key: string]: any }) {
    return request<API.BaseResponseLoginUserVO_>('/user/login', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        data: body,
        ...(options || {}),
    })
}

/** Logout 用户登出 POST /user/logout */
export async function logout(
    // 叠加生成的Param类型 (非body参数swagger默认没有生成对象)
    params: API.logoutParams,
    options?: { [key: string]: any }
) {
    return request<API.BaseResponseBool_>('/user/logout', {
        method: 'POST',
        params: { ...params },
        ...(options || {}),
    })
}

/** Register 用户注册 POST /user/register */
export async function register(body: API.UserRegisterRequest, options?: { [key: string]: any }) {
    return request<API.BaseResponseInt_>('/user/register', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        data: body,
        ...(options || {}),
    })
}

/** Update User 更新用户（管理员） POST /user/update */
export async function updateUser(
    // 叠加生成的Param类型 (非body参数swagger默认没有生成对象)
    params: API.updateUserParams,
    body: API.UserUpdateRequest,
    options?: { [key: string]: any }
) {
    return request<API.BaseResponseBool_>('/user/update', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        params: { ...params },
        data: body,
        ...(options || {}),
    })
}
