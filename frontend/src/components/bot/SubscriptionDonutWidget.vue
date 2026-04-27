<script setup>
import { useLayout } from '@/layout/composables/layout';
import { computed, ref, watch } from 'vue';

const { layoutConfig, isDarkTheme } = useLayout();

const chartData = ref(null);
const chartOptions = ref(null);

const props = defineProps({
    subscriptions: { type: Object, default: () => ({}) }
});

const subscriptionItems = computed(() => props.subscriptions.items || []);
const totalSub = computed(() => props.subscriptions.total || subscriptionItems.value.reduce((sum, item) => sum + Number(item.fee || 0), 0));

function setChartData() {
    return {
        labels: subscriptionItems.value.map((s) => s.name),
        datasets: [
            {
                data: subscriptionItems.value.map((s) => s.fee),
                backgroundColor: subscriptionItems.value.map((s) => s.color),
                hoverBackgroundColor: subscriptionItems.value.map((s) => `${s.color}CC`),
                borderWidth: 2,
                borderColor: 'transparent'
            }
        ]
    };
}

function setChartOptions() {
    const documentStyle = getComputedStyle(document.documentElement);
    const textColor = documentStyle.getPropertyValue('--text-color');
    return {
        maintainAspectRatio: false,
        plugins: {
            legend: {
                position: 'bottom',
                labels: { color: textColor, usePointStyle: true, padding: 12 }
            },
            tooltip: {
                callbacks: {
                    label: (ctx) => {
                        const pct = totalSub.value ? ((ctx.parsed / totalSub.value) * 100).toFixed(1) : '0.0';
                        return ` NT$ ${ctx.parsed} (${pct}%)`;
                    }
                }
            }
        },
        cutout: '60%'
    };
}

watch([() => layoutConfig.primary, () => layoutConfig.surface, isDarkTheme, () => props.subscriptions], () => {
    chartData.value = setChartData();
    chartOptions.value = setChartOptions();
}, { deep: true, immediate: true });
</script>

<template>
    <div class="card">
        <div class="flex items-center justify-between mb-4">
            <div>
                <div class="font-semibold text-xl">串流訂閱費用</div>
                <div class="text-muted-color text-sm mt-1">每月合計 NT$ {{ totalSub.toLocaleString() }}</div>
            </div>
            <Tag severity="secondary" :value="`${subscriptionItems.length} 項服務`" />
        </div>

        <div class="relative">
            <Chart type="doughnut" :data="chartData" :options="chartOptions" class="h-60" />
            <div class="absolute inset-0 flex items-center justify-center pointer-events-none" style="padding-bottom: 3.5rem">
                <div class="text-center">
                    <div class="text-muted-color text-xs">月訂閱</div>
                    <div class="font-bold text-lg">NT$ {{ totalSub.toLocaleString() }}</div>
                </div>
            </div>
        </div>

        <div class="flex flex-col gap-2 mt-4">
            <div v-for="sub in subscriptionItems" :key="sub.name" class="flex items-center justify-between">
                <div class="flex items-center gap-2">
                    <div class="w-2.5 h-2.5 rounded-full" :style="{ backgroundColor: sub.color }"></div>
                    <span class="text-sm">{{ sub.name }}</span>
                    <Tag :value="sub.cycle" severity="secondary" class="text-xs!" />
                </div>
                <span class="font-semibold text-sm">NT$ {{ sub.fee }}</span>
            </div>
        </div>
    </div>
</template>
