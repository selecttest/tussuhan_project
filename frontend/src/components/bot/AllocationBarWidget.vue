<script setup>
import { useLayout } from '@/layout/composables/layout';
import { computed, ref, watch } from 'vue';

const { layoutConfig, isDarkTheme } = useLayout();

const chartData = ref(null);
const chartOptions = ref(null);

const props = defineProps({
    payerSplit: { type: Object, default: () => ({}) }
});

const byType = computed(() => props.payerSplit.byType || []);
const tTotal = computed(() => props.payerSplit.tTotal || 0);
const fTotal = computed(() => props.payerSplit.fTotal || 0);

function setChartData() {
    const documentStyle = getComputedStyle(document.documentElement);
    return {
        labels: byType.value.map(item => item.type),
        datasets: [
            {
                label: 'T 負擔',
                data: byType.value.map(item => item.tPaid),
                backgroundColor: documentStyle.getPropertyValue('--p-primary-500'),
                borderRadius: 6,
                barThickness: 14
            },
            {
                label: 'F 負擔',
                data: byType.value.map(item => item.fPaid),
                backgroundColor: '#F59E0B',
                borderRadius: 6,
                barThickness: 14
            }
        ]
    };
}

function setChartOptions() {
    const documentStyle = getComputedStyle(document.documentElement);
    const borderColor = documentStyle.getPropertyValue('--surface-border');
    const textMutedColor = documentStyle.getPropertyValue('--text-color-secondary');
    const textColor = documentStyle.getPropertyValue('--text-color');

    return {
        indexAxis: 'y',
        maintainAspectRatio: false,
        plugins: {
            legend: { labels: { color: textColor, usePointStyle: true } },
            tooltip: {
                callbacks: {
                    label: (ctx) => ` NT$ ${ctx.parsed.x.toLocaleString()}`
                }
            }
        },
        scales: {
            x: {
                ticks: { color: textMutedColor, callback: (v) => `${(v / 1000).toFixed(0)}k` },
                grid: { color: borderColor }
            },
            y: {
                ticks: { color: textMutedColor },
                grid: { color: 'transparent' }
            }
        }
    };
}

watch([() => layoutConfig.primary, () => layoutConfig.surface, isDarkTheme, () => props.payerSplit], () => {
    chartData.value = setChartData();
    chartOptions.value = setChartOptions();
}, { deep: true, immediate: true });
</script>

<template>
    <div class="card">
        <div class="mb-6">
            <div class="font-semibold text-xl">T / F 分類負擔</div>
            <div class="text-muted-color text-sm mt-1">
                T 合計 NT$ {{ tTotal.toLocaleString() }} ／ F 合計 NT$ {{ fTotal.toLocaleString() }}
            </div>
        </div>

        <Chart type="bar" :data="chartData" :options="chartOptions" class="h-64" />

        <div class="grid gap-2 mt-6" :style="{ gridTemplateColumns: `repeat(${Math.min(byType.length, 5)}, 1fr)` }">
            <div v-for="item in byType" :key="item.type" class="text-center">
                <div class="text-xs text-muted-color mb-1">{{ item.type }}</div>
                <div class="text-xs font-semibold text-primary">
                    {{ (item.tPaid + item.fPaid).toLocaleString() }}
                </div>
            </div>
        </div>
    </div>
</template>
