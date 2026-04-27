<script setup>
const props = defineProps({
    totalIncome: { type: Number, default: 0 },
    totalExpense: { type: Number, default: 0 },
    netIncome: { type: Number, default: 0 },
    totalSubscription: { type: Number, default: 0 },
    subscriptionCount: { type: Number, default: 0 }
});

function formatNTD(value) {
    return `NT$ ${value.toLocaleString('zh-TW')}`;
}
</script>

<template>
    <div class="col-span-12 lg:col-span-6 xl:col-span-3">
        <div class="card mb-0">
            <div class="flex justify-between mb-4">
                <div>
                    <span class="block text-muted-color font-medium mb-4">本月總收入</span>
                    <div class="text-surface-900 dark:text-surface-0 font-medium text-xl">{{ formatNTD(totalIncome) }}</div>
                </div>
                <div class="flex items-center justify-center bg-green-100 dark:bg-green-400/10 rounded-border" style="width: 2.5rem; height: 2.5rem">
                    <i class="pi pi-arrow-up text-green-500 text-xl!"></i>
                </div>
            </div>
            <span class="text-green-500 font-medium">+12.3% </span>
            <span class="text-muted-color">較上個月</span>
        </div>
    </div>

    <div class="col-span-12 lg:col-span-6 xl:col-span-3">
        <div class="card mb-0">
            <div class="flex justify-between mb-4">
                <div>
                    <span class="block text-muted-color font-medium mb-4">本月總支出</span>
                    <div class="text-surface-900 dark:text-surface-0 font-medium text-xl">{{ formatNTD(totalExpense) }}</div>
                </div>
                <div class="flex items-center justify-center bg-red-100 dark:bg-red-400/10 rounded-border" style="width: 2.5rem; height: 2.5rem">
                    <i class="pi pi-arrow-down text-red-500 text-xl!"></i>
                </div>
            </div>
            <span class="text-red-500 font-medium">-5.8% </span>
            <span class="text-muted-color">較上個月</span>
        </div>
    </div>

    <div class="col-span-12 lg:col-span-6 xl:col-span-3">
        <div class="card mb-0">
            <div class="flex justify-between mb-4">
                <div>
                    <span class="block text-muted-color font-medium mb-4">本月淨收入</span>
                    <div class="text-surface-900 dark:text-surface-0 font-medium text-xl">{{ formatNTD(netIncome) }}</div>
                </div>
                <div class="flex items-center justify-center bg-blue-100 dark:bg-blue-400/10 rounded-border" style="width: 2.5rem; height: 2.5rem">
                    <i class="pi pi-wallet text-blue-500 text-xl!"></i>
                </div>
            </div>
            <span class="text-primary font-medium">財務健康 </span>
            <span class="text-muted-color">結餘良好</span>
        </div>
    </div>

    <div class="col-span-12 lg:col-span-6 xl:col-span-3">
        <div class="card mb-0">
            <div class="flex justify-between mb-4">
                <div>
                    <span class="block text-muted-color font-medium mb-4">每月訂閱費</span>
                    <div class="text-surface-900 dark:text-surface-0 font-medium text-xl">{{ formatNTD(totalSubscription) }}</div>
                </div>
                <div class="flex items-center justify-center bg-purple-100 dark:bg-purple-400/10 rounded-border" style="width: 2.5rem; height: 2.5rem">
                    <i class="pi pi-credit-card text-purple-500 text-xl!"></i>
                </div>
            </div>
            <span class="text-purple-500 font-medium">{{ subscriptionCount }} 項服務 </span>
            <span class="text-muted-color">訂閱中</span>
        </div>
    </div>
</template>
