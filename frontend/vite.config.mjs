import { fileURLToPath, URL } from 'node:url';

import { PrimeVueResolver } from '@primevue/auto-import-resolver';
import tailwindcss from '@tailwindcss/vite';
import vue from '@vitejs/plugin-vue';
import legacy from '@vitejs/plugin-legacy';
import VueDevTools from 'vite-plugin-vue-devtools';
import Components from 'unplugin-vue-components/vite';
import { defineConfig, loadEnv } from 'vite';
import { transform as lcssTransform, browserslistToTargets } from 'lightningcss';
import browserslist from 'browserslist';

function iosCompatCssPlugin() {
    return {
        name: 'ios-compat-css',
        apply: 'build',
        enforce: 'post',
        generateBundle(_, bundle) {
            const targets = browserslistToTargets(browserslist(['iOS >= 14', 'safari >= 14']));
            for (const chunk of Object.values(bundle)) {
                if (chunk.type !== 'asset' || !chunk.fileName.endsWith('.css')) continue;
                try {
                    const result = lcssTransform({
                        filename: chunk.fileName,
                        code: Buffer.from(typeof chunk.source === 'string' ? chunk.source : chunk.source),
                        targets,
                        minify: true,
                        drafts: { customMedia: true }
                    });
                    chunk.source = result.code.toString();
                } catch {
                    // 若轉換失敗保留原始 CSS
                }
            }
        }
    };
}

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
        build: {
            target: ['es2020', 'safari14']
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
            }),
            legacy({
                targets: ['ios >= 14', 'safari >= 14'],
                modernPolyfills: true
            }),
            iosCompatCssPlugin()
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
