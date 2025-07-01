const { defineConfig } = require('@vue/cli-service');
module.exports = defineConfig({
    transpileDependencies: true,
    lintOnSave: false,
    productionSourceMap: false,
    chainWebpack: config => {
        config.plugin('html').tap(args => {
            args[0].title = '数字孪生富水水库';
            return args;
        });
    },
    devServer: {
        //http://10.42.173.20:8088
        // proxy: {
        //     '/api': {
        //         target: 'http://localhost:8066/', // 目标域
        //         changeOrigin: true, // 允许跨域
        //         pathRewrite: {
        //             '^/api': '' // 重写路径
        //         }
        //     }
        // }
    }
});
