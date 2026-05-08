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
                syntax: '[品項] [金額]',
                example: '拉亞+M 415',
                desc: '極簡記帳。自動推測分類、預設 T 付全額、日期為今日。',
            },
            {
                syntax: 'F [品項] [金額]',
                example: 'F coco 99',
                desc: 'F 結帳付全額。Payer = F，T_paid = 0，F_paid = 金額。',
            },
            {
                syntax: '[品項] [金額] 分[對方負擔]',
                example: '早餐+便當 590 分215',
                desc: '分帳規則：分後面的金額是「F」負擔。',
            },
            {
                syntax: '[日期] [類別] [F] [品項] [金額] [分X]',
                example: '昨天 food F 聚餐 600 分300',
                desc: '進階寫法。日期支援：昨天 / 前天 / 5/7 / 2026/5/7。',
            },
            {
                syntax: '多筆（換行或 ; / ； 分隔）',
                example: '拉亞 415; F coco 99; 早餐+便當 590 分215',
                desc: '一次送多筆記帳，系統會逐筆解析與寫入，成功後回覆批次結果。',
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
                desc: '查詢本月摘要（總支出、T/F 負擔、結算）。',
            },
            {
                syntax: '查 [YYYY-MM] / 查 [4月]',
                example: '查 2026-04',
                desc: '查詢指定月份支出摘要',
            },
            {
                syntax: '查 [分類]',
                example: '查 餐費',
                desc: '查詢本月該分類小計（food / drink / baby / tuition / insurance / other）。',
            },
            {
                syntax: '今日',
                example: '今日',
                desc: '查詢今日所有支出明細（最多顯示 5 筆）',
            },
            {
                syntax: '昨天',
                example: '昨天',
                desc: '查詢昨天所有支出明細。',
            },
            {
                syntax: '本月',
                example: '本月',
                desc: '查詢本月支出摘要，等同於「查」',
            },
            {
                syntax: '最近 / 最近5',
                example: '最近8',
                desc: '查詢最近 N 筆紀錄（1~20 筆，預設 5）。',
            },
            {
                syntax: '結算',
                example: '結算',
                desc: '查詢本月誰該補誰（依雙方付款差額計算）。',
            },
            {
                syntax: '刪 / 撤銷',
                example: '刪',
                desc: '刪除最新一筆紀錄（安全起見僅最後一筆）。',
            },
            {
                syntax: 'help / 說明 / 幫助 / 指令',
                example: 'help',
                desc: '顯示完整指令清單（記帳 / 查詢 / 操作）。',
            },
        ],
    },
];

const TYPE_CLASS = {
    food:      'bg-orange-100 text-orange-700 dark:bg-orange-900/60 dark:text-orange-300',
    baby:      'bg-pink-100 text-pink-700 dark:bg-pink-900/60 dark:text-pink-300',
    drink:     'bg-teal-100 text-teal-700 dark:bg-teal-900/60 dark:text-teal-300',
    tuition:   'bg-violet-100 text-violet-700 dark:bg-violet-900/60 dark:text-violet-300',
    other:     'bg-slate-100 text-slate-600 dark:bg-slate-700/60 dark:text-slate-300',
    insurance: 'bg-blue-100 text-blue-700 dark:bg-blue-900/60 dark:text-blue-300',
};

const CATEGORIES = [
    { alias: '餐費 / 食物 / 早餐 / 午餐 / 晚餐', type: 'food' },
    { alias: '飲料 / 喝', type: 'drink' },
    { alias: '寶寶 / 嬰兒 / 育兒', type: 'baby' },
    { alias: '學費 / 補習', type: 'tuition' },
    { alias: '保險 / 保費', type: 'insurance' },
    { alias: '其他（或直接輸入英文分類）', type: 'other' },
];
</script>

<template>
    <div class="flex flex-col gap-6">

        <!-- 頁首 -->
        <div class="flex items-center justify-between flex-wrap gap-3">
            <div class="flex items-center gap-3">
                <Button icon="pi pi-arrow-left" text rounded size="small" @click="router.back()" />
                <div>
                    <h1 class="text-2xl font-bold text-surface-900 dark:text-surface-0">LINE Bot 指令說明（新版）</h1>
                    <p class="text-muted-color mt-1">極簡記帳 · 補記日期 · 查詢結算 · 分類對照</p>
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
                    <li class="flex items-start gap-2"><i class="pi pi-check-circle text-green-500 mt-0.5 flex-shrink-0" />補記日期請放在最前面，支援：昨天 / 前天 / 5/7 / 2026/5/7。</li>
                    <li class="flex items-start gap-2"><i class="pi pi-check-circle text-green-500 mt-0.5 flex-shrink-0" />分帳金額不可大於總金額。</li>
                    <li class="flex items-start gap-2"><i class="pi pi-check-circle text-green-500 mt-0.5 flex-shrink-0" />補記日期不可是未來，且不可早於 30 天前。</li>
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
