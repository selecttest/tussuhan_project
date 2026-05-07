import { fileURLToPath, URL } from 'node:url';

import { PrimeVueResolver } from '@primevue/auto-import-resolver';
import tailwindcss from '@tailwindcss/vite';
import vue from '@vitejs/plugin-vue';
import VueDevTools from 'vite-plugin-vue-devtools';
import Components from 'unplugin-vue-components/vite';
import { defineConfig, loadEnv } from 'vite';

// https://vitejs.dev/config/
export default defineConfig(({ mode }) => {
    const env = loadEnv(mode, process.cwd(), '');
    /** 記帳後端位址；8000 常被其他專案占用時可設為 http://127.0.0.1:8001 */
    const apiProxyTarget = env.VITE_API_PROXY_TARGET || 'http://127.0.0.1:8000';

    return {
        server: {
            host: '0.0.0.0',
            port: 3000,
            proxy: {
                '/api': {
                    target: apiProxyTarget,
                    changeOrigin: true
                }
            }
        },
        preview: {
            host: '0.0.0.0',
            port: 3000
        },
        optimizeDeps: {
            noDiscovery: true
        },
        plugins: [
            vue(),
            VueDevTools(),
            tailwindcss(),
            Components({
                resolvers: [PrimeVueResolver()]
            })
        ],
        resolve: {
            alias: {
                '@': fileURLToPath(new URL('./src', import.meta.url))
            }
        },
        css: {
            preprocessorOptions: {
                scss: {
                    api: 'modern-compiler'
                }
            }
        }
    };
});
