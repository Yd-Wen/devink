// @ts-ignore
/* eslint-disable */
import request from '@/request'

/** Get Blog 获取博客详情 GET /api/blog/${param0} */
export async function getBlogApiBlogTaskIdGet(
  // 叠加生成的Param类型 (非body参数swagger默认没有生成对象)
  params: API.getBlogApiBlogTaskIdGetParams,
  options?: { [key: string]: any }
) {
  const { task_id: param0, ...queryParams } = params
  return request<API.BaseResponseBlogVO_>(`/api/blog/${param0}`, {
    method: 'GET',
    params: { ...queryParams },
    ...(options || {}),
  })
}

/** Ai Modify Outline AI 修改大纲 POST /api/blog/ai-modify-outline */
export async function aiModifyOutlineApiBlogAiModifyOutlinePost(
  // 叠加生成的Param类型 (非body参数swagger默认没有生成对象)
  params: API.aiModifyOutlineApiBlogAiModifyOutlinePostParams,
  body: API.BlogAiModifyOutlineRequest,
  options?: { [key: string]: any }
) {
  return request<API.BaseResponseList_>('/api/blog/ai-modify-outline', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    params: { ...params },
    data: body,
    ...(options || {}),
  })
}

/** Confirm Outline 确认大纲 POST /api/blog/confirm-outline */
export async function confirmOutlineApiBlogConfirmOutlinePost(
  // 叠加生成的Param类型 (非body参数swagger默认没有生成对象)
  params: API.confirmOutlineApiBlogConfirmOutlinePostParams,
  body: API.BlogConfirmOutlineRequest,
  options?: { [key: string]: any }
) {
  return request<API.BaseResponseNoneType_>('/api/blog/confirm-outline', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    params: { ...params },
    data: body,
    ...(options || {}),
  })
}

/** Confirm Title 确认标题并输入补充描述 POST /api/blog/confirm-title */
export async function confirmTitleApiBlogConfirmTitlePost(
  // 叠加生成的Param类型 (非body参数swagger默认没有生成对象)
  params: API.confirmTitleApiBlogConfirmTitlePostParams,
  body: API.BlogConfirmTitleRequest,
  options?: { [key: string]: any }
) {
  return request<API.BaseResponseNoneType_>('/api/blog/confirm-title', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    params: { ...params },
    data: body,
    ...(options || {}),
  })
}

/** Create Blog 创建博客任务 POST /api/blog/create */
export async function createBlogApiBlogCreatePost(
  // 叠加生成的Param类型 (非body参数swagger默认没有生成对象)
  params: API.createBlogApiBlogCreatePostParams,
  body: API.BlogCreateRequest,
  options?: { [key: string]: any }
) {
  return request<API.BaseResponseStr_>('/api/blog/create', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    params: { ...params },
    data: body,
    ...(options || {}),
  })
}

/** Delete Blog 删除博客 POST /api/blog/delete */
export async function deleteBlogApiBlogDeletePost(
  // 叠加生成的Param类型 (非body参数swagger默认没有生成对象)
  params: API.deleteBlogApiBlogDeletePostParams,
  body: API.DeleteRequest,
  options?: { [key: string]: any }
) {
  return request<API.BaseResponseBool_>('/api/blog/delete', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    params: { ...params },
    data: body,
    ...(options || {}),
  })
}

/** Get Execution Logs 获取任务执行日志 GET /api/blog/execution-logs/${param0} */
export async function getExecutionLogsApiBlogExecutionLogsTaskIdGet(
  // 叠加生成的Param类型 (非body参数swagger默认没有生成对象)
  params: API.getExecutionLogsApiBlogExecutionLogsTaskIdGetParams,
  options?: { [key: string]: any }
) {
  const { task_id: param0, ...queryParams } = params
  return request<API.BaseResponseAgentExecutionStatsVO_>(`/api/blog/execution-logs/${param0}`, {
    method: 'GET',
    params: { ...queryParams },
    ...(options || {}),
  })
}

/** List Blog 分页查询博客列表 POST /api/blog/list */
export async function listBlogApiBlogListPost(
  // 叠加生成的Param类型 (非body参数swagger默认没有生成对象)
  params: API.listBlogApiBlogListPostParams,
  body: API.BlogQueryRequest,
  options?: { [key: string]: any }
) {
  return request<API.BaseResponseDict_>('/api/blog/list', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    params: { ...params },
    data: body,
    ...(options || {}),
  })
}

/** Get Progress SSE 进度推送 GET /api/blog/progress/${param0} */
export async function getProgressApiBlogProgressTaskIdGet(
  // 叠加生成的Param类型 (非body参数swagger默认没有生成对象)
  params: API.getProgressApiBlogProgressTaskIdGetParams,
  options?: { [key: string]: any }
) {
  const { task_id: param0, ...queryParams } = params
  return request<any>(`/api/blog/progress/${param0}`, {
    method: 'GET',
    params: { ...queryParams },
    ...(options || {}),
  })
}
