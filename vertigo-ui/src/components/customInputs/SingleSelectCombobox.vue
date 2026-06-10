<template>
  <div class="relative w-full">
    <input
      v-model="query"
      class="input input-bordered w-full"
      :placeholder="localSelected?.value || placeholder"
      @focus="open = true"
      @input="open = true" 
      @keydown.enter.prevent="handleEnter"
      @blur="onBlur"
      autocomplete="off"
    />

    <ul
      v-if="open && (filteredItems.length || (query.trim() && !exactMatch))"
      class="absolute mt-1 max-h-60 w-full overflow-auto rounded-md bg-base-100 py-1 shadow-lg z-10"
    >
      <li
        v-for="item in filteredItems"
        :key="item.id"
        @mousedown.prevent="selectItem(item)"
        class="cursor-pointer px-4 py-2 hover:bg-base-300 flex items-center gap-2"
      >
        <CheckIcon v-if="localSelected?.value === item.value" class="h-4 w-4 text-teal-400" />
        {{ item.value }}
      </li>
      <li
        v-if="query.trim() && !exactMatch"
        @mousedown.prevent="addCustom"
        class="cursor-pointer px-4 py-2 hover:bg-base-300 text-sm italic"
      >
        Create "{{ query.trim() }}"
      </li>
    </ul>
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
  modelValue: Item | null
}>()

const emit = defineEmits<{ (e: 'update:modelValue', val: Item | null): void }>()

const query = ref('')
const open = ref(false)
const localSelected = ref<Item | null>(props.modelValue)
const localItems = ref<Item[]>([...props.items])

watch(() => props.modelValue, (val) => { localSelected.value = val })
watch(() => props.items, (val) => { localItems.value = [...val] })

const normalize = (s: string) => s.trim().toLowerCase()

const filteredItems = computed(() =>
  query.value === ''
    ? localItems.value
    : localItems.value.filter(i => normalize(i.value).includes(normalize(query.value)))
)

const exactMatch = computed(() =>
  localItems.value.some(i => normalize(i.value) === normalize(query.value))
)

const selectItem = (item: Item) => {
  localSelected.value = item
  emit('update:modelValue', item)
  query.value = ''
  open.value = false
}

const addCustom = () => {
  const val = query.value.trim()
  if (!val) return
  const key = normalize(val)
  const item = { id: `custom:${key}`, value: val }
  if (!localItems.value.find(i => normalize(i.value) === key)) localItems.value.push(item)
  selectItem(item)
}

const handleEnter = () => {
  if (!open.value) {
    open.value = true
    return
  }

  if (query.value.trim() && !exactMatch.value) {
    addCustom()
  } else if (filteredItems.value.length > 0) {
    selectItem(filteredItems.value[0])
  }
}

const onBlur = () => setTimeout(() => { open.value = false; query.value = '' }, 150)
</script>