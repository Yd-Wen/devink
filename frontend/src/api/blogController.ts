// @ts-ignore
/* eslint-disable */
import request from '@/request'

/** Get Blog 获取博客详情 GET /blog/${param0} */
export async function getBlog(
    // 叠加生成的Param类型 (非body参数swagger默认没有生成对象)
    params: API.getBlogParams,
    options?: { [key: string]: any }
) {
    const { taskId: param0, ...queryParams } = params
    return request<API.BaseResponseBlogVO>(`/blog/${param0}`, {
        method: 'GET',
        params: { ...queryParams },
        ...(options || {}),
    })
}

/** Ai Modify Outline AI 修改大纲 POST /blog/ai-modify-outline */
export async function aiModifyOutline(
    body: API.BlogAiModifyOutlineRequest,
    options?: { [key: string]: any }
) {
    return request<API.BaseResponseListOutlineSection>('/blog/ai-modify-outline', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        data: body,
        ...(options || {}),
    })
}

/** Confirm Outline 确认大纲 POST /blog/confirm-outline */
export async function confirmOutline(
    body: API.BlogConfirmOutlineRequest,
    options?: { [key: string]: any }
) {
    return request<API.BaseResponseVoid>('/blog/confirm-outline', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        data: body,
        ...(options || {}),
    })
}

/** Confirm Title 确认标题并输入补充描述 POST /blog/confirm-title */
export async function confirmTitle(
    body: API.BlogConfirmTitleRequest,
    options?: { [key: string]: any }
) {
    return request<API.BaseResponseVoid>('/blog/confirm-title', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        data: body,
        ...(options || {}),
    })
}

/** Create Blog 创建博客任务 POST /blog/create */
export async function createBlog(
    body: API.BlogCreateRequest,
    options?: { [key: string]: any }
) {
    return request<API.BaseResponseString>('/blog/create', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        data: body,
        ...(options || {}),
    })
}

/** Delete Blog 删除博客 POST /blog/delete */
export async function deleteBlog(
    body: API.DeleteRequest,
    options?: { [key: string]: any }
) {
    return request<API.BaseResponseBoolean>('/blog/delete', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        data: body,
        ...(options || {}),
    })
}

/** Get Execution Logs 获取任务执行日志 GET /blog/execution-logs/${param0} */
export async function getExecutionLogs(
    // 叠加生成的Param类型 (非body参数swagger默认没有生成对象)
    params: API.getExecutionLogsParams,
    options?: { [key: string]: any }
) {
    const { taskId: param0, ...queryParams } = params
    return request<API.BaseResponseAgentExecutionStats>(`/blog/execution-logs/${param0}`, {
        method: 'GET',
        params: { ...queryParams },
        ...(options || {}),
    })
}

/** List Blog 分页查询博客列表 POST /blog/list */
export async function listBlog(
    body: API.BlogQueryRequest,
    options?: { [key: string]: any }
) {
    return request<API.BaseResponsePageBlogVO>('/blog/list', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        data: body,
        ...(options || {}),
    })
}

/** Get Progress SSE 进度推送 GET /blog/progress/${param0} */
export async function getProgress(
    // 叠加生成的Param类型 (非body参数swagger默认没有生成对象)
    params: API.getProgressParams,
    options?: { [key: string]: any }
) {
    const { taskId: param0, ...queryParams } = params
    return request<any>(`/blog/progress/${param0}`, {
        method: 'GET',
        params: { ...queryParams },
        ...(options || {}),
    })
}
