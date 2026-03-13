<template>
  <div class="relative w-full">
    <div class="flex items-center gap-2">
      <input
        v-model="query"
        class="input input-bordered w-full"
        :placeholder="selectedValuesPlaceholder"
        @keydown.enter.prevent="handleEnter"
        @focus="open = true"
        @blur="onBlur"
        autocomplete="off"
      />
    </div>

    <ul
      v-if="open && filteredItems.length"
      class="absolute mt-1 max-h-60 w-full overflow-auto rounded-md bg-base-100 py-1 shadow-lg z-10"
    >
      <li
        v-for="item in filteredItems"
        :key="item.id"
        @mousedown.prevent="toggleItem(item)"
        class="cursor-pointer px-4 py-2 hover:bg-base-300 flex items-center gap-2"
      >
        <CheckIcon v-if="isSelected(item)" class="h-4 w-4 text-teal-400" />
        <span :class="isSelected(item) ? 'text-teal-400' : ''">{{ item.value }}</span>
      </li>
      <li
        v-if="query.trim() && !exactMatch"
        @mousedown.prevent="addCustom"
        class="cursor-pointer px-4 py-2 hover:bg-base-300 text-sm italic"
      >
        Create "{{ query.trim() }}"
      </li>
    </ul>

    <div v-if="localSelected.length" class="flex flex-wrap mt-2 gap-2">
      <div
        v-for="item in localSelected"
        :key="item.id"
        class="badge badge-info rounded-md flex items-center gap-1 px-2 py-1"
      >
        <span class="text-xs">{{ item.value }}</span>
        <button type="button" @click="removeItem(item)">
          <svg class="h-3 w-3 stroke-current" viewBox="0 0 24 24" fill="none">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { CheckIcon } from '@heroicons/vue/20/solid'

type Item = { id: any; value: string }

const props = defineProps<{
  field?: string
  placeholder?: string
  items: Item[]
  modelValue: Item[]
}>()

const emit = defineEmits<{ (e: 'update:modelValue', val: Item[]): void }>()

const query = ref('')
const open = ref(false)
const localSelected = ref<Item[]>([...props.modelValue])
const localItems = ref<Item[]>([...props.items])

// Only sync in when parent value actually changes (e.g. form reset)
watch(() => props.modelValue, (val) => { localSelected.value = [...val] })
watch(() => props.items, (val) => { localItems.value = [...val] })

const normalize = (s: string) => s.trim().toLowerCase()

const filteredItems = computed(() =>
  query.value === ''
    ? localItems.value
    : localItems.value.filter(i =>
        normalize(i.value).includes(normalize(query.value))
      )
)

const exactMatch = computed(() =>
  localItems.value.some(i => normalize(i.value) === normalize(query.value))
)

const selectedValuesPlaceholder = computed(() =>
  localSelected.value.length ? localSelected.value.map(i => i.value).join(', ') : props.placeholder
)

const isSelected = (item: Item) =>
  localSelected.value.some(i => normalize(i.value) === normalize(item.value))

const toggleItem = (item: Item) => {
  if (isSelected(item)) {
    removeItem(item)
  } else {
    const next = [...localSelected.value, item]
    localSelected.value = next
    emit('update:modelValue', next)
  }
  query.value = ''
}

const removeItem = (item: Item) => {
  const next = localSelected.value.filter(i => normalize(i.value) !== normalize(item.value))
  localSelected.value = next
  emit('update:modelValue', next)
}

const addCustom = () => {
  const val = query.value.trim()
  if (!val) return
  const key = normalize(val)
  const item = localItems.value.find(i => normalize(i.value) === key) ?? { id: `custom:${key}`, value: val }
  if (!localItems.value.find(i => normalize(i.value) === key)) localItems.value.push(item)
  if (!isSelected(item)) toggleItem(item)
  else query.value = ''
}

const handleEnter = () => {
  if (filteredItems.value.length === 1) toggleItem(filteredItems.value[0])
  else if (query.value.trim()) addCustom()
}

const onBlur = () => setTimeout(() => { open.value = false; query.value = '' }, 150)
</script>