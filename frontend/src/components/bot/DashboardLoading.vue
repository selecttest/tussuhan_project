<script setup>
defineProps({
    message: { type: String, default: '正在從 Google Sheets 載入資料...' }
});
</script>

<template>
    <div class="fixed inset-0 z-[1000] flex items-center justify-center" style="background: rgba(0,0,0,0.18); backdrop-filter: blur(2px);">
        <div class="flex flex-col items-center gap-6 px-14 py-[4.2rem] rounded-2xl bg-surface-0 dark:bg-surface-800 shadow-2xl border border-surface-200 dark:border-surface-700 min-w-[22rem]">
            <div class="flex items-center justify-center" style="width:7.5rem;height:7.5rem;flex-shrink:0">
                <div class="relative flex items-center justify-center" style="width:6.25rem;height:6.25rem">
                    <div class="absolute inset-0 rounded-full border-[5px] border-surface-200 dark:border-surface-700"></div>
                    <div class="absolute inset-0 rounded-full border-[5px] border-t-primary border-r-transparent border-b-transparent border-l-transparent animate-spin"></div>
                    <i class="pi pi-wallet text-primary" style="font-size:2.25rem"></i>
                </div>
            </div>

            <div class="text-center">
                <div class="font-semibold text-surface-900 dark:text-surface-0 text-xl mb-1">載入中</div>
                <div class="text-muted-color">{{ message }}</div>
            </div>

            <div class="flex gap-2">
                <div class="w-2.5 h-2.5 rounded-full bg-primary animate-bounce" style="animation-delay:0ms"></div>
                <div class="w-2.5 h-2.5 rounded-full bg-primary animate-bounce" style="animation-delay:150ms"></div>
                <div class="w-2.5 h-2.5 rounded-full bg-primary animate-bounce" style="animation-delay:300ms"></div>
            </div>
        </div>
    </div>
</template>
