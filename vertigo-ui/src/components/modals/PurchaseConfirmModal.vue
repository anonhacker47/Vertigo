<template>
  <div v-if="show"
    class="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/70 backdrop-blur-md transition-all duration-200">
    <form class="bg-slate-900 border border-slate-800 rounded-2xl p-6 max-w-sm w-full mx-4 shadow-2xl relative" @submit.prevent="handleConfirm">
      <h3 class="text-lg font-bold text-white mb-5">Add Purchase Details</h3>

      <div class="flex flex-col gap-4 mb-6">
        <div class="flex flex-col gap-1.5">
          <label for="purchase-date" class="text-xs font-bold text-slate-400 uppercase tracking-wider">Bought Date</label>
          <DatePicker :model-value="ymdToDate(localDate)" input-id="purchase-date" date-format="d M yy" show-icon icon-display="input" fluid
            @update:model-value="localDate = dateToYmd($event as Date | null) ?? ''" />
        </div>

        <div class="flex flex-col gap-1.5">
          <label for="purchase-price" class="text-xs font-bold text-slate-400 uppercase tracking-wider">Purchase Price</label>
          <InputNumber v-model="localPrice" input-id="purchase-price" mode="decimal" :min="0" :max-fraction-digits="2"
            :prefix="currency ? `${currency} ` : undefined" placeholder="0.00" fluid />
        </div>
      </div>

      <div class="flex items-center gap-3 justify-end border-t border-slate-800/60 pt-4">
        <button type="button" @click="$emit('cancel')"
          class="px-4 py-2 text-sm font-semibold text-slate-400 hover:text-white hover:bg-slate-800 rounded-xl transition">
          Cancel
        </button>
        <button type="submit"
          class="px-5 py-2 text-sm font-bold text-slate-950 bg-emerald-400 hover:bg-emerald-300 rounded-xl transition shadow-lg shadow-emerald-500/10">
          Mark as Owned
        </button>
      </div>
    </form>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, nextTick } from 'vue';
import DatePicker from 'primevue/datepicker';
import InputNumber from 'primevue/inputnumber';
import { dateToYmd, ymdToDate } from '@/utils/dateInput';

const props = defineProps<{
  show: boolean;
  currency?: string;
  initialPrice?: number | null;
  initialDate?: string | null;
}>();

const emit = defineEmits<{
  (e: 'cancel'): void;
  (e: 'confirm', payload: { price: number | null; date: string | null }): void;
}>();

const localPrice = ref<number | null>(null);
// Kept as "YYYY-MM-DD" like the other forms; the picker converts at its edges.
const localDate = ref<string>("");

watch(() => props.show, (isShowing) => {
  if (isShowing) {
    localPrice.value = props.initialPrice ?? null;
    localDate.value = props.initialDate ? props.initialDate.substring(0, 10) : "";
    nextTick(() => document.getElementById('purchase-price')?.focus());
  }
});

function handleConfirm() {
  const finalPrice = localPrice.value !== null && !isNaN(Number(localPrice.value))
    ? Number(localPrice.value)
    : null;
  const finalDate = localDate.value ? new Date(localDate.value).toISOString() : null;

  emit('confirm', { price: finalPrice, date: finalDate });
}
</script>
