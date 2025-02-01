<template>
  <Combobox v-model="selected" nullable>
    <div class="relative w-full">
      <div class="relative w-full cursor-default rounded-lg bg-base-10">
        <ComboboxInput class="w-full input input-bordered" autoComplete="off" @change="query = $event.target.value"
          :placeholder="placeholder" />
        <ComboboxButton class="absolute inset-y-0 right-0 flex items-center pr-2">
          <ChevronUpDownIcon class="h-5 w-5 text-gray-400" aria-hidden="true" />
        </ComboboxButton>
      </div>  
      <TransitionRoot leave="transition ease-in duration-100" leaveFrom="opacity-100" leaveTo="opacity-0"
        @after-leave="query = ''">
        <ComboboxOptions
          class="absolute mt-1 max-h-60 w-full overflow-auto rounded-md bg-base-100 py-1 shadow-lg ring-1 ring-black/5 focus:outline-none sm:text-sm"
          style="z-index: 1;">
          <ComboboxOption v-for="item in filteredItems" as="template" :key="item.id" :value="item.value"
            v-slot="{ active }">
            <ul class="">
              <li class="relative cursor-pointer  select-none py-3 pl-10 pr-4" :class="{
                'bg-base-300 text-white': active,
                'text-white': !active,
              }">
                <span class="block truncate" :class="{ 'font-medium': active, 'font-normal': !active }">
                  {{ item.value }}
                </span>
                <span v-if="selected" class="absolute inset-y-0 left-0 flex items-center pl-3"
                  :class="{ 'text-teal-400': active, 'text-white': !active }">
                  <CheckIcon class="h-5 w-5" aria-hidden="true" />
                </span>
              </li>
            </ul>
          </ComboboxOption>
          <ComboboxOption v-slot="{ active }" v-if="queryPerson" :value="queryPerson" class="relative cursor-default">
            <ul class="">
            <li class="relative cursor-pointer  select-none py-3 pl-10 pr-4" :class="{
              'bg-base-300 text-white': active,
              'text-white': !active,
            }">
              <span class="block truncate" :class="{ 'font-medium': active, 'font-normal': !active }">
                Create "{{ query }}"
              </span>
              <span v-if="selected" class="absolute inset-y-0 left-0 flex items-center pl-3"
                  :class="{ 'text-white': active, 'text-teal-600': !active }">
                  <CheckIcon class="h-5 w-5" aria-hidden="true" />
                </span>
            </li>
            </ul>
          </ComboboxOption>
        </ComboboxOptions>
      </TransitionRoot>
    </div>
  </Combobox>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import {
  Combobox,
  ComboboxInput,
  ComboboxOptions,
  ComboboxButton,
  ComboboxOption,
  TransitionRoot,
} from '@headlessui/vue'
import { CheckIcon, ChevronUpDownIcon } from '@heroicons/vue/20/solid'
import SeriesService from '@/services/SeriesService';

const items = ref([])
const props = defineProps({
  field: String,
  placeholder: String
})

let selected = ref([])

onMounted(() => {
  getSeriesFields();
});

async function getSeriesFields() {
  try {
    const response = await SeriesService.getSeriesFieldValues(
      `${props.field}`,
    );

    items.value = response.data;

    console.log(items.value);
  } catch (error) {
    console.log(error);
  }
}
let query = ref('')

const queryPerson = computed(() => {
  return query.value === '' ? null : query.value
})

let filteredItems = computed(() =>
  query.value === ''
    ? items.value
    : items.value.filter((item) =>
      item.value
        .toLowerCase()
        .replace(/\s+/g, '')
        .includes(query.value.toLowerCase().replace(/\s+/g, ''))
    )
)


</script>
