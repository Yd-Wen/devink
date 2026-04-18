// @ts-ignore
/* eslint-disable */
import request from '@/request'

/** Root 根路径 GET / */
export async function rootGet(options?: { [key: string]: any }) {
  return request<any>('/', {
    method: 'GET',
    ...(options || {}),
  })
}
