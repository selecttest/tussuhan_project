<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';

const router = useRouter();
const showNotes = ref(true);
const SHEET_URL = 'https://docs.google.com/spreadsheets/d/104yNlgh-PwPoQXqBUDIVAehjn-qOQXx7b8Dhgqy0RzY/edit?usp=sharing';

const COMMANDS = [
    {
        group: '記帳',
        icon: 'pi pi-pencil',
        color: 'text-blue-500',
        bg: 'bg-blue-50 dark:bg-blue-950',
        border: 'border-blue-200 dark:border-blue-800',
        items: [
            {
                syntax: '記 [類別] [品項] [金額]',
                example: '記 餐費 拉亞+M 415',
                desc: 'T 付全額。Payer = T，T_paid = 415，F_paid = 0',
            },
            {
                syntax: '記F [類別] [品項] [金額]',
                example: '記F 飲料 coco 99',
                desc: 'F 付全額。Payer = F，T_paid = 0，F_paid = 99',
            },
            {
                syntax: '記 [類別] [品項] [金額] 分[F負擔金額]',
                example: '記 餐費 早餐+便當 590 分215',
                desc: 'T 結帳，F 負擔 215。T_paid = 375，F_paid = 215',
            },
            {
                syntax: '記F [類別] [品項] [金額] 分[T負擔金額]',
                example: '記F 餐費 聚餐 600 分300',
                desc: 'F 結帳，T 負擔 300。T_paid = 300，F_paid = 300',
            },
        ],
    },
    {
        group: '查詢',
        icon: 'pi pi-search',
        color: 'text-green-500',
        bg: 'bg-green-50 dark:bg-green-950',
        border: 'border-green-200 dark:border-green-800',
        items: [
            {
                syntax: '查',
                example: '查',
                desc: '查詢當月支出摘要（T / F 合計）',
            },
            {
                syntax: '查 [YYYY-MM]',
                example: '查 2026-04',
                desc: '查詢指定月份支出摘要',
            },
            {
                syntax: '今日',
                example: '今日',
                desc: '查詢今日所有支出明細（最多顯示 5 筆）',
            },
            {
                syntax: '本月',
                example: '本月',
                desc: '查詢本月支出摘要，等同於「查」',
            },
            {
                syntax: 'help / 說明 / 幫助',
                example: 'help',
                desc: '顯示可用指令列表',
            },
        ],
    },
];

const TYPE_CLASS = {
    Food:      'bg-orange-100 text-orange-700 dark:bg-orange-900/60 dark:text-orange-300',
    Baby:      'bg-pink-100 text-pink-700 dark:bg-pink-900/60 dark:text-pink-300',
    Drink:     'bg-teal-100 text-teal-700 dark:bg-teal-900/60 dark:text-teal-300',
    Tuition:   'bg-violet-100 text-violet-700 dark:bg-violet-900/60 dark:text-violet-300',
    Other:     'bg-slate-100 text-slate-600 dark:bg-slate-700/60 dark:text-slate-300',
    Insurance: 'bg-blue-100 text-blue-700 dark:bg-blue-900/60 dark:text-blue-300',
};

const CATEGORIES = [
    { alias: '餐費 / 食物 / 早餐 / 午餐 / 晚餐', type: 'Food' },
    { alias: '飲料 / 喝', type: 'Drink' },
    { alias: '寶寶 / 嬰兒 / 育兒', type: 'Baby' },
    { alias: '學費 / 補習', type: 'Tuition' },
    { alias: '其他（或直接輸入英文分類）', type: 'Other' },
];
</script>

