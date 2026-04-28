<script setup>
import DashboardLoading from '@/components/bot/DashboardLoading.vue';
import { fetchAllExpenseRecords, fetchExpenseRecords } from '@/service/DashboardApi';
import { computed, onMounted, reactive, ref } from 'vue';
import { useRouter } from 'vue-router';

const ALL = '__all__';

const router = useRouter();
const loading = ref(false);
const error = ref('');
const selectedMonth = ref(ALL);
const selectedTypes = ref([]);
const availableMonths = ref([]);
const allRecords = ref([]);
const filteredRecords = ref([]);
const monthTotal = ref(0);
const lastUpdatedAt = ref('');
const showColPanel = ref(false);

/* 欄位可見度：日期固定顯示，其餘可切換 */
const colVisible = reactive({
    type:   true,
    detail: true,
    amount: true,
    payer:  true,
    tf:     true,
});

const COL_LABELS = {
    type:   '分類',
    detail: '品項',
    amount: '金額',
    payer:  '付款',
    tf:     'T / F',
};

/* RWD 預設：小螢幕隱藏 payer 和 T/F */
function applyRwdDefaults() {
    if (window.innerWidth < 640) {
        colVisible.payer = false;
        colVisible.tf    = false;
    }
}

const TYPE_SEVERITY = {
    Food:    'info',
    Baby:    'warning',
    Drink:   'success',
    Tuition: 'help',
    Other:   'secondary',
};
const PAYER_SEVERITY = { T: 'info', F: 'warn' };

/* 從已載入的紀錄取得所有分類選項 */
const typeOptions = computed(() => {
    const set = new Set(allRecords.value.map((r) => r.type).filter(Boolean));
    return [...set].sort().map((t) => ({ label: t, value: t }));
});

const monthOptions = computed(() => [
    { label: '全部紀錄', value: ALL },
    ...availableMonths.value.map((m) => ({ label: m, value: m })),
]);

const displayMonth = computed(() =>
    selectedMonth.value === ALL ? '全部紀錄' : selectedMonth.value
);

/* 套用分類篩選後再排序 */
const displayRecords = computed(() => {
    let rows = filteredRecords.value;
    if (selectedTypes.value.length) {
        rows = rows.filter((r) => selectedTypes.value.includes(r.type));
    }
    return [...rows].sort((a, b) => (b.date || '').localeCompare(a.date || ''));
});

/* 顯示合計只算篩選後的結果 */
const displayTotal = computed(() =>
    displayRecords.value.reduce((s, r) => s + Number(r.amount || 0), 0)
);

/* ── 資料載入 ── */
async function loadAll() {
    loading.value = true;
    error.value = '';
    try {
        const data = await fetchAllExpenseRecords();
        allRecords.value     = data.records || [];
        availableMonths.value = data.availableMonths || [];
        filteredRecords.value = allRecords.value;
        monthTotal.value      = data.total || 0;
        lastUpdatedAt.value   = new Date().toLocaleString('zh-TW');
    } catch (err) {
        error.value = err instanceof Error ? err.message : '無法載入資料';
    } finally {
        loading.value = false;
    }
}

async function loadMonth(month) {
    loading.value = true;
    error.value = '';
    try {
        const data = await fetchExpenseRecords(month);
        filteredRecords.value = data.records || [];
        monthTotal.value      = data.total || 0;
        if (data.availableMonths?.length) availableMonths.value = data.availableMonths;
        lastUpdatedAt.value = new Date().toLocaleString('zh-TW');
    } catch (err) {
        error.value = err instanceof Error ? err.message : '無法載入資料';
    } finally {
        loading.value = false;
    }
}

function handleMonthChange(val) {
    selectedMonth.value = val;
    selectedTypes.value = [];
    if (val === ALL) loadAll();
    else loadMonth(val);
}

function clearFilters() {
    selectedTypes.value = [];
}

onMounted(() => {
    applyRwdDefaults();
    loadAll();
});
</script>

