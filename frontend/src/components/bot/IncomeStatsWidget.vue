<script setup>
const props = defineProps({
    totalExpense: { type: Number, default: 0 },
    tTotal: { type: Number, default: 0 },
    fTotal: { type: Number, default: 0 },
    todayExpense: { type: Number, default: 0 }
});

function fmt(value) {
    return `NT$ ${value.toLocaleString('zh-TW')}`;
}
</script>

<template>
    <div class="col-span-12 lg:col-span-6 xl:col-span-3">
        <div class="card mb-0">
            <div class="flex justify-between mb-4">
                <div>
                    <span class="block text-muted-color font-medium mb-4">本月總支出</span>
                    <div class="text-surface-900 dark:text-surface-0 font-medium text-xl">{{ fmt(totalExpense) }}</div>
                </div>
                <div class="flex items-center justify-center bg-red-100 dark:bg-red-400/10 rounded-border" style="width:2.5rem;height:2.5rem">
                    <i class="pi pi-shopping-cart text-red-500 text-xl!"></i>
                </div>
            </div>
            <span class="text-muted-color text-sm">累計所有分類支出</span>
        </div>
    </div>

    <div class="col-span-12 lg:col-span-6 xl:col-span-3">
        <div class="card mb-0">
            <div class="flex justify-between mb-4">
                <div>
                    <span class="block text-muted-color font-medium mb-4">T 負擔</span>
                    <div class="text-surface-900 dark:text-surface-0 font-medium text-xl">{{ fmt(tTotal) }}</div>
                </div>
                <div class="flex items-center justify-center bg-blue-100 dark:bg-blue-400/10 rounded-border" style="width:2.5rem;height:2.5rem">
                    <i class="pi pi-user text-blue-500 text-xl!"></i>
                </div>
            </div>
            <span class="text-muted-color text-sm">
                {{ totalExpense ? ((tTotal / totalExpense) * 100).toFixed(1) : '0.0' }}% 佔比
            </span>
        </div>
    </div>

    <div class="col-span-12 lg:col-span-6 xl:col-span-3">
        <div class="card mb-0">
            <div class="flex justify-between mb-4">
                <div>
                    <span class="block text-muted-color font-medium mb-4">F 負擔</span>
                    <div class="text-surface-900 dark:text-surface-0 font-medium text-xl">{{ fmt(fTotal) }}</div>
                </div>
                <div class="flex items-center justify-center bg-orange-100 dark:bg-orange-400/10 rounded-border" style="width:2.5rem;height:2.5rem">
                    <i class="pi pi-users text-orange-500 text-xl!"></i>
                </div>
            </div>
            <span class="text-muted-color text-sm">
                {{ totalExpense ? ((fTotal / totalExpense) * 100).toFixed(1) : '0.0' }}% 佔比
            </span>
        </div>
    </div>

    <div class="col-span-12 lg:col-span-6 xl:col-span-3">
        <div class="card mb-0">
            <div class="flex justify-between mb-4">
                <div>
                    <span class="block text-muted-color font-medium mb-4">今日支出</span>
                    <div class="text-surface-900 dark:text-surface-0 font-medium text-xl">{{ fmt(todayExpense) }}</div>
                </div>
                <div class="flex items-center justify-center bg-green-100 dark:bg-green-400/10 rounded-border" style="width:2.5rem;height:2.5rem">
                    <i class="pi pi-calendar-clock text-green-500 text-xl!"></i>
                </div>
            </div>
            <span class="text-muted-color text-sm">今日所有消費加總</span>
        </div>
    </div>
</template>