<template>
    <div class="flex flex-col gap-6">

        <!-- 頁首 -->
        <div class="flex items-center justify-between flex-wrap gap-3">
            <div class="flex items-center gap-3">
                <Button icon="pi pi-arrow-left" text rounded size="small" @click="router.back()" />
                <div>
                    <h1 class="text-2xl font-bold text-surface-900 dark:text-surface-0">LINE Bot 指令說明</h1>
                    <p class="text-muted-color mt-1">記帳 · 查詢 · 分類對照</p>
                </div>
            </div>
            <div class="flex items-center gap-2">
                <!-- 注意事項 icon button -->
                <Button
                    icon="pi pi-exclamation-circle"
                    text
                    rounded
                    severity="warn"
                    v-tooltip.bottom="'注意事項'"
                    @click="showNotes = !showNotes"
                />
                <!-- Google Sheets 連結 -->
                <a :href="SHEET_URL" target="_blank" rel="noopener noreferrer">
                    <Button icon="pi pi-table" label="原始資料表" size="small" severity="secondary" outlined />
                </a>
            </div>
        </div>

        <!-- 注意事項展開面板 -->
        <Transition name="fade">
            <div v-if="showNotes" class="card border-l-4 border-amber-400 dark:border-amber-500 bg-amber-50 dark:bg-amber-950">
                <div class="flex items-center justify-between mb-3">
                    <div class="flex items-center gap-2">
                        <i class="pi pi-exclamation-circle text-amber-500" />
                        <span class="font-semibold text-surface-900 dark:text-surface-0">注意事項</span>
                    </div>
                    <Button icon="pi pi-times" text rounded size="small" severity="secondary" @click="showNotes = false" />
                </div>
                <ul class="flex flex-col gap-2 text-sm text-surface-700 dark:text-surface-300 list-none">
                    <li class="flex items-start gap-2"><i class="pi pi-check-circle text-green-500 mt-0.5 flex-shrink-0" />每個欄位以「空白」分隔，品項可使用 <code class="font-mono bg-surface-100 dark:bg-surface-700 px-1 rounded">+</code> 連接多個品名。</li>
                    <li class="flex items-start gap-2"><i class="pi pi-check-circle text-green-500 mt-0.5 flex-shrink-0" />金額只接受正整數，不含小數點。</li>
                    <li class="flex items-start gap-2"><i class="pi pi-check-circle text-green-500 mt-0.5 flex-shrink-0" />記帳日期自動為「今日」，無法手動指定。</li>
                    <li class="flex items-start gap-2"><i class="pi pi-check-circle text-green-500 mt-0.5 flex-shrink-0" />分帳金額不可大於總金額。</li>
                    <li class="flex items-start gap-2"><i class="pi pi-check-circle text-green-500 mt-0.5 flex-shrink-0" />輸入錯誤格式時，Bot 會回覆錯誤說明。</li>
                </ul>
            </div>
        </Transition>

        <!-- 指令區塊 -->
        <div v-for="group in COMMANDS" :key="group.group" class="card">
            <div class="flex items-center gap-2 mb-4">
                <div :class="['flex items-center justify-center w-8 h-8 rounded-lg', group.bg]">
                    <i :class="[group.icon, group.color, 'text-sm']" />
                </div>
                <span class="font-semibold text-lg text-surface-900 dark:text-surface-0">{{ group.group }}指令</span>
            </div>

            <div class="flex flex-col gap-3">
                <div
                    v-for="(cmd, i) in group.items"
                    :key="i"
                    :class="['rounded-xl border p-4', group.border, group.bg]"
                >
                    <!-- 語法 -->
                    <div class="flex items-start justify-between flex-wrap gap-2 mb-2">
                        <code class="text-sm font-mono font-semibold text-surface-900 dark:text-surface-0 bg-surface-100 dark:bg-surface-700 px-2 py-1 rounded-lg">
                            {{ cmd.syntax }}
                        </code>
                    </div>
                    <!-- 說明 -->
                    <p class="text-sm text-surface-700 dark:text-surface-300 mb-2">{{ cmd.desc }}</p>
                    <!-- 範例 -->
                    <div class="flex items-center gap-2">
                        <span class="text-xs text-muted-color">範例：</span>
                        <code class="text-xs font-mono bg-surface-0 dark:bg-surface-900 border border-surface-200 dark:border-surface-700 px-2 py-0.5 rounded-md text-primary">
                            {{ cmd.example }}
                        </code>
                    </div>
                </div>
            </div>
        </div>

        <!-- 分類對照 -->
        <div class="card">
            <div class="flex items-center gap-2 mb-4">
                <div class="flex items-center justify-center w-8 h-8 rounded-lg bg-purple-50 dark:bg-purple-950">
                    <i class="pi pi-tag text-purple-500 text-sm" />
                </div>
                <span class="font-semibold text-lg text-surface-900 dark:text-surface-0">分類對照表</span>
            </div>
            <p class="text-muted-color text-sm mb-4">輸入中文別名時，系統自動對應到以下分類；也可直接輸入英文分類名稱。</p>

            <DataTable :value="CATEGORIES" responsive-layout="scroll" striped-rows>
                <Column header="輸入關鍵字" style="min-width:220px">
                    <template #body="{ data }">
                        <span class="text-sm text-surface-700 dark:text-surface-300 font-mono">{{ data.alias }}</span>
                    </template>
                </Column>
                <Column header="對應分類" style="width:110px">
                    <template #body="{ data }">
                        <span :class="['inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold', TYPE_CLASS[data.type] ?? 'bg-gray-100 text-gray-600']">
                                {{ data.type }}
                            </span>
                    </template>
                </Column>
            </DataTable>
        </div>


    </div>
</template>
