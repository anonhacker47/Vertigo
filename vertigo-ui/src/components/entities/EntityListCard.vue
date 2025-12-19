<template>
    <RouterLink :to="to" :class="deleteMode ? 'animate animate-wiggle' : ' '"
        class="bg-base-200 rounded-xl shadow-md hover:shadow-xl transition-all flex flex-col justify-between border border-slate-700">

        <!-- IMAGE WRAPPER -->
        <div class="w-full flex items-center rounded-t-xl justify-center bg-base-300 h-80 overflow-hidden">
            <img v-if="image && !imgError" loading="lazy" decoding="async" :src="image" @error="imgError = true"
                class="object-cover max-h-full w-full" />
            <div v-else class="w-full flex items-center justify-center h-full">
                <ImagePlaceHolderItem :title="title" size="lg" />
            </div>
        </div>

        <!-- TEXT -->
        <div class="p-4 text-center">
            <h2 class="text-lg font-semibold text-white truncate">
                {{ title }}
            </h2>
        </div>

        <div v-if="deleteMode" @click.stop.prevent="$emit('onDelete')"
            class="absolute -top-3 -right-3 rounded hover:scale-105 hover:rotate-180 z-[800] transition ease-in-out">
            <img src="@/assets/remove.svg" alt="" height="30" width="30" class="min-w-[25px] min-h-[25px]" />
        </div>

    </RouterLink>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import ImagePlaceHolderItem from '../cards/ImagePlaceHolderItem.vue';

const props = defineProps<{
    title: string
    image: string | Promise<string> | null
    to: string | Record<string, any>
    deleteMode: boolean
}>()

const imgError = ref(false)
</script>
