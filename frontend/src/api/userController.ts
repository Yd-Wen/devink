// @ts-ignore
/* eslint-disable */
import request from '@/request'

/** Add User 添加用户（管理员） POST /api/user/add */
export async function addUserApiUserAddPost(
  // 叠加生成的Param类型 (非body参数swagger默认没有生成对象)
  params: API.addUserApiUserAddPostParams,
  body: API.UserAddRequest,
  options?: { [key: string]: any }
) {
  return request<API.BaseResponseInt_>('/api/user/add', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    params: { ...params },
    data: body,
    ...(options || {}),
  })
}

/** Delete User 删除用户（管理员） POST /api/user/delete */
export async function deleteUserApiUserDeletePost(
  // 叠加生成的Param类型 (非body参数swagger默认没有生成对象)
  params: API.deleteUserApiUserDeletePostParams,
  body: API.DeleteRequest,
  options?: { [key: string]: any }
) {
  return request<API.BaseResponseBool_>('/api/user/delete', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    params: { ...params },
    data: body,
    ...(options || {}),
  })
}

/** Get User By Id 根据 ID 获取用户 GET /api/user/get */
export async function getUserByIdApiUserGetGet(
  // 叠加生成的Param类型 (非body参数swagger默认没有生成对象)
  params: API.getUserByIdApiUserGetGetParams,
  options?: { [key: string]: any }
) {
  return request<API.BaseResponseUserVO_>('/api/user/get', {
    method: 'GET',
    params: {
      ...params,
    },
    ...(options || {}),
  })
}

/** Get Login User 获取当前登录用户 GET /api/user/get/login */
export async function getLoginUserApiUserGetLoginGet(
  // 叠加生成的Param类型 (非body参数swagger默认没有生成对象)
  params: API.getLoginUserApiUserGetLoginGetParams,
  options?: { [key: string]: any }
) {
  return request<API.BaseResponseLoginUserVO_>('/api/user/get/login', {
    method: 'GET',
    params: { ...params },
    ...(options || {}),
  })
}

/** List Users By Page 分页查询用户列表（管理员） POST /api/user/list/page */
export async function listUsersByPageApiUserListPagePost(
  // 叠加生成的Param类型 (非body参数swagger默认没有生成对象)
  params: API.listUsersByPageApiUserListPagePostParams,
  body: API.UserQueryRequest,
  options?: { [key: string]: any }
) {
  return request<API.BaseResponseDict_>('/api/user/list/page', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    params: { ...params },
    data: body,
    ...(options || {}),
  })
}

/** Login 用户登录 POST /api/user/login */
export async function loginApiUserLoginPost(
  body: API.UserLoginRequest,
  options?: { [key: string]: any }
) {
  return request<API.BaseResponseLoginUserVO_>('/api/user/login', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    data: body,
    ...(options || {}),
  })
}

/** Logout 用户登出 POST /api/user/logout */
export async function logoutApiUserLogoutPost(
  // 叠加生成的Param类型 (非body参数swagger默认没有生成对象)
  params: API.logoutApiUserLogoutPostParams,
  options?: { [key: string]: any }
) {
  return request<API.BaseResponseBool_>('/api/user/logout', {
    method: 'POST',
    params: { ...params },
    ...(options || {}),
  })
}

/** Register 用户注册 POST /api/user/register */
export async function registerApiUserRegisterPost(
  body: API.UserRegisterRequest,
  options?: { [key: string]: any }
) {
  return request<API.BaseResponseInt_>('/api/user/register', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    data: body,
    ...(options || {}),
  })
}

/** Update User 更新用户（管理员） POST /api/user/update */
export async function updateUserApiUserUpdatePost(
  // 叠加生成的Param类型 (非body参数swagger默认没有生成对象)
  params: API.updateUserApiUserUpdatePostParams,
  body: API.UserUpdateRequest,
  options?: { [key: string]: any }
) {
  return request<API.BaseResponseBool_>('/api/user/update', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    params: { ...params },
    data: body,
    ...(options || {}),
  })
}
