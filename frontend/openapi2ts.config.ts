// openapi2ts.config.ts
export default {
    requestLibPath: "import request from '@/request'",
    schemaPath: 'http://localhost:8567/openapi.json',
    serversPath: './src',
    hook: {
        customFunctionName: (data) => {
            const { operationId, method } = data;

            // snake_case 转 camelCase
            // get_login_user_api_user_get_login_get -> getLoginUser
            const clean = operationId
                .replace(/_api_.*$/, '')           // 移除 _api_ 及之后所有内容
                .replace(/_get$|_post$|_put$|_delete$|_patch$/, '') // 移除末尾方法标记
                .split('_')                         // 按下划线分割
                .map((word, index) =>
                    index === 0
                        ? word                      // 首单词小写
                        : word.charAt(0).toUpperCase() + word.slice(1) // 后续首字母大写
                )
                .join('');                          // 拼接

            return clean;
        },
    },
}