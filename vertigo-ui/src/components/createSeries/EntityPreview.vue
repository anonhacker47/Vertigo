<template>
    <div class="grid gap-4 md:grid-cols-2">
        <section v-for="group in groups" :key="group.label" class="rounded-xl border border-base-300 p-4">
            <header class="mb-3 flex items-baseline justify-between gap-2">
                <h4 class="text-sm font-semibold">{{ group.label }}</h4>
                <span class="text-xs tabular-nums opacity-60">{{ group.items.length }}</span>
            </header>

            <div v-if="group.items.length" class="flex max-h-40 flex-wrap gap-2 overflow-y-auto pr-1">
                <span v-for="item in group.items" :key="item.key"
                    class="rounded-md border border-base-300 bg-base-200 px-2.5 py-1 text-sm leading-tight">
                    {{ item.value }}
                </span>
            </div>
            <p v-else class="text-sm opacity-60">None listed on {{ source }}.</p>
        </section>

        <p v-if="note" class="text-xs opacity-60 md:col-span-2">{{ note }}</p>
    </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Entity {
    value: string
    metron_id?: number
    mal_id?: number
}

const props = defineProps<{
    creators: Entity[] | undefined
    characters: Entity[] | undefined
    creatorsLabel: string
    source: string
    note?: string
}>()

function keyed(items: Entity[] | undefined) {
    return (items || []).map((e, i) => ({ value: e.value, key: e.metron_id ?? e.mal_id ?? `${e.value}-${i}` }))
}

const groups = computed(() => [
    { label: props.creatorsLabel, items: keyed(props.creators) },
    { label: 'Characters', items: keyed(props.characters) },
])
</script>
