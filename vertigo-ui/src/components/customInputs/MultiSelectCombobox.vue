<template>
  <Combobox v-model="model" multiple>
    <div class="relative">
      <div class="relative w-full cursor-default rounded-lg bg-base-10">
        <ComboboxInput class="w-full input input-bordered" autoComplete="off" @change="query = $event.target.value"
        :placeholder="placeholder" />
        <ComboboxButton class="absolute inset-y-0 right-0 flex items-center pr-2">
          <ChevronUpDownIcon class="h-5 w-5 text-gray-400" aria-hidden="true" />
        </ComboboxButton>
      </div>
      <div v-if="model.length > 0" class="flex flex-col justify-center items-center h-16 w-full">
        <div v-for="(person, i) in model" :key="i" class="flex items-center justify-center mr-1 mb-1 bg-base-600 rounded-md">
          <span class="text-white text-xs">{{ person }}</span>
          <button type="button" class="ml-1 focus:outline-none" @click="removePerson(person)">
            <span class="text-white">X</span>
          </button>
        </div>
    </div>
      <TransitionRoot leave="transition ease-in duration-100" leaveFrom="opacity-100" leaveTo="opacity-0"
        @after-leave="query = ''">
        <ComboboxOptions
          class="absolute mt-1 max-h-60 w-full overflow-auto rounded-md bg-base-100 py-1 shadow-lg ring-1 ring-black/5 focus:outline-none sm:text-sm"
          style="z-index: 1;">
          <ComboboxOption v-for="person in filteredPeople" as="template" :key="person.id" :value="person.value"
            v-slot="{ active }">
            <li class="relative cursor-default select-none py-3 pl-10 pr-4" :class="{
              'bg-base-300 text-white': active,
              'text-white': !active,
            }">
              <span class="block truncate" :class="{ 'font-medium': active, 'font-normal': !active }">
                {{ person.value }}
              </span>
              <!-- <span v-if="model" class="absolute inset-y-0 left-0 flex items-center pl-3"
                :class="{ 'text-white': active, 'text-teal-600': !active }">
                <CheckIcon class="h-5 w-5" aria-hidden="true" />
              </span> -->
            </li>
          </ComboboxOption>
          <ComboboxOption v-slot="{ active }" v-if="queryPerson" :value="queryPerson" class="relative cursor-default">
            <li class="relative cursor-default select-none py-3 pl-10 pr-4" :class="{
              'bg-base-300 text-white': active,
              'text-white': !active,
            }">
              <span class="block truncate" :class="{ 'font-medium': active, 'font-normal': !active }">
                Create "{{ query }}"
              </span>
              <!-- <span v-if="model" class="absolute inset-y-0 left-0 flex items-center pl-3"
                :class="{ 'text-white': active, 'text-teal-600': !active }">
                <CheckIcon class="h-5 w-5" aria-hidden="true" />
              </span> -->
            </li>
          </ComboboxOption>
        </ComboboxOptions>
      </TransitionRoot>
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
import { CheckIcon, ChevronUpDownIcon } from '@heroicons/vue/20/solid'
import SeriesService from '@/services/SeriesService';

const people = ref("")
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

    people.value = response.data;

    console.log(people.value);
  } catch (error) {
    console.log(error);
  }
}
let query = ref('')

const queryPerson = computed(() => {
  return query.value === '' ? null : query.value
})

let filteredPeople = computed(() =>
  query.value === ''
    ? people.value
    : people.value.filter((person) =>
      person.value
        .toLowerCase()
        .replace(/\s+/g, '')
        .includes(query.value.toLowerCase().replace(/\s+/g, ''))
    )
)

const removePerson = (person) => {
  model.value = model.value.filter(p => p !== person);
  console.log("model: ", model.value);
}

</script>
