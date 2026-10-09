<template>
  <details class="dropdown dropdown-end">
    <summary class="inline-flex h-10 cursor-pointer select-none items-center gap-2 rounded-lg border border-slate-700 bg-base-100 px-3.5 text-sm font-bold text-slate-200 hover:border-slate-500">
      <i class="pi pi-sliders-h text-sky-300"></i> Display
    </summary>

    <ul
      class="menu dropdown-content cursor-default card shadow bg-base-100 border border-slate-700 rounded-md w-64 md:w-80 z-100">
      <div class="label px-2 justify-center flex">
        <span class="font-bold text-lg text-sky-200 text-grey-500">Display Options</span>
      </div>

      <div class="flex justify-center mt-1 px-2">
        <SelectButton v-model="viewModeModel" :options="[
          { label: 'Card View', value: 'card' },
          { label: 'List View', value: 'list' }
        ]" optionValue="value" optionLabel="label" />
      </div>

      <div class="border-b border-slate-700 py-4" v-if="viewMode == 'card'">
        <div class="label justify-center pt-0">
          <span class="text-slate-200 text-sm">Items per line</span>
        </div>
        <div v-if="getScreenWidth() >= 500" class="px-5">
          <input @change="changeGrid" type="range" min="2" max="10" :value="selectedGrid" class="range range-xs"
            step="1" />
        </div>
        <div v-if="getScreenWidth() >= 500" class="w-full flex justify-between text-xs px-5">
          <span>2</span>
          <span>3</span>
          <span>4</span>
          <span>5</span>
          <span>6</span>
          <span>7</span>
          <span>8</span>
          <span>9</span>
          <span>10</span>
        </div>
        <div v-if="getScreenWidth() < 500" class="px-5">
          <input @change="changeGrid" type="range" min="2" max="5" :value="selectedGrid" class="range range-xs"
            step="1" />
        </div>
        <div v-if="getScreenWidth() < 500" class="w-full flex justify-between text-xs px-5">
          <span>2</span>
          <span>3</span>
          <span>4</span>
          <span>5</span>
        </div>
      </div>

      <div class="mt-2 pt-2 px-4">
        <div class="label justify-center pt-0">
          <span class="text-slate-200 text-sm">Items per page</span>
        </div>

        <div class="flex flex-wrap justify-center gap-4">
          <div v-for="size in [10, 25, 50, 100]" :key="size" class="flex items-center gap-2 cursor-pointer">
            <RadioButton v-model="itemsPerPage" :value="size" :inputId="'ipp-' + size" name="itemsPerPage" :pt="{
              root: 'cursor-pointer',
              input: 'cursor-pointer',
              box: 'w-4 h-4 border border-slate-500 bg-slate-800 rounded-full flex items-center justify-center data-[p-highlight=true]:border-blue-400',
              icon: 'bg-blue-400 w-2 h-2 rounded-full'
            }" />

            <label :for="'ipp-' + size" class="text-slate-200 text-sm cursor-pointer">
              {{ size }}
            </label>
          </div>
        </div>
      </div>

      <div class="flex justify-between px-5 mt-2">
        <div class="label">
          <span class="font-bold text-lg text-sky-200">Sort By</span>
        </div>
        <div class="flex items-center gap-4">
          <div class="flex items-center gap-2 cursor-pointer">
            <RadioButton v-model="orderDir" inputId="asc" name="orderDir" value="asc" @click="orderDirection" />
            <label for="asc" class="text-gray-400 text-sm cursor-pointer">Asc</label>
          </div>

          <div class="flex items-center gap-2 cursor-pointer">
            <RadioButton v-model="orderDir" inputId="desc" name="orderDir" value="desc" @click="orderDirection" />
            <label for="desc" class="text-gray-400 text-sm cursor-pointer">Desc</label>
          </div>
        </div>
      </div>
      <div class=" gap-4 py-2 px-6">
        <div class="flex items-center justify-between gap-3 cursor-pointer">
          <label for="order-title" class="text-slate-200 cursor-pointer font-bold">Title</label>
          <RadioButton v-model="orderBy" inputId="order-title" name="orderBy" value="title"
            @click="orderByProperties" />
        </div>

        <div class="flex items-center gap-3 justify-between cursor-pointer">
          <label for="order-date" class="text-slate-200 cursor-pointer font-bold">Date Added</label>
          <RadioButton v-model="orderBy" inputId="order-date" name="orderBy" value="timestamp"
            @click="orderByProperties" />
        </div>
      </div>
    </ul>
  </details>
</template>

<script setup lang="ts">
import { useUserPreferences } from "@/store/userPreferences";
import SelectButton from 'primevue/selectbutton';
import RadioButton from 'primevue/radiobutton'

defineProps<{
  getScreenWidth: () => number;
  selectedGrid: string | number | null;
  changeGrid: (selected: any) => void;
  orderDirection: (values: any) => void;
  orderByProperties: (values: any) => void;
  itemsPerPage: number;
}>();

const viewModeModel = defineModel<string>("viewMode");
const orderBy = defineModel<string>("orderBy", { required: true });
const orderDir = defineModel<string>("orderDir", { required: true });
const itemsPerPage = defineModel<number>("itemsPerPage", { required: true });

const userPreferences = useUserPreferences();

</script>

<style>
input:checked+label {
  border: 2px;
  color: #38bdf8;
}

.dropdown.dropdown-center.dropdown-right .dropdown-content,
.dropdown-center.dropdown-left .dropdown-content {
  @apply top-1/2 transform -translate-y-1/2;
}

.dropdown-center.dropdown-bottom .dropdown-content,
.dropdown-center.dropdown-top .dropdown-content {
  @apply left-1/2 transform -translate-x-1/2;
}
</style>
