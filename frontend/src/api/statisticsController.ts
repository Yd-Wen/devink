// @ts-ignore
/* eslint-disable */
import request from '@/request'

/** Get Statistics 获取系统统计数据（仅管理员） GET /api/statistics/overview */
export async function getStatistics(
  // 叠加生成的Param类型 (非body参数swagger默认没有生成对象)
  params: API.getStatisticsParams,
  options?: { [key: string]: any }
) {
  return request<API.BaseResponseStatisticsVO_>('/api/statistics/overview', {
    method: 'GET',
    params: { ...params },
    ...(options || {}),
  })
}
