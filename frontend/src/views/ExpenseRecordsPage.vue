<script setup>
import DashboardLoading from '@/components/bot/DashboardLoading.vue';
import { deleteExpenseRow, fetchAllExpenseRecords, fetchExpenseRecords, updateExpenseRow } from '@/service/DashboardApi';
import { computed, onMounted, reactive, ref } from 'vue';
import { useRouter } from 'vue-router';
import { useToast } from 'primevue/usetoast';

const ALL = '__all__';

const router = useRouter();
const toast = useToast();
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
/** 後端 expense API：demo | google_sheets */
const dataSource = ref('');

const EDIT_TYPE_OPTIONS = ['food', 'baby', 'drink', 'tuition', 'other', 'insurance'];
const PAYER_SELECT_OPTIONS = [
    { label: 'T', value: 'T' },
    { label: 'F', value: 'F' },
];

const editDialogVisible = ref(false);
const editSaving = ref(false);
const editSheetRow = ref(null);
const editForm = reactive({
    date: '',
    type: 'food',
    detail: '',
    amount: 0,
    payer: 'T',
    tPaid: 0,
    fPaid: 0,
});

const deleteDialogVisible = ref(false);
const deleteTarget = ref(null);
const deleteLoading = ref(false);

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

/* 馬卡龍色系：每種分類使用明顯可區分的柔和色 */
const TYPE_CLASS = {
    food:      'bg-orange-100 text-orange-700 dark:bg-orange-900/60 dark:text-orange-300',
    baby:      'bg-pink-100 text-pink-700 dark:bg-pink-900/60 dark:text-pink-300',
    drink:     'bg-teal-100 text-teal-700 dark:bg-teal-900/60 dark:text-teal-300',
    tuition:   'bg-violet-100 text-violet-700 dark:bg-violet-900/60 dark:text-violet-300',
    other:     'bg-slate-100 text-slate-600 dark:bg-slate-700/60 dark:text-slate-300',
    insurance: 'bg-blue-100 text-blue-700 dark:bg-blue-900/60 dark:text-blue-300',
};

function typeClass(type) {
    return TYPE_CLASS[normalizeType(type)] ?? 'bg-gray-100 text-gray-600 dark:bg-gray-700/60 dark:text-gray-300';
}
const PAYER_SEVERITY = { T: 'info', F: 'warn' };

function normalizeType(type) {
    const t = String(type || '').trim().toLowerCase();
    return ['food', 'drink', 'baby', 'tuition', 'insurance', 'other'].includes(t) ? t : 'other';
}

function normalizeRecord(row) {
    return { ...row, type: normalizeType(row?.type) };
}

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

function rowEditable(row) {
    const n = Number(row.sheetRow);
    return row.sheetRow != null && Number.isFinite(n) && n >= 2;
}

function openEdit(row) {
    if (!rowEditable(row)) return;
    editSheetRow.value = row.sheetRow;
    editForm.date = row.date ?? '';
    editForm.type = normalizeType(row.type);
    editForm.detail = row.detail ?? '';
    editForm.amount = Number(row.amount || 0);
    editForm.payer = row.payer === 'F' ? 'F' : 'T';
    editForm.tPaid = Number(row.tPaid ?? row.t_paid ?? 0);
    editForm.fPaid = Number(row.fPaid ?? row.f_paid ?? 0);
    editDialogVisible.value = true;
}

async function saveEdit() {
    if (editForm.tPaid + editForm.fPaid !== editForm.amount) {
        toast.add({
            severity: 'warn',
            summary: '無法儲存',
            detail: 'T 付 + F 付 必須等於金額',
            life: 4000,
        });
        return;
    }
    editSaving.value = true;
    try {
        await updateExpenseRow(editSheetRow.value, {
            date: editForm.date,
            type: editForm.type,
            detail: editForm.detail,
            amount: editForm.amount,
            payer: editForm.payer,
            tPaid: editForm.tPaid,
            fPaid: editForm.fPaid,
        });
        toast.add({ severity: 'success', summary: '已更新', life: 2500 });
        editDialogVisible.value = false;
        await handleMonthChange(selectedMonth.value);
    } catch (err) {
        toast.add({
            severity: 'error',
            summary: '更新失敗',
            detail: err instanceof Error ? err.message : '請稍後再試',
            life: 5000,
        });
    } finally {
        editSaving.value = false;
    }
}

function askDelete(row) {
    if (!rowEditable(row)) return;
    deleteTarget.value = row;
    deleteDialogVisible.value = true;
}

async function confirmDelete() {
    const row = deleteTarget.value;
    if (!row?.sheetRow) return;
    deleteLoading.value = true;
    try {
        await deleteExpenseRow(row.sheetRow);
        toast.add({ severity: 'success', summary: '已刪除', life: 2500 });
        deleteDialogVisible.value = false;
        deleteTarget.value = null;
        await handleMonthChange(selectedMonth.value);
    } catch (err) {
        toast.add({
            severity: 'error',
            summary: '刪除失敗',
            detail: err instanceof Error ? err.message : '請稍後再試',
            life: 5000,
        });
    } finally {
        deleteLoading.value = false;
    }
}

/* ── 資料載入 ── */
async function loadAll() {
    loading.value = true;
    error.value = '';
    try {
        const data = await fetchAllExpenseRecords();
        allRecords.value     = (data.records || []).map(normalizeRecord);
        availableMonths.value = data.availableMonths || [];
        filteredRecords.value = allRecords.value;
        monthTotal.value      = data.total || 0;
        dataSource.value      = data.dataSource || '';
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
        filteredRecords.value = (data.records || []).map(normalizeRecord);
        monthTotal.value      = data.total || 0;
        dataSource.value     = data.dataSource || '';
        if (data.availableMonths?.length) availableMonths.value = data.availableMonths;
        lastUpdatedAt.value = new Date().toLocaleString('zh-TW');
    } catch (err) {
        error.value = err instanceof Error ? err.message : '無法載入資料';
    } finally {
        loading.value = false;
    }
}

