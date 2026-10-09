<template>
    <div class="grid gap-4 md:grid-cols-2">
        <section v-for="group in groups" :key="group.label">
            <header class="mb-2 flex items-baseline justify-between gap-2">
                <h4 class="text-[13px] font-bold text-slate-400">{{ group.label }}</h4>
                <span class="text-xs font-bold tabular-nums text-slate-500">{{ group.items.length }}</span>
            </header>

            <div v-if="group.items.length" class="flex max-h-40 flex-wrap gap-1.5 overflow-y-auto pr-1">
                <span v-for="item in group.items" :key="item.key" class="fm-chip fm-chip--static">
                    {{ item.value }}
                </span>
            </div>
            <p v-else class="fm-hint">None listed on {{ source }}.</p>
        </section>

        <p v-if="note" class="fm-hint md:col-span-2">{{ note }}</p>
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
