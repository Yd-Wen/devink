// @ts-ignore
/* eslint-disable */
import request from '@/request'

/** Get Statistics 获取系统统计数据（仅管理员） GET /api/statistics/overview */
export async function getStatistics(
    options?: { [key: string]: any }
) {
    return request<API.BaseResponseStatisticsVO>('/statistics/overview', {
        method: 'GET',
        ...(options || {}),
    })
}
