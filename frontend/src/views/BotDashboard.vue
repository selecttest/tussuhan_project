<script setup>
import AllocationBarWidget from '@/components/bot/AllocationBarWidget.vue';
import DashboardLoading from '@/components/bot/DashboardLoading.vue';
import IncomeStatsWidget from '@/components/bot/IncomeStatsWidget.vue';
import IncomeTableWidget from '@/components/bot/IncomeTableWidget.vue';
import RevenueDonutWidget from '@/components/bot/RevenueDonutWidget.vue';
import SubscriptionDonutWidget from '@/components/bot/SubscriptionDonutWidget.vue';
import TrendLineWidget from '@/components/bot/TrendLineWidget.vue';
import { fetchDashboardData } from '@/service/DashboardApi';
import { computed, onMounted, ref } from 'vue';
import { useRouter } from 'vue-router';

const router = useRouter();

const dashboard = ref(null);
const loading = ref(false);
const error = ref('');
const selectedMonth = ref('');
const lastUpdatedAt = ref('');

function normalizeType(type) {
    const t = String(type || '').trim().toLowerCase();
    return ['food', 'drink', 'baby', 'tuition', 'insurance', 'other'].includes(t) ? t : 'other';
}

function normalizeDashboardData(raw) {
    const cloned = { ...(raw || {}) };
    const expenseRecords = (cloned.expense?.records || []).map((r) => ({ ...r, type: normalizeType(r.type) }));
    const typeItems = (cloned.typeBreakdown?.items || []).map((i) => ({ ...i, label: normalizeType(i.label) }));
    const typeLabels = (cloned.typeBreakdown?.chart?.labels || []).map(normalizeType);
    const byType = (cloned.payerSplit?.byType || []).map((i) => ({ ...i, type: normalizeType(i.type) }));
    return {
        ...cloned,
        expense: { ...(cloned.expense || {}), records: expenseRecords },
        typeBreakdown: {
            ...(cloned.typeBreakdown || {}),
            items: typeItems,
            chart: { ...(cloned.typeBreakdown?.chart || {}), labels: typeLabels },
        },
        payerSplit: { ...(cloned.payerSplit || {}), byType },
    };
}

const stats = computed(() => dashboard.value?.stats || {});
const typeBreakdown = computed(() => dashboard.value?.typeBreakdown || {});
const trend = computed(() => dashboard.value?.trend || {});
const payerSplit = computed(() => dashboard.value?.payerSplit || {});
const expense = computed(() => dashboard.value?.expense || {});
const displayMonth = computed(() => stats.value.month || selectedMonth.value || '最新月份');

async function loadDashboard(month = selectedMonth.value) {
    loading.value = true;
    error.value = '';
    try {
        dashboard.value = normalizeDashboardData(await fetchDashboardData(month));
        selectedMonth.value = dashboard.value?.stats?.month || month || '';
        lastUpdatedAt.value = new Date().toLocaleString('zh-TW');
    } catch (err) {
        error.value = err instanceof Error ? err.message : '無法載入資料';
    } finally {
        loading.value = false;
    }
}

function handleMonthChange(month) {
    selectedMonth.value = month;
    loadDashboard(month);
}

onMounted(() => loadDashboard());
</script>

<template>
    <div class="flex flex-col gap-6">
        <!-- 頁首 -->
        <div class="flex items-center justify-between flex-wrap gap-3">
            <div>
                <h1 class="text-2xl font-bold text-surface-900 dark:text-surface-0">支出記帳 Dashboard</h1>
                <p class="text-muted-color mt-1">Google Sheets 真實數據 · {{ displayMonth }}</p>
            </div>
            <div class="flex items-center gap-3 text-sm">
                <span v-if="lastUpdatedAt" class="text-muted-color">最後同步：{{ lastUpdatedAt }}</span>
                <Button label="重新整理" icon="pi pi-sync" size="small" :loading="loading" @click="loadDashboard()" />
            </div>
        </div>

        <Message v-if="error" severity="error" :closable="false">{{ error }}</Message>

        <!-- Loading：顯示在頁首下方、內容區中間 -->
        <Transition name="fade">
            <DashboardLoading
                v-if="loading"
                :message="dashboard ? '重新整理資料中...' : '正在從 Google Sheets 載入資料...'"
            />
        </Transition>

        <template v-if="dashboard">
            <!-- 4 張統計卡片 -->
            <div class="grid grid-cols-12 gap-6">
                <IncomeStatsWidget
                    :total-expense="stats.totalExpense || 0"
                    :t-total="stats.tTotal || 0"
                    :f-total="stats.fTotal || 0"
                    :today-expense="stats.todayExpense || 0"
                />
            </div>

            <!-- 分類圓餅圖 + T/F 分類橫條圖 -->
            <div class="grid grid-cols-12 gap-6">
                <div class="col-span-12 xl:col-span-5">
                    <RevenueDonutWidget :type-breakdown="typeBreakdown" />
                </div>
                <div class="col-span-12 xl:col-span-7">
                    <AllocationBarWidget :payer-split="payerSplit" />
                </div>
            </div>

            <!-- 月度趨勢折線圖 -->
            <div class="grid grid-cols-12 gap-6">
                <div class="col-span-12">
                    <TrendLineWidget :trend="trend" />
                </div>
            </div>

            <!-- T/F 比例圓餅 + 支出紀錄表格 -->
            <div class="flex items-center justify-between">
                <span class="text-muted-color text-sm font-medium">T / F 負擔比例 · 支出紀錄</span>
                <Button
                    label="查看完整紀錄"
                    icon="pi pi-arrow-right"
                    icon-pos="right"
                    size="small"
                    text
                    @click="router.push('/bot/expense-records')"
                />
            </div>
            <div class="grid grid-cols-12 gap-6">
                <div class="col-span-12 xl:col-span-4">
                    <SubscriptionDonutWidget :payer-split="payerSplit" />
                </div>
                <div class="col-span-12 xl:col-span-8">
                    <IncomeTableWidget
                        :month="selectedMonth"
                        :available-months="expense.availableMonths || []"
                        :records="expense.records || []"
                        :total="expense.total || 0"
                        @update:month="handleMonthChange"
                    />
                </div>
            </div>
        </template>
    </div>
</template>
