<script setup>
import { useLayout } from '@/layout/composables/layout';
import { computed, ref, watch } from 'vue';

const { layoutConfig, isDarkTheme } = useLayout();

const chartData = ref(null);
const chartOptions = ref(null);
const activeTab = ref(0);

const props = defineProps({
    revenue: { type: Object, default: () => ({}) }
});

const items = computed(() => props.revenue.items || []);
const labels = computed(() => props.revenue.chart?.labels || items.value.map((item) => item.label));
const values = computed(() => props.revenue.chart?.values || items.value.map((item) => item.value));
const totalIncome = computed(() => props.revenue.total || values.value.reduce((sum, value) => sum + Number(value || 0), 0));

function setChartData() {
    const documentStyle = getComputedStyle(document.documentElement);
    return {
        labels: labels.value,
        datasets: [
            {
                data: values.value,
                backgroundColor: [
                    documentStyle.getPropertyValue('--p-primary-500'),
                    documentStyle.getPropertyValue('--p-primary-400'),
                    documentStyle.getPropertyValue('--p-primary-300'),
                    documentStyle.getPropertyValue('--p-primary-200'),
                    documentStyle.getPropertyValue('--p-primary-100')
                ],
                hoverBackgroundColor: [
                    documentStyle.getPropertyValue('--p-primary-400'),
                    documentStyle.getPropertyValue('--p-primary-300'),
                    documentStyle.getPropertyValue('--p-primary-200'),
                    documentStyle.getPropertyValue('--p-primary-100'),
                    documentStyle.getPropertyValue('--p-primary-50')
                ]
            }
        ]
    };
}

function setChartOptions() {
    const documentStyle = getComputedStyle(document.documentElement);
    const textColor = documentStyle.getPropertyValue('--text-color');
    const textMutedColor = documentStyle.getPropertyValue('--text-color-secondary');
    return {
        maintainAspectRatio: false,
        plugins: {
            legend: {
                position: 'bottom',
                labels: {
                    color: textColor,
                    usePointStyle: true,
                    padding: 16
                }
            },
            tooltip: {
                callbacks: {
                    label: function (context) {
                        const total = context.dataset.data.reduce((a, b) => a + b, 0);
                        const value = context.parsed;
                        const pct = ((value / total) * 100).toFixed(1);
                        return ` NT$ ${value.toLocaleString()} (${pct}%)`;
                    }
                }
            }
        },
        cutout: '65%'
    };
}

watch([() => layoutConfig.primary, () => layoutConfig.surface, isDarkTheme, () => props.revenue], () => {
    chartData.value = setChartData();
    chartOptions.value = setChartOptions();
}, { deep: true, immediate: true });
</script>

<template>
    <div class="card">
        <div class="flex items-center justify-between mb-4">
            <div class="font-semibold text-xl">營收結構分析</div>
            <SelectButton v-model="activeTab" :options="[{ label: '當月佔比', value: 0 }, { label: '收入明細', value: 1 }]" option-label="label" option-value="value" size="small" />
        </div>

        <div v-if="activeTab === 0">
            <div class="relative">
                <Chart type="doughnut" :data="chartData" :options="chartOptions" class="h-72" />
                <div class="absolute inset-0 flex items-center justify-center pointer-events-none">
                    <div class="text-center">
                        <div class="text-muted-color text-sm">本月總收入</div>
                        <div class="font-bold text-xl text-surface-900 dark:text-surface-0">NT$ {{ totalIncome.toLocaleString() }}</div>
                    </div>
                </div>
            </div>
        </div>

        <div v-else>
            <div class="flex flex-col gap-3 mt-2">
                <div v-for="(label, i) in labels" :key="label" class="flex items-center justify-between p-3 rounded-lg bg-surface-50 dark:bg-surface-800">
                    <div class="flex items-center gap-3">
                        <div class="w-3 h-3 rounded-full" :style="{ backgroundColor: `hsl(${220 + i * 20}, 70%, ${60 - i * 5}%)` }"></div>
                        <span class="font-medium">{{ label }}</span>
                    </div>
                    <div class="text-right">
                        <div class="font-semibold">NT$ {{ Number(values[i] || 0).toLocaleString() }}</div>
                        <div class="text-muted-color text-sm">{{ totalIncome ? ((Number(values[i] || 0) / totalIncome) * 100).toFixed(1) : '0.0' }}%</div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>
