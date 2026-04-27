<script setup>
import AllocationBarWidget from '@/components/bot/AllocationBarWidget.vue';
import IncomeStatsWidget from '@/components/bot/IncomeStatsWidget.vue';
import IncomeTableWidget from '@/components/bot/IncomeTableWidget.vue';
import RevenueDonutWidget from '@/components/bot/RevenueDonutWidget.vue';
import SubscriptionDonutWidget from '@/components/bot/SubscriptionDonutWidget.vue';
import TrendLineWidget from '@/components/bot/TrendLineWidget.vue';
import { fetchDashboardData } from '@/service/DashboardApi';
import { computed, onMounted, ref } from 'vue';

const dashboard = ref(null);
const loading = ref(false);
const error = ref('');
const selectedMonth = ref('');
const lastUpdatedAt = ref('');

const stats = computed(() => dashboard.value?.stats || {});
const income = computed(() => dashboard.value?.income || {});
const revenue = computed(() => dashboard.value?.revenue || {});
const allocation = computed(() => dashboard.value?.allocation || {});
const trend = computed(() => dashboard.value?.trend || {});
const subscriptions = computed(() => dashboard.value?.subscriptions || {});
const displayMonth = computed(() => stats.value.month || selectedMonth.value || '最新月份');

async function loadDashboard(month = selectedMonth.value) {
    loading.value = true;
    error.value = '';

    try {
        dashboard.value = await fetchDashboardData(month);
        selectedMonth.value = dashboard.value?.stats?.month || dashboard.value?.income?.month || month || '';
        lastUpdatedAt.value = new Date().toLocaleString('zh-TW');
    } catch (err) {
        error.value = err instanceof Error ? err.message : '無法載入 Google Sheets 資料';
    } finally {
        loading.value = false;
    }
}

function handleMonthChange(month) {
    selectedMonth.value = month;
    loadDashboard(month);
}

onMounted(() => {
    loadDashboard();
});
</script>

<template>
    <div class="flex flex-col gap-6">
        <!-- 頁首 -->
        <div class="flex items-center justify-between">
            <div>
                <h1 class="text-2xl font-bold text-surface-900 dark:text-surface-0">收入理財 Dashboard</h1>
                <p class="text-muted-color mt-1">Google Sheets 真實數據 · {{ displayMonth }}</p>
            </div>
            <div class="flex items-center gap-3 text-sm">
                <span v-if="lastUpdatedAt" class="text-muted-color">最後同步：{{ lastUpdatedAt }}</span>
                <Button label="重新整理" icon="pi pi-sync" size="small" :loading="loading" @click="loadDashboard()" />
            </div>
        </div>

        <Message v-if="error" severity="error" :closable="false">{{ error }}</Message>
        <Message v-else-if="loading && !dashboard" severity="info" :closable="false">正在載入 Google Sheets 資料...</Message>

        <template v-if="dashboard">
            <!-- 統計卡片 -->
            <div class="grid grid-cols-12 gap-6">
                <IncomeStatsWidget
                    :total-income="stats.totalIncome || 0"
                    :total-expense="stats.totalExpense || 0"
                    :net-income="stats.netIncome || 0"
                    :total-subscription="stats.totalSubscription || 0"
                    :subscription-count="stats.subscriptionCount || 0"
                />
            </div>

            <!-- 營收環形圖 + 財務分配長條圖 -->
            <div class="grid grid-cols-12 gap-6">
                <div class="col-span-12 xl:col-span-5">
                    <RevenueDonutWidget :revenue="revenue" />
                </div>
                <div class="col-span-12 xl:col-span-7">
                    <AllocationBarWidget :allocation="allocation" />
                </div>
            </div>

            <!-- 月度趨勢折線圖 -->
            <div class="grid grid-cols-12 gap-6">
                <div class="col-span-12">
                    <TrendLineWidget :trend="trend" />
                </div>
            </div>

            <!-- 訂閱費用 + 收入紀錄表格 -->
            <div class="grid grid-cols-12 gap-6">
                <div class="col-span-12 xl:col-span-4">
                    <SubscriptionDonutWidget :subscriptions="subscriptions" />
                </div>
                <div class="col-span-12 xl:col-span-8">
                    <IncomeTableWidget
                        :month="selectedMonth"
                        :available-months="income.availableMonths || []"
                        :records="income.records || []"
                        :total="income.total || 0"
                        @update:month="handleMonthChange"
                    />
                </div>
            </div>
        </template>
    </div>
</template>
