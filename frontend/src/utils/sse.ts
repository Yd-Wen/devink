/**
 * SSE 工具函数
 */
import { API_BASE_URL } from '@/config/env'

export interface SSEMessage {
    type: string
    data?: any
    [key: string]: any
}

export interface SSEOptions {
    onMessage: (message: SSEMessage) => void
    onError?: (error: Event) => void
    onComplete?: () => void
}

/**
 * 从 Cookie 中获取 session_id
 */
function getSessionIdFromCookie(): string {
    const cookies = document.cookie.split(';')
    for (const cookie of cookies) {
        const [name, value] = cookie.trim().split('=')
        if (name === 'SESSION_ID') {
            return value || ''
        }
    }
    return ''
}

/**
 * 建立 SSE 连接
 */
export const connectSSE = (taskId: string, options: SSEOptions): EventSource => {
    const { onMessage, onError, onComplete } = options

    // 从 Cookie 获取 session_id 并添加到 URL
    const sessionId = getSessionIdFromCookie()
    console.log('[SSE] sessionId from cookie:', sessionId)
    const url = sessionId
        ? `${API_BASE_URL}/blog/progress/${taskId}?session_id=${sessionId}`
        : `${API_BASE_URL}/blog/progress/${taskId}`
    console.log('[SSE] url:', url)

    const eventSource = new EventSource(url)

    eventSource.onmessage = (event) => {
        try {
            const message: SSEMessage = JSON.parse(event.data)
            onMessage(message)

            // 检查是否完成
            if (message.type === 'ALL_COMPLETE' || message.type === 'ERROR') {
                eventSource.close()
                onComplete?.()
            }
        } catch (error) {
            console.error('SSE 消息解析失败:', error)
        }
    }

    eventSource.onerror = (error) => {
        console.error('SSE 连接错误:', error)
        onError?.(error)
        eventSource.close()
    }

    return eventSource
}

/**
 * 关闭 SSE 连接
 */
export const closeSSE = (eventSource: EventSource | null) => {
    if (eventSource) {
        eventSource.close()
    }
}
