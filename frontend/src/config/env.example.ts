/**
 * 环境变量配置示例
 * 复制此文件为 env.ts 并填写实际配置
 *
 * 开发环境: VITE_API_BASE_URL=http://localhost:8567/api
 * Docker 生产环境: VITE_API_BASE_URL=/api（通过 Nginx 反向代理）
 */

// API 基础地址
// import.meta.env.VITE_API_BASE_URL 在构建时由 Vite 静态替换
export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8567/api'