<template>
    <div class="flex flex-col gap-6">
        <Transition name="fade">
            <DashboardLoading
                v-if="loading"
                :message="allRecords.length ? '重新整理資料中...' : '正在載入資料...'"
            />
        </Transition>

        <!-- 頁首 -->
        <div class="flex items-center justify-between flex-wrap gap-3">
            <div class="flex items-center gap-3">
                <Button icon="pi pi-arrow-left" text rounded size="small" @click="router.back()" />
                <div>
                    <h1 class="text-2xl font-bold text-surface-900 dark:text-surface-0">支出紀錄明細</h1>
                    <p class="text-muted-color mt-1">{{ displayMonth }}</p>
                </div>
            </div>
            <div class="flex items-center gap-3 text-sm">
                <span v-if="lastUpdatedAt" class="text-muted-color hidden sm:inline">最後同步：{{ lastUpdatedAt }}</span>
                <Button label="重新整理" icon="pi pi-sync" size="small" :loading="loading" @click="handleMonthChange(selectedMonth)" />
            </div>
        </div>

        <Message v-if="error" severity="error" :closable="false">{{ error }}</Message>

        <div class="card">
            <!-- ── 工具列：月份 / 篩選 / 欄位 ── -->
            <div class="flex flex-col gap-3 mb-4">

                <!-- 第一行：標題 + 月份選擇 -->
                <div class="flex items-center justify-between flex-wrap gap-3">
                    <div>
                        <div class="font-semibold text-xl">支出紀錄</div>
                        <div class="text-muted-color text-sm mt-1">
                            合計 NT$ {{ displayTotal.toLocaleString() }}
                            <span class="ml-2 text-xs">（共 {{ displayRecords.length }} 筆）</span>
                            <Tag
                                v-if="selectedTypes.length"
                                :value="`已篩選 ${selectedTypes.length} 種分類`"
                                severity="warn"
                                class="ml-2 text-xs cursor-pointer"
                                @click="clearFilters"
                            />
                        </div>
                    </div>
                    <Select
                        :model-value="selectedMonth"
                        :options="monthOptions"
                        option-label="label"
                        option-value="value"
                        placeholder="選擇月份"
                        class="w-44"
                        @update:model-value="handleMonthChange"
                    />
                </div>

                <!-- 第二行：篩選器 + 欄位顯示按鈕 -->
                <div class="flex items-center flex-wrap gap-2">
                    <!-- 分類多選 -->
                    <MultiSelect
                        v-model="selectedTypes"
                        :options="typeOptions"
                        option-label="label"
                        option-value="value"
                        placeholder="篩選分類"
                        display="chip"
                        class="flex-1 min-w-[180px] max-w-xs"
                        :show-toggle-all="false"
                    >
                        <template #option="{ option }">
                            <Tag :value="option.label" :severity="TYPE_SEVERITY[option.label] || 'secondary'" />
                        </template>
                    </MultiSelect>

                    <Button
                        v-if="selectedTypes.length"
                        icon="pi pi-times"
                        text
                        size="small"
                        severity="secondary"
                        @click="clearFilters"
                    />

                    <div class="ml-auto relative">
                        <Button
                            icon="pi pi-table"
                            text
                            size="small"
                            severity="secondary"
                            v-tooltip.bottom="'顯示欄位'"
                            @click="showColPanel = !showColPanel"
                        />
                        <!-- 欄位選擇浮層 -->
                        <div
                            v-if="showColPanel"
                            class="absolute right-0 top-full mt-1 z-10 bg-surface-0 dark:bg-surface-800 border border-surface-200 dark:border-surface-700 rounded-xl shadow-lg p-3 min-w-[160px]"
                        >
                            <div class="text-xs font-semibold text-muted-color mb-2 px-1">顯示欄位</div>
                            <div
                                v-for="(label, key) in COL_LABELS"
                                :key="key"
                                class="flex items-center gap-2 py-1 px-1 rounded hover:bg-surface-100 dark:hover:bg-surface-700"
                            >
                                <Checkbox v-model="colVisible[key]" :binary="true" :input-id="`col-${key}`" @click.stop />
                                <label :for="`col-${key}`" class="text-sm cursor-pointer select-none" @click.stop="colVisible[key] = !colVisible[key]">{{ label }}</label>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- ── 資料表 ── -->
            <DataTable
                :value="displayRecords"
                :rows="50"
                :paginator="displayRecords.length > 50"
                paginator-template="FirstPageLink PrevPageLink PageLinks NextPageLink LastPageLink RowsPerPageDropdown"
                :rows-per-page-options="[25, 50, 100]"
                responsive-layout="scroll"
                striped-rows
                :loading="loading"
                @click.stop
            >
                <!-- 日期（固定顯示） -->
                <Column field="date" header="日期" style="width:120px" :sortable="true">
                    <template #body="{ data }">
                        <span class="text-muted-color text-sm">{{ data.date }}</span>
                    </template>
                </Column>

                <Column v-if="colVisible.type" field="type" header="分類" style="width:90px">
                    <template #body="{ data }">
                        <Tag :value="data.type" :severity="TYPE_SEVERITY[data.type] || 'secondary'" />
                    </template>
                </Column>

                <Column v-if="colVisible.detail" field="detail" header="品項" style="width:160px;min-width:120px">
                    <template #body="{ data }">
                        <span class="font-medium">{{ data.detail }}</span>
                    </template>
                </Column>

                <Column v-if="colVisible.amount" field="amount" header="金額" style="width:120px" :sortable="true">
                    <template #body="{ data }">
                        <span class="font-semibold text-red-500 dark:text-red-400">
                            NT$ {{ data.amount.toLocaleString() }}
                        </span>
                    </template>
                </Column>

                <Column v-if="colVisible.payer" field="payer" header="付款" style="width:70px">
                    <template #body="{ data }">
                        <Tag :value="data.payer" :severity="PAYER_SEVERITY[data.payer] || 'secondary'" />
                    </template>
                </Column>

                <Column v-if="colVisible.tf" header="T / F" style="width:160px">
                    <template #body="{ data }">
                        <div class="flex gap-2 text-sm">
                            <span class="text-blue-500">T ${{ data.tPaid.toLocaleString() }}</span>
                            <span class="text-muted-color">/</span>
                            <span class="text-amber-500">F ${{ data.fPaid.toLocaleString() }}</span>
                        </div>
                    </template>
                </Column>
            </DataTable>
        </div>
    </div>

    <!-- 點擊浮層外部關閉欄位面板 -->
    <div v-if="showColPanel" class="fixed inset-0 z-[5]" @click="showColPanel = false" />
</template>
