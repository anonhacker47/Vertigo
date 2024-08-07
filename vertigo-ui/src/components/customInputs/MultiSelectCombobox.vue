<template>
  <Combobox v-model="model" multiple>
    <div class="relative w-52">
      <div class="relative w-full cursor-default rounded-lg bg-base-10">
        <ComboboxInput class="w-full input input-bordered" autoComplete="off" @change="query = $event.target.value"
          :placeholder="selectedValuesPlaceholder" />
        <ComboboxButton class="absolute inset-y-0 right-0 flex items-center pr-2">
          <ChevronUpDownIcon class="h-5 w-5 text-gray-400" aria-hidden="true" />
        </ComboboxButton>
      </div>
      <TransitionRoot leave="transition ease-in duration-100" leaveFrom="opacity-100" leaveTo="opacity-0"
        @after-leave="query = ''">
        <ComboboxOptions
          class="absolute mt-1 max-h-60 w-full dropdown-content overflow-auto rounded-md bg-base-100 py-1 shadow-lg ring-2 ring-gray-400/5 focus:outline-none sm:text-sm"
          style="z-index: 1;">
          <ComboboxOption v-for="item in filteredItems" as="template" :key="item.id" :value="item.value"
            v-slot="{ active, selected }">
            <ul class="">
              <li class="relative cursor-pointer select-none py-3 pl-10 pr-4" :class="{
                'bg-base-300 text-teal-400': active,
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
          <ComboboxOption v-slot="{ active, selected }" v-if="queryItem" :value="queryItem" @click="addCustomItem(queryItem)" class="relative cursor-pointer">
            <ul>
              <li class="relative cursor-default select-none py-3 pl-10 pr-4" :class="{
                'bg-base-300 text-white': active,
                'text-white': !active,
              }">
                <span class="block truncate" :class="{ 'font-medium': active, 'font-normal': !active }">
                  {{ query }}
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
      <div class="flex flex-wrap justify-center mt-2 gap-2 h-12 overflow-auto">
        <div v-for="(item, i) in model" :key="i" class="badge badge-info p-0 bg-base-600  rounded-md">
          <span class="text-white text-xs px-2 py-1">{{ item }}</span>
          <button type="button" class="ml-1 focus:outline-none self-center" @click="removeItem(item)">
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"
              class="inline-block h-4 w-4 stroke-current">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
            </svg>
          </button>
        </div>
      </div>
    </div>
  </Combobox>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import {
  Combobox,
  ComboboxInput,
  ComboboxButton,
  ComboboxOptions,
  ComboboxOption,
  TransitionRoot,
} from '@headlessui/vue'
import { CheckIcon, ChevronUpDownIcon,TrashIcon } from '@heroicons/vue/20/solid'
import SeriesService from '@/services/SeriesService';

const items = ref("")
const props = defineProps({
  field: String,
  placeholder: String
})

const model = defineModel({
  type: Array,
  default: []
})

onMounted(() => {
  getSeriesFields();
});


async function getSeriesFields() {
  try {
    const response = await SeriesService.getSeriesFieldValues(
      `${props.field}`,
    );

    items.value = response.data;

    console.log("items2multiple",items.value);
  } catch (error) {
    console.log(error);
  }
}
let query = ref('')

const queryItem = computed(() => {
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

const selectedValuesPlaceholder = computed(() => {
  return model.value.length > 0 ? model.value.join(', ') : props.placeholder;
})

const removeItem = (item) => {
  model.value = model.value.filter(p => p !== item);
  console.log("model: ", model.value);
}

const addCustomItem = (value) => {
  if (!items.value.find(item => item.value === value)) {
    items.value.push({ id: value, value: value });
  }
  if (!model.value.includes(value)) {
    model.value.push(value);
  }
  query.value = '';
}
</script>
