/**
 * Markdown 工具函数
 */
import { marked } from 'marked'

/**
 * Markdown 转 HTML
 * @param markdown Markdown 内容
 */
export const markdownToHtml = (markdown: string): string => {
    return marked(markdown) as string
}