async function handleMonthChange(val) {
    selectedMonth.value = val;
    selectedTypes.value = [];
    if (val === ALL) await loadAll();
    else await loadMonth(val);
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

        <Message
            v-if="displayRecords.length && dataSource === 'demo'"
            severity="info"
            :closable="false"
            class="text-sm"
        >
            目前後端使用<strong>示範資料</strong>（未讀取 Google Sheets），此頁無法編輯或刪除。請設定
            <code class="text-xs bg-surface-100 dark:bg-surface-800 px-1 rounded">GOOGLE_SHEETS_ID</code>、
            <code class="text-xs bg-surface-100 dark:bg-surface-800 px-1 rounded">GOOGLE_CREDENTIALS_PATH</code>
            並重啟後端，再按「重新整理」。
        </Message>

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
                            <span :class="['inline-flex items-center px-2 py-0.5 rounded-full text-xs font-semibold', typeClass(option.label)]">
                                {{ option.label }}
                            </span>
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
                        <span :class="['inline-flex items-center px-2 py-0.5 rounded-full text-xs font-semibold', typeClass(data.type)]">
                            {{ data.type }}
                        </span>
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

                <Column header="操作" style="width:104px" :exportable="false">
                    <template #body="{ data }">
                        <div class="flex gap-0.5">
                            <Button
                                icon="pi pi-pencil"
                                rounded
                                text
                                size="small"
                                :disabled="!rowEditable(data)"
                                v-tooltip.top="'編輯'"
                                @click="openEdit(data)"
                            />
                            <Button
                                icon="pi pi-trash"
                                rounded
                                text
                                size="small"
                                severity="danger"
                                :disabled="!rowEditable(data)"
                                v-tooltip.top="'刪除'"
                                @click="askDelete(data)"
                            />
                        </div>
                    </template>
                </Column>
            </DataTable>
        </div>
    </div>

    <Dialog
        v-model:visible="editDialogVisible"
        header="編輯支出"
        :modal="true"
        :style="{ width: 'min(440px, 96vw)' }"
        :dismissable-mask="true"
    >
        <div class="flex flex-col gap-3 pt-2">
            <div>
                <label for="edit-date" class="text-sm text-muted-color block mb-1">日期</label>
                <InputText id="edit-date" v-model="editForm.date" class="w-full" placeholder="例：2026/4/7" />
            </div>
            <div>
                <label for="edit-type" class="text-sm text-muted-color block mb-1">分類</label>
                <Select
                    id="edit-type"
                    v-model="editForm.type"
                    :options="EDIT_TYPE_OPTIONS"
                    class="w-full"
                    placeholder="選擇分類"
                />
            </div>
            <div>
                <label for="edit-detail" class="text-sm text-muted-color block mb-1">品項</label>
                <InputText id="edit-detail" v-model="editForm.detail" class="w-full" />
            </div>
            <div>
                <label for="edit-amount" class="text-sm text-muted-color block mb-1">總金額</label>
                <InputNumber
                    id="edit-amount"
                    v-model="editForm.amount"
                    class="w-full"
                    :min="0"
                    fluid
                    :use-grouping="true"
                />
            </div>
            <div>
                <label for="edit-payer" class="text-sm text-muted-color block mb-1">結帳（付款人）</label>
                <Select
                    id="edit-payer"
                    v-model="editForm.payer"
                    :options="PAYER_SELECT_OPTIONS"
                    option-label="label"
                    option-value="value"
                    class="w-full"
                />
            </div>
            <div class="grid grid-cols-2 gap-3">
                <div>
                    <label for="edit-tpaid" class="text-sm text-muted-color block mb-1">T 付</label>
                    <InputNumber
                        id="edit-tpaid"
                        v-model="editForm.tPaid"
                        class="w-full"
                        :min="0"
                        fluid
                        :use-grouping="true"
                    />
                </div>
                <div>
                    <label for="edit-fpaid" class="text-sm text-muted-color block mb-1">F 付</label>
                    <InputNumber
                        id="edit-fpaid"
                        v-model="editForm.fPaid"
                        class="w-full"
                        :min="0"
                        fluid
                        :use-grouping="true"
                    />
                </div>
            </div>
            <p class="text-xs text-muted-color m-0">T 付 + F 付 必須等於總金額；儲存後會寫回 Google 試算表同一列。</p>
        </div>
        <template #footer>
            <Button label="取消" text @click="editDialogVisible = false" />
            <Button label="儲存" icon="pi pi-check" :loading="editSaving" @click="saveEdit" />
        </template>
    </Dialog>

    <Dialog
        v-model:visible="deleteDialogVisible"
        header="確認刪除"
        :modal="true"
        :style="{ width: 'min(400px, 96vw)' }"
        :dismissable-mask="true"
    >
        <p v-if="deleteTarget" class="m-0 leading-relaxed">
            刪除「<strong>{{ deleteTarget.detail }}</strong>」NT$
            {{ Number(deleteTarget.amount).toLocaleString() }}？<br />
            將從 Google 試算表刪除該列，請以「重新整理」確認列表。
        </p>
        <template #footer>
            <Button label="取消" text @click="deleteDialogVisible = false" />
            <Button label="刪除" icon="pi pi-trash" severity="danger" :loading="deleteLoading" @click="confirmDelete" />
        </template>
    </Dialog>

    <!-- 點擊浮層外部關閉欄位面板 -->
    <div v-if="showColPanel" class="fixed inset-0 z-[5]" @click="showColPanel = false" />
</template>
