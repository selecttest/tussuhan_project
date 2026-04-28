<script setup>
import { useLayout } from '@/layout/composables/layout';
import { computed, ref, watch } from 'vue';

const { layoutConfig, isDarkTheme } = useLayout();

const chartData = ref(null);
const chartOptions = ref(null);

const props = defineProps({
    payerSplit: { type: Object, default: () => ({}) }
});

const tTotal = computed(() => props.payerSplit.tTotal || 0);
const fTotal = computed(() => props.payerSplit.fTotal || 0);
const grandTotal = computed(() => tTotal.value + fTotal.value);

function setChartData() {
    return {
        labels: ['T 負擔', 'F 負擔'],
        datasets: [{
            data: [tTotal.value, fTotal.value],
            backgroundColor: ['#3B82F6', '#F59E0B'],
            hoverBackgroundColor: ['#2563EB', '#D97706'],
            borderWidth: 2,
            borderColor: 'transparent'
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
                        const pct = grandTotal.value ? ((ctx.parsed / grandTotal.value) * 100).toFixed(1) : '0.0';
                        return ` NT$ ${ctx.parsed.toLocaleString()} (${pct}%)`;
                    }
                }
            }
        },
        cutout: '62%'
    };
}

watch([() => layoutConfig.primary, () => layoutConfig.surface, isDarkTheme, () => props.payerSplit], () => {
    chartData.value = setChartData();
    chartOptions.value = setChartOptions();
}, { deep: true, immediate: true });
</script>

<template>
    <div class="card">
        <div class="flex items-center justify-between mb-4">
            <div>
                <div class="font-semibold text-xl">T / F 負擔比例</div>
                <div class="text-muted-color text-sm mt-1">本月合計 NT$ {{ grandTotal.toLocaleString() }}</div>
            </div>
        </div>

        <div class="relative">
            <Chart type="doughnut" :data="chartData" :options="chartOptions" class="h-60" />
            <div class="absolute inset-0 flex items-center justify-center pointer-events-none" style="padding-bottom:3.5rem">
                <div class="text-center">
                    <div class="text-muted-color text-xs">總支出</div>
                    <div class="font-bold text-lg">NT$ {{ grandTotal.toLocaleString() }}</div>
                </div>
            </div>
        </div>

        <div class="flex flex-col gap-3 mt-4">
            <div class="flex items-center justify-between">
                <div class="flex items-center gap-2">
                    <div class="w-2.5 h-2.5 rounded-full bg-blue-500"></div>
                    <span class="text-sm font-medium">T 負擔</span>
                </div>
                <div class="text-right">
                    <span class="font-semibold">NT$ {{ tTotal.toLocaleString() }}</span>
                    <span class="text-muted-color text-xs ml-2">
                        {{ grandTotal ? ((tTotal / grandTotal) * 100).toFixed(1) : '0.0' }}%
                    </span>
                </div>
            </div>
            <div class="flex items-center justify-between">
                <div class="flex items-center gap-2">
                    <div class="w-2.5 h-2.5 rounded-full" style="background:#F59E0B"></div>
                    <span class="text-sm font-medium">F 負擔</span>
                </div>
                <div class="text-right">
                    <span class="font-semibold">NT$ {{ fTotal.toLocaleString() }}</span>
                    <span class="text-muted-color text-xs ml-2">
                        {{ grandTotal ? ((fTotal / grandTotal) * 100).toFixed(1) : '0.0' }}%
                    </span>
                </div>
            </div>
        </div>
    </div>
</template>
