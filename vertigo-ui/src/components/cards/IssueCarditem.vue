<template>
  <div :class="{ 'animate-wiggle': editMode && is_last }" class="w-44 h-64 flex relative flex-col rounded-lg border-2 overflow-hidden shadow-lg bg-zinc-900"
    :style="`border-color: rgb${themecolor};`">
    <!-- <button v-if="is_last" @click="$emit('deleteIssue')"
      class="absolute top-2 right-2 text-red-500 hover:text-red-700 transition-colors z-10" title="Delete">
      ✕
    </button> -->
    <div v-if="editMode && is_last" @click.prevent="$emit('deleteIssue')"
      class="absolute top-0 right-0 rounded hover:scale-105 hover:rotate-180 z-[800] transition ease-in-out">
      <img src="@/assets/remove.svg" alt="" height="30" width="30" class="min-w-[25px] min-h-[25px]" />
    </div>
    <!-- Cover Image -->
    <div class="h-[70%] w-full bg-cover bg-center relative" :style="`background-image: url(${image})`">
      <!-- Title Overlay -->
      <div class="absolute inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center px-3">
        <p class="text-white text-2xl font-semibold text-center leading-snug tracking-wide">
          Vol. {{ title }}
        </p>
      </div>
    </div>

    <!-- Bottom Section -->
    <div class="space-y-1 text-white text-sm font-semibold px-2 py-2">

      <!-- Owned Row -->
      <div class="flex flex-col gap-1">
        <div class="flex items-center gap-2 cursor-pointer hover:bg-zinc-700 px-2 py-1 rounded transition-all"
          @click="handleStatusClick('is_owned')">
          <img :class="is_owned ? 'opacity-100' : 'invert'" src="../../assets/collection.svg" alt="Owned"
            class="w-6 h-6" />
          <span class="truncate">
            {{ is_owned ? (bought_date ? '' + formatDate(bought_date) : 'Owned') : 'Not Owned' }}
          </span>
        </div>

        <input v-if="showOwnedDatePicker" type="date" class="bg-zinc-800 text-white rounded px-2 py-1"
          @change="event => handleDateChange('is_owned', event)" />
      </div>

      <!-- Bought Price Row -->
      <!-- Bought Price Row -->
      <div v-if="is_owned" class="flex flex-col gap-1 border-b border-zinc-700 pb-2">
        <div class="flex items-center gap-3 cursor-pointer hover:bg-zinc-700 px-2 py-1 rounded transition-all"
          @click="handlePriceClick">
          <!-- <img src="../../assets/price-tag.svg" alt="Price" class="w-5 h-5 -scale-x-100" /> -->
          <span class="truncate ml-1 justify-center items-center flex text-emerald-500 text-xl">
            {{ symbol }}
          </span>
          <span class="truncate">
            {{ props.bought_price !== null ? `${props.bought_price}` : 'Add Price' }}
          </span>
        </div>
        <input v-if="showPriceInput" type="number" min="0" step="0.01" placeholder="Enter Price"
          class="bg-zinc-800 text-white rounded px-2 py-1" @change="handlePriceChange" :value="props.bought_price ?? ''" />
      </div>

      <!-- Read Row -->
      <div class="flex flex-col gap-1">
        <div class="flex items-center gap-2 cursor-pointer hover:bg-zinc-700 px-2 py-1 rounded transition-all"
          @click="handleStatusClick('is_read')">
          <img :class="is_read ? 'opacity-100' : 'invert'" src="../../assets/read.svg" alt="Read" class="w-6 h-6" />
          <span class="truncate">
            {{ is_read ? (read_date ? '' + formatDate(read_date) : 'Read') : 'Not Read' }}
          </span>
        </div>

        <input v-if="showReadDatePicker" type="date" class="bg-zinc-800 text-white rounded px-2 py-1"
          @change="event => handleDateChange('is_read', event)" />
      </div>
    </div>


  </div>
</template>


<script setup lang="ts">
import { ref, watch } from 'vue';
import { computed } from 'vue'
import getSymbolFromCurrency from 'currency-symbol-map'

const props = defineProps({
  image: String,
  themecolor: String,
  title: String,
  is_owned: Boolean,
  is_read: Boolean,
  bought_date: Date,
  read_date: Date,
  bought_price: Number,
  preferred_currency: String,
  is_last: Boolean,
  edit_mode: Boolean,
})

const editMode = computed(() => props.edit_mode)

watch(editMode, (newVal, oldVal) => {
  console.log('editMode changed:', oldVal, '→', newVal)
})

const symbol = getSymbolFromCurrency(props.preferred_currency)

function formatDate(dateStr: Date | string): string {
  return new Date(dateStr).toLocaleDateString('en-GB', {
    day: 'numeric',
    month: 'short',
    year: 'numeric',
  });
}
const showOwnedDatePicker = ref(false);
const showReadDatePicker = ref(false);
const showPriceInput = ref(false);

function handlePriceClick() {
  showPriceInput.value = true;
}

function handlePriceChange(event: Event) {
  const price = parseFloat((event.target as HTMLInputElement).value);
  emit('updateStatus', { status: 'bought_price', value: price });
  showPriceInput.value = false;
}

const emit = defineEmits(['updateStatus', 'updateDate', 'deleteIssue']);

function handleStatusClick(status: 'is_owned' | 'is_read') {
  if (status === 'is_owned' && !props.is_owned) {
    showOwnedDatePicker.value = true;
  } else if (status === 'is_read' && !props.is_read) {
    showReadDatePicker.value = true;
  } else {
    // If already enabled and clicked again → disable with null date
    emit('updateStatus', { status, value: false });
  }
}

function handleDateChange(status: 'is_owned' | 'is_read', event: Event) {
  const date = (event.target as HTMLInputElement).value;
  emit('updateStatus', { status, value: true, date });

  if (status === 'is_owned') showOwnedDatePicker.value = false;
  else if (status === 'is_read') showReadDatePicker.value = false;
}

</script>

<style scoped></style>