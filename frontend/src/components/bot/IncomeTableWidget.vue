<script setup>
import { computed } from 'vue';

const props = defineProps({
    month: { type: String, default: '' },
    availableMonths: { type: Array, default: () => [] },
    records: { type: Array, default: () => [] },
    total: { type: Number, default: 0 }
});
const emit = defineEmits(['update:month']);

const monthTotal = computed(() => props.total || props.records.reduce((sum, record) => sum + Number(record.amount || 0), 0));

const typeSeverity = {
    固定收入: 'success',
    模板:     'info',
    接案:     'warning',
    獎金:     'danger',
    網拍:     'secondary'
};
</script>

<template>
    <div class="card">
        <div class="flex items-center justify-between mb-4">
            <div>
                <div class="font-semibold text-xl">收入紀錄</div>
                <div class="text-muted-color text-sm mt-1">本月合計 NT$ {{ monthTotal.toLocaleString() }}</div>
            </div>
            <Select :model-value="month" :options="availableMonths" placeholder="選擇月份" class="w-36" @update:model-value="emit('update:month', $event)" />
        </div>

        <DataTable :value="records" :rows="6" :paginator="records.length > 6" responsiveLayout="scroll" stripedRows>
            <Column field="name" header="收入來源" style="min-width: 140px">
                <template #body="{ data }">
                    <div class="flex items-center gap-2">
                        <i class="pi pi-dollar text-primary text-sm"></i>
                        <span class="font-medium">{{ data.name }}</span>
                    </div>
                </template>
            </Column>
            <Column field="date" header="入帳日期" style="width: 120px">
                <template #body="{ data }">
                    <span class="text-muted-color text-sm">{{ data.date }}</span>
                </template>
            </Column>
            <Column field="type" header="類型" style="width: 110px">
                <template #body="{ data }">
                    <Tag :value="data.type" :severity="typeSeverity[data.type] || 'secondary'" />
                </template>
            </Column>
            <Column field="amount" header="金額" style="width: 130px">
                <template #body="{ data }">
                    <span class="font-semibold text-green-600 dark:text-green-400">
                        NT$ {{ data.amount.toLocaleString() }}
                    </span>
                </template>
            </Column>
        </DataTable>
    </div>
</template>
