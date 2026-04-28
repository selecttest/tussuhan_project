<script setup>
import { computed } from 'vue';

const props = defineProps({
    month: { type: String, default: '' },
    availableMonths: { type: Array, default: () => [] },
    records: { type: Array, default: () => [] },
    total: { type: Number, default: 0 }
});
const emit = defineEmits(['update:month']);

const monthTotal = computed(() => props.total || props.records.reduce((sum, r) => sum + Number(r.amount || 0), 0));

const TYPE_SEVERITY = {
    Food: 'info',
    Baby: 'warning',
    Drink: 'success',
    Tuition: 'help',
    Other: 'secondary',
};

const PAYER_SEVERITY = { T: 'info', F: 'warn' };
</script>

<template>
    <div class="card">
        <div class="flex items-center justify-between mb-4">
            <div>
                <div class="font-semibold text-xl">支出紀錄</div>
                <div class="text-muted-color text-sm mt-1">本月合計 NT$ {{ monthTotal.toLocaleString() }}</div>
            </div>
            <Select
                :model-value="month"
                :options="availableMonths"
                placeholder="選擇月份"
                class="w-36"
                @update:model-value="emit('update:month', $event)"
            />
        </div>

        <DataTable :value="records" :rows="8" :paginator="records.length > 8" responsiveLayout="scroll" stripedRows>
            <Column field="date" header="日期" style="width:110px">
                <template #body="{ data }">
                    <span class="text-muted-color text-sm">{{ data.date }}</span>
                </template>
            </Column>
            <Column field="type" header="分類" style="width:90px">
                <template #body="{ data }">
                    <Tag :value="data.type" :severity="TYPE_SEVERITY[data.type] || 'secondary'" />
                </template>
            </Column>
            <Column field="detail" header="品項" style="min-width:120px">
                <template #body="{ data }">
                    <span class="font-medium">{{ data.detail }}</span>
                </template>
            </Column>
            <Column field="amount" header="金額" style="width:110px">
                <template #body="{ data }">
                    <span class="font-semibold text-red-500 dark:text-red-400">
                        NT$ {{ data.amount.toLocaleString() }}
                    </span>
                </template>
            </Column>
            <Column field="payer" header="付款" style="width:70px">
                <template #body="{ data }">
                    <Tag :value="data.payer" :severity="PAYER_SEVERITY[data.payer] || 'secondary'" />
                </template>
            </Column>
            <Column header="T / F" style="width:160px">
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
</template>
