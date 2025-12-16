<template>
  <details class="dropdown">
    <summary class="btn m-1">

      <svg width="24" height="24" xmlns="http://www.w3.org/2000/svg" fill-rule="evenodd" class="focus:fill-black"
        clip-rule="evenodd">
        <path
          d="M12.01 20c-5.065 0-9.586-4.211-12.01-8.424 2.418-4.103 6.943-7.576 12.01-7.576 5.135 0 9.635 3.453 11.999 7.564-2.241 4.43-6.726 8.436-11.999 8.436zm-10.842-8.416c.843 1.331 5.018 7.416 10.842 7.416 6.305 0 10.112-6.103 10.851-7.405-.772-1.198-4.606-6.595-10.851-6.595-6.116 0-10.025 5.355-10.842 6.584zm10.832-4.584c2.76 0 5 2.24 5 5s-2.24 5-5 5-5-2.24-5-5 2.24-5 5-5zm0 1c2.208 0 4 1.792 4 4s-1.792 4-4 4-4-1.792-4-4 1.792-4 4-4z"
          fill="#a5f3fc" />
      </svg>
    </summary>

    <ul
      class="menu dropdown-content cursor-default card shadow bg-base-100 border border-slate-700 rounded-md w-64 md:w-80 z-[100]">
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
      <div class="form-control gap-4 py-2 px-6">
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
