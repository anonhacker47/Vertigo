<template>
  <div class="dropdown dropdown-bottom dropdown-center">
    <button tabindex="0" class="btn m-1 focus:ring">
      <svg
        width="24"
        height="24"
        xmlns="http://www.w3.org/2000/svg"
        fill-rule="evenodd"
        class="focus:fill-black"
        clip-rule="evenodd"
      >
        <path
          d="M12.01 20c-5.065 0-9.586-4.211-12.01-8.424 2.418-4.103 6.943-7.576 12.01-7.576 5.135 0 9.635 3.453 11.999 7.564-2.241 4.43-6.726 8.436-11.999 8.436zm-10.842-8.416c.843 1.331 5.018 7.416 10.842 7.416 6.305 0 10.112-6.103 10.851-7.405-.772-1.198-4.606-6.595-10.851-6.595-6.116 0-10.025 5.355-10.842 6.584zm10.832-4.584c2.76 0 5 2.24 5 5s-2.24 5-5 5-5-2.24-5-5 2.24-5 5-5zm0 1c2.208 0 4 1.792 4 4s-1.792 4-4 4-4-1.792-4-4 1.792-4 4-4z"
          fill="#a5f3fc"
        />
      </svg>
    </button>
    <button
      tabindex="0"
      class="dropdown-content cursor-default card shadow bg-base-100 border border-slate-700 rounded-md w-64 md:w-80 z-20"
    >
      <div class="label px-2 justify-center flex border-b border-slate-700">
        <span class="font-bold text-lg text-sky-200 text-grey-500"
          >Display Options</span
        >
      </div>

      <div
        class="flex justify-between mt-1 px-2 pb-1 border-b border-slate-700"
      >
        <div class="form-control">
          <label class="label cursor-pointer">
            <span class="text-slate-200 ml-2">Card View</span>
            <input
              type="radio"
              name="viewMode"
              value="card"
              class="radio ml-4"
              v-model="viewMode"
              @change="changeViewMode('card')"
            />
          </label>
        </div>
        <div class="form-control">
          <label class="label cursor-pointer">
            <span class="text-slate-200">List View</span>
            <input
              type="radio"
              name="viewMode"
              value="list"
              class="radio ml-4 mr-2"
              v-model="viewMode"
              @change="changeViewMode('list')"
            />
          </label>
        </div>
      </div>

      <div class="border-b border-slate-700 pb-4" v-if="viewMode == 'card'">
        <div class="label justify-center pt-0">
          <span class="text-slate-200 text-sm">Items per line</span>
        </div>
        <div v-if="getScreenWidth() >= 500" class="px-5">
          <input
            @change="changeGrid"
            type="range"
            min="2"
            max="10"
            :value="selectedGrid"
            class="range range-xs"
            step="1"
          />
        </div>
        <div
          v-if="getScreenWidth() >= 500"
          class="w-full flex justify-between text-xs px-5"
        >
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
          <input
            @change="changeGrid"
            type="range"
            min="2"
            max="5"
            :value="selectedGrid"
            class="range range-xs"
            step="1"
          />
        </div>
        <div
          v-if="getScreenWidth() < 500"
          class="w-full flex justify-between text-xs px-5"
        >
          <span>2</span>
          <span>3</span>
          <span>4</span>
          <span>5</span>
        </div>
      </div>

      <div class="border-t border-slate-700 mt-2 pt-2 px-4">
        <div class="label justify-center pt-0">
          <span class="text-slate-200 text-sm">Items per page</span>
        </div>

        <div class="flex flex-wrap gap-4">
          <label
            class="label cursor-pointer"
            v-for="size in [10, 25, 50, 100]"
            :key="size"
          >
            <span class="text-slate-200 mr-2">{{ size }}</span>
            <input
              type="radio"
              name="itemsPerPage"
              class="radio radio-sm radio-primary"
              :value="size"
              v-model="itemsPerPage"
            />
          </label>
        </div>
      </div>

      <div class="flex justify-between px-3">
        <div class="label">
          <span class="font-bold text-lg text-sky-200">Sort By</span>
        </div>
        <div class="flex">
          <input
            type="radio"
            id="asc"
            value="asc"
            name="asc"
            class="hidden"
            @click="orderDirection"
            v-model="orderDir"
          /><label
            for="asc"
            class="label text-gray-400 label-text mr-2 text-sm cursor-pointer"
            >Asc</label
          >
          <input
            type="radio"
            id="desc"
            value="desc"
            name="asc"
            class="hidden"
            @click="orderDirection"
            v-model="orderDir"
          /><label
            for="desc"
            class="label text-gray-400 label-text text-sm cursor-pointer"
            >Desc</label
          >
        </div>
      </div>
      <div class="form-control px-5">
        <label class="label cursor-pointer">
          <span class="text-slate-200">Title</span>
          <input
            type="radio"
            name="orderBy"
            class="radio checked:bg-red-500"
            @click="orderByProperties"
            value="title"
            v-model="orderBy"
          />
        </label>
      </div>
      <div class="form-control px-5 pb-2">
        <label class="label cursor-pointer">
          <span class="text-slate-200">Date Added</span>
          <input
            type="radio"
            name="orderBy"
            class="radio checked:bg-blue-500"
            @click="orderByProperties"
            value="timestamp"
            v-model="orderBy"
          />
        </label>
      </div>
    </button>
  </div>
</template>

<script setup lang="ts">
import { useUserPreferences } from "@/store/userPreferences";

defineProps<{
  getScreenWidth: () => number;
  selectedGrid: string | number | null;
  changeGrid: (selected: any) => void;
  orderDirection: (values: any) => void;
  orderByProperties: (values: any) => void;
  itemsPerPage: number;
}>();

const viewMode = defineModel<string>("viewMode", { required: true });
const orderBy = defineModel<string>("orderBy", { required: true });
const orderDir = defineModel<string>("orderDir", { required: true });
const itemsPerPage = defineModel<number>("itemsPerPage", { required: true });

const userPreferences = useUserPreferences();

const changeViewMode = (mode: "card" | "list") => {
  userPreferences.setViewMode(mode);
  viewMode.value = mode;
};
</script>

<style>
input:checked + label {
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
