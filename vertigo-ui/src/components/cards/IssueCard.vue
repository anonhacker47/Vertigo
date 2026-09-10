<template>
  <div :class="{ 'animate-wiggle': editMode && is_last }"
    class="w-44 h-64 flex relative flex-col rounded-lg border-2 shadow-lg bg-zinc-900"
    :style="`border-color: rgb${themecolor};`">
    
    <div v-if="editMode && is_last" @click.prevent="$emit('deleteIssue')"
      class="absolute -top-3 -right-3 rounded hover:scale-105 hover:rotate-180 z-[800] transition ease-in-out">
      <img src="@/assets/remove.svg" alt="" height="30" width="30" class="min-w-[25px] min-h-[25px]" />
    </div>

    <RouterLink :to="{ name: 'IssueDetail', params: { seriesId: series.id, slug: series.slug, number: issue.number } }"
      class="h-[70%] w-full bg-cover bg-center relative rounded-t-lg overflow-hidden block group cursor-pointer"
      :style="`background-image: url(${coverImage})`">
      <div
        class="absolute inset-0 bg-black/60 backdrop-blur-xs flex flex-col items-center justify-center gap-0.5 px-3 group-hover:bg-black/40 transition-colors duration-200">
        <p v-if="hasCustomTitle" class="text-slate-300 text-xs font-semibold tracking-widest">
          {{ issueNumberLabel(issue.number) }}
        </p>
        <p class="text-white font-semibold text-center leading-snug tracking-wide"
          :class="hasCustomTitle ? 'text-lg line-clamp-3' : 'text-2xl'">
          {{ hasCustomTitle ? issue.title : issueNumberLabel(issue.number) }}
        </p>
      </div>
    </RouterLink>

    <div class="space-y-1 text-white text-sm bg-base-100 rounded-b-lg font-semibold px-2 py-2">

      <div class="flex flex-col gap-1">
        <div class="flex items-center gap-2 cursor-pointer hover:bg-zinc-700 px-2 py-1 rounded transition-all"
          @click="handleStatusClick('is_owned')">
          <img :class="issue.is_owned ? 'opacity-100' : 'invert'" src="../../assets/collection.svg" alt="Owned" class="w-6 h-6" />
          <span class="truncate">
            {{ issue.is_owned ? (issue.bought_date ? formatDate(issue.bought_date) : 'Owned') : 'Not Owned' }}
          </span>
        </div>
        <input v-if="showOwnedDatePicker" type="date" class="bg-zinc-800 text-white rounded px-2 py-1"
          @change="event => handleDateChange('is_owned', event)" />
      </div>

      <div v-if="issue.is_owned" class="flex flex-col gap-1 border-b border-zinc-700 pb-2">
        <div class="flex items-center gap-3 cursor-pointer hover:bg-zinc-700 px-2 py-1 rounded transition-all"
          @click="handlePriceClick">
          <span class="truncate ml-1 justify-center items-center flex text-emerald-500 text-xl">{{ symbol }}</span>
          <span class="truncate">
            {{ issue.bought_price !== null && issue.bought_price !== undefined ? `${issue.bought_price}` : 'Add Price' }}
          </span>
        </div>
        <input v-if="showPriceInput" type="number" min="0" step="0.01" placeholder="Enter Price"
          class="bg-zinc-800 text-white rounded px-2 py-1" @change="handlePriceChange"
          :value="issue.bought_price ?? ''" />
      </div>

      <div class="flex flex-col gap-1">
        <div class="flex items-center gap-2 cursor-pointer hover:bg-zinc-700 px-2 py-1 rounded transition-all"
          @click="handleStatusClick('is_read')">
          <img :class="issue.is_read ? 'opacity-100' : 'invert'" src="../../assets/read.svg" alt="Read" class="w-6 h-6" />
          <span class="truncate">
            {{ issue.is_read ? (issue.read_date ? formatDate(issue.read_date) : 'Read') : 'Not Read' }}
          </span>
        </div>
        <input v-if="showReadDatePicker" type="date" class="bg-zinc-800 text-white rounded px-2 py-1"
          @change="event => handleDateChange('is_read', event)" />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import getSymbolFromCurrency from 'currency-symbol-map';
import { Issue } from '@/types/issue.types';
import IssueService from '@/services/IssueService';
import { hasCustomIssueTitle, issueNumberLabel } from '@/utils/issueTitle';

const props = defineProps({
  issue: { type: Object as () => Issue, required: true },
  image: String,
  themecolor: String,
  preferred_currency: String,
  is_last: Boolean,
  edit_mode: Boolean,
  series: { type: Object, required: true }
});

const emit = defineEmits(['updateStatus', 'deleteIssue']);

const editMode = computed(() => props.edit_mode);

const hasCustomTitle = computed(() => hasCustomIssueTitle(props.issue.title, props.issue.number));

// The issue's own cover (cache-busted by last_updated) wins; otherwise the series cover passed as `image`.
const coverImage = computed(() =>
  props.issue.thumbnail
    ? IssueService.getIssueImageById(props.issue.id, props.issue.last_updated)
    : props.image
);
const symbol = getSymbolFromCurrency(props.preferred_currency);

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

function handleStatusClick(status: 'is_owned' | 'is_read') {
  if (status === 'is_owned' && !props.issue.is_owned) {
    showOwnedDatePicker.value = true;
  } else if (status === 'is_read' && !props.issue.is_read) {
    showReadDatePicker.value = true;
  } else {
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