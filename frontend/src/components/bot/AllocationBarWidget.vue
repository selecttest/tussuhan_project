<script setup>
import { useLayout } from '@/layout/composables/layout';
import { computed, ref, watch } from 'vue';

const { layoutConfig, isDarkTheme } = useLayout();

const chartData = ref(null);
const chartOptions = ref(null);

const props = defineProps({
    allocation: { type: Object, default: () => ({}) }
});

const totalIncome = computed(() => props.allocation.totalIncome || 0);
const allocations = computed(() => props.allocation.items || []);

function setChartData() {
    const documentStyle = getComputedStyle(document.documentElement);
    return {
        labels: allocations.value.map((a) => a.label),
        datasets: [
            {
                label: '預算',
                data: allocations.value.map((a) => a.budgeted),
                backgroundColor: `${documentStyle.getPropertyValue('--p-primary-300')}80`,
                borderColor: documentStyle.getPropertyValue('--p-primary-300'),
                borderWidth: 1,
                barThickness: 14
            },
            {
                label: '實際',
                data: allocations.value.map((a) => a.actual),
                backgroundColor: documentStyle.getPropertyValue('--p-primary-500'),
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
            legend: {
                labels: { color: textColor, usePointStyle: true }
            },
            tooltip: {
                callbacks: {
                    label: (ctx) => ` NT$ ${ctx.parsed.x.toLocaleString()}`
                }
            }
        },
        scales: {
            x: {
                ticks: {
                    color: textMutedColor,
                    callback: (v) => `${(v / 1000).toFixed(0)}k`
                },
                grid: { color: borderColor }
            },
            y: {
                ticks: { color: textMutedColor },
                grid: { color: 'transparent' }
            }
        }
    };
}

watch([() => layoutConfig.primary, () => layoutConfig.surface, isDarkTheme, () => props.allocation], () => {
    chartData.value = setChartData();
    chartOptions.value = setChartOptions();
}, { deep: true, immediate: true });
</script>

<template>
    <div class="card">
        <div class="mb-6">
            <div class="font-semibold text-xl">財務分配概覽</div>
            <div class="text-muted-color text-sm mt-1">預算 vs 實際支出對比（NT$ {{ totalIncome.toLocaleString() }} 月收入基準）</div>
        </div>

        <Chart type="bar" :data="chartData" :options="chartOptions" class="h-64" />

        <div class="grid grid-cols-5 gap-2 mt-6">
            <div v-for="item in allocations" :key="item.label" class="text-center">
                <div class="text-xs text-muted-color mb-1">{{ item.label.split(' ')[0] }}</div>
                <div
                    class="text-xs font-semibold"
                    :class="item.actual > item.budgeted ? 'text-red-500' : 'text-green-500'"
                >
                    {{ item.actual > item.budgeted ? '超支' : '正常' }}
                </div>
            </div>
        </div>
    </div>
</template>
