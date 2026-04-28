<script setup>
import { useLayout } from '@/layout/composables/layout';
import { computed, ref, watch } from 'vue';

const { layoutConfig, isDarkTheme } = useLayout();

const chartData = ref(null);
const chartOptions = ref(null);

const props = defineProps({
    trend: { type: Object, default: () => ({}) }
});

const months = computed(() => props.trend.months || []);
const expenseValues = computed(() => props.trend.expenseValues || []);
const tValues = computed(() => props.trend.tValues || []);
const fValues = computed(() => props.trend.fValues || []);

function setChartData() {
    const documentStyle = getComputedStyle(document.documentElement);
    return {
        labels: months.value,
        datasets: [
            {
                label: '總支出',
                data: expenseValues.value,
                fill: true,
                backgroundColor: 'rgba(239,68,68,0.08)',
                borderColor: 'rgb(239,68,68)',
                tension: 0.4,
                pointBackgroundColor: 'rgb(239,68,68)',
                pointRadius: 5,
                pointHoverRadius: 7
            },
            {
                label: 'T 負擔',
                data: tValues.value,
                fill: false,
                borderColor: documentStyle.getPropertyValue('--p-primary-500'),
                borderDash: [5, 5],
                tension: 0.4,
                pointBackgroundColor: documentStyle.getPropertyValue('--p-primary-500'),
                pointRadius: 4,
                pointHoverRadius: 6
            },
            {
                label: 'F 負擔',
                data: fValues.value,
                fill: false,
                borderColor: '#F59E0B',
                borderDash: [5, 5],
                tension: 0.4,
                pointBackgroundColor: '#F59E0B',
                pointRadius: 4,
                pointHoverRadius: 6
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
        maintainAspectRatio: false,
        plugins: {
            legend: { labels: { color: textColor, usePointStyle: true } },
            tooltip: {
                callbacks: {
                    label: (ctx) => ` NT$ ${ctx.parsed.y.toLocaleString()}`
                }
            }
        },
        scales: {
            x: { ticks: { color: textMutedColor }, grid: { color: borderColor } },
            y: {
                ticks: { color: textMutedColor, callback: (v) => `${(v / 1000).toFixed(0)}k` },
                grid: { color: borderColor }
            }
        }
    };
}

watch([() => layoutConfig.primary, () => layoutConfig.surface, isDarkTheme, () => props.trend], () => {
    chartData.value = setChartData();
    chartOptions.value = setChartOptions();
}, { deep: true, immediate: true });
</script>

<template>
    <div class="card">
        <div class="flex items-center justify-between mb-6">
            <div>
                <div class="font-semibold text-xl">月度支出趨勢</div>
                <div class="text-muted-color text-sm mt-1">近 6 個月 T / F 負擔變化</div>
            </div>
            <div class="flex gap-4 flex-wrap">
                <div class="flex items-center gap-2">
                    <div class="w-3 h-1 rounded bg-red-500"></div>
                    <span class="text-muted-color text-sm">總支出</span>
                </div>
                <div class="flex items-center gap-2">
                    <div class="w-3 h-1 rounded bg-primary"></div>
                    <span class="text-muted-color text-sm">T 負擔</span>
                </div>
                <div class="flex items-center gap-2">
                    <div class="w-3 h-1 rounded" style="background:#F59E0B"></div>
                    <span class="text-muted-color text-sm">F 負擔</span>
                </div>
            </div>
        </div>
        <Chart type="line" :data="chartData" :options="chartOptions" class="h-72" />
    </div>
</template>
