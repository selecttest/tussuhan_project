<script setup>
import { useLayout } from '@/layout/composables/layout';
import { computed, ref, watch } from 'vue';

const { layoutConfig, isDarkTheme } = useLayout();

const chartData = ref(null);
const chartOptions = ref(null);
const activeTab = ref(0);

const props = defineProps({
    typeBreakdown: { type: Object, default: () => ({}) }
});

const items = computed(() => props.typeBreakdown.items || []);
const labels = computed(() => props.typeBreakdown.chart?.labels || items.value.map(i => i.label));
const values = computed(() => props.typeBreakdown.chart?.values || items.value.map(i => i.value));
const total = computed(() => props.typeBreakdown.total || 0);

const TYPE_COLORS = {
    Food: '#3B82F6',
    Baby: '#F59E0B',
    Drink: '#10B981',
    Tuition: '#8B5CF6',
    Other: '#6B7280',
};

function getColor(label, idx) {
    return TYPE_COLORS[label] || `hsl(${220 + idx * 30}, 65%, ${55 - idx * 3}%)`;
}

function setChartData() {
    return {
        labels: labels.value,
        datasets: [{
            data: values.value,
            backgroundColor: labels.value.map((l, i) => getColor(l, i)),
            hoverBackgroundColor: labels.value.map((l, i) => `${getColor(l, i)}CC`),
        }]
    };
}

function setChartOptions() {
    const documentStyle = getComputedStyle(document.documentElement);
    const textColor = documentStyle.getPropertyValue('--text-color');
    return {
        maintainAspectRatio: false,
        plugins: {
            legend: { position: 'bottom', labels: { color: textColor, usePointStyle: true, padding: 16 } },
            tooltip: {
                callbacks: {
                    label: (ctx) => {
                        const pct = total.value ? ((ctx.parsed / total.value) * 100).toFixed(1) : '0.0';
                        return ` NT$ ${ctx.parsed.toLocaleString()} (${pct}%)`;
                    }
                }
            }
        },
        cutout: '65%'
    };
}

watch([() => layoutConfig.primary, () => layoutConfig.surface, isDarkTheme, () => props.typeBreakdown], () => {
    chartData.value = setChartData();
    chartOptions.value = setChartOptions();
}, { deep: true, immediate: true });
</script>

<template>
    <div class="card">
        <div class="flex items-center justify-between mb-4">
            <div class="font-semibold text-xl">支出分類分析</div>
            <SelectButton
                v-model="activeTab"
                :options="[{ label: '圓餅圖', value: 0 }, { label: '明細', value: 1 }]"
                option-label="label" option-value="value" size="small"
            />
        </div>

        <div v-if="activeTab === 0">
            <div class="relative">
                <Chart type="doughnut" :data="chartData" :options="chartOptions" class="h-72" />
                <div class="absolute inset-0 flex items-center justify-center pointer-events-none" style="padding-bottom:3.5rem">
                    <div class="text-center">
                        <div class="text-muted-color text-sm">本月總支出</div>
                        <div class="font-bold text-xl text-surface-900 dark:text-surface-0">NT$ {{ total.toLocaleString() }}</div>
                    </div>
                </div>
            </div>
        </div>

        <div v-else>
            <div class="flex flex-col gap-3 mt-2">
                <div v-for="(label, i) in labels" :key="label" class="flex items-center justify-between p-3 rounded-lg bg-surface-50 dark:bg-surface-800">
                    <div class="flex items-center gap-3">
                        <div class="w-3 h-3 rounded-full" :style="{ backgroundColor: getColor(label, i) }"></div>
                        <span class="font-medium">{{ label }}</span>
                    </div>
                    <div class="text-right">
                        <div class="font-semibold">NT$ {{ Number(values[i] || 0).toLocaleString() }}</div>
                        <div class="text-muted-color text-sm">{{ total ? ((Number(values[i] || 0) / total) * 100).toFixed(1) : '0.0' }}%</div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>
