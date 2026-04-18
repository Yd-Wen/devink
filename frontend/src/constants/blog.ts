/**
 * 博客相关常量定义
 */

// 博客状态枚举
export enum BlogStatus {
    PENDING = 'PENDING',
    PROCESSING = 'PROCESSING',
    COMPLETED = 'COMPLETED',
    FAILED = 'FAILED',
}

// 状态文本映射
export const STATUS_TEXT_MAP: Record<string, string> = {
    [BlogStatus.PENDING]: '等待中',
    [BlogStatus.PROCESSING]: '生成中',
    [BlogStatus.COMPLETED]: '已完成',
    [BlogStatus.FAILED]: '失败',
}

// 状态颜色映射（用于 Ant Design Tag）
export const STATUS_TAG_COLOR_MAP: Record<string, string> = {
    [BlogStatus.PENDING]: 'default',
    [BlogStatus.PROCESSING]: 'processing',
    [BlogStatus.COMPLETED]: 'success',
    [BlogStatus.FAILED]: 'error',
}

// 状态颜色映射（用于自定义样式）
export const STATUS_COLOR_MAP: Record<string, string> = {
    [BlogStatus.PENDING]: '#6B7280',
    [BlogStatus.PROCESSING]: '#3B82F6',
    [BlogStatus.COMPLETED]: '#22C55E',
    [BlogStatus.FAILED]: '#EF4444',
}

// 博客创作相关
export const MAX_TOPIC_LENGTH = 500
export const DEFAULT_TOTAL_IMAGES = 5

// 状态筛选选项
export const STATUS_OPTIONS = [
    { value: '', label: '全部状态' },
    { value: BlogStatus.COMPLETED, label: '已完成' },
    { value: BlogStatus.PROCESSING, label: '生成中' },
    { value: BlogStatus.PENDING, label: '等待中' },
    { value: BlogStatus.FAILED, label: '失败' },
]
