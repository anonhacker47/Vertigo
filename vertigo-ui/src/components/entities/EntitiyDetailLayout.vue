<template>
  <div v-if="entity" class="min-w-screen h-full bg-no-repeat bg-center bg-cover"
    :style="{ backgroundImage: backgroundStyle }">

    <div class="flex flex-col h-full">

      <!-- Top Section -->
      <div class="relative py-6 px-6 border-b border-slate-700">

        <!-- Previous -->
        <RouterLink v-if="neighbours.previous" :to="`/${type}/${neighbours.previous.id}-${neighbours.previous.slug}`"
          class="absolute left-6 top-1/2 -translate-y-1/2 px-4 py-2 capitalize-first bg-slate-800 rounded-md font-bold hover:bg-slate-700 transition flex items-center gap-2">
          <i class="pi pi-chevron-left"></i>
          <span>Previous {{ pascalType }}</span>
        </RouterLink>

        <!-- Next -->
        <RouterLink v-if="neighbours.next" :to="`/${type}/${neighbours.next.id}-${neighbours.next.slug}`"
          class="absolute right-6 top-1/2 -translate-y-1/2 px-4 py-2 capitalize-first bg-slate-800 rounded-md font-bold hover:bg-slate-700 transition flex items-center gap-2">
          <span>Next {{ pascalType }}</span>
          <i class="pi pi-chevron-right"></i>
        </RouterLink>

        <div class="flex w-full items-center justify-center gap-4 ml-6">
          <p class="font-bold text-3xl text-primary text-center truncate">
            {{ entity.title }}
          </p>
          <RouterLink :to="editLink"
            class="cursor-pointer w-12 h-12 transition hover:scale-110 hover:border-emerald-400 hover:border-2 rounded-full flex items-center justify-center">
            <EditIcon class="w-7 h-7 fill-slate-300" />
          </RouterLink>
        </div>


      </div>


      <!-- Main Content -->
      <div class="flex flex-col md:flex-row p-8 gap-8 grow">

        <!-- Left: Thumbnail -->
        <div class="flex flex-col w-fit justify-center border-primary h-80 items-center">
          <div class="flex flex-col border-2 rounded-lg justify-center border-primary h-80 w-60 items-center">
            <img v-if="entity.thumbnail" :src="thumbnail(entity.id)" alt=""
              class="rounded-lg  object-cover max-h-full w-full  m-4" />

            <div v-else
              class="w-60 h-80 rounded-lg text-wrap truncate bg-slate-900 flex items-center justify-center p-4 text-center">
              <span class="text-3xl text-primary font-semibold opacity-60">
                {{ entity.title }}
              </span>
            </div>

          </div>
          <p class="mt-4 text-sm text-center text-slate-400">
            Added on: {{ formatDate(entity.timestamp) }}
          </p>
        </div>

        <!-- Right: Description -->
        <div class="flex flex-col md:w-2/3">
          <p class="text-2xl font-bold text-primary text-center md:text-left">
            Description
          </p>

          <p v-if="entity.description" class="mt-4 text-white text-justify leading-relaxed">
            {{ entity.description }}
          </p>

          <p v-else class="mt-4 text-slate-500 italic text-center md:text-left">
            No description available.
          </p>
          <div v-if="entity.series_count !== undefined"
            class="mt-8 p-4 bg-slate-800 border w-48 border-slate-700 rounded-lg flex flex-col items-center">

            <p class="text-xl font-bold text-primary mb-1">
              Series Count
            </p>

            <p class="text-white text-lg font-semibold">
              {{ entity.series_count }}
            </p>

          </div>
          <RouterLink v-if="entity.series_count > 0" :to="`/series?${type}=${entity.id}`"
            class="px-3 py-2 my-3 bg-primary w-48 text-center text-black font-bold rounded-md hover:bg-emerald-400 transition text-sm">
            View Series List
          </RouterLink>
        </div>

      </div>

    </div>

  </div>
</template>

<script setup lang="ts">
import { usePascalType } from "@/composables/usePascalType";
import { Entity } from "@/types/entity.types";
import { computed } from "vue";
import EditIcon from "@/assets/EditIcon.vue";

// --- Props ---
const props = defineProps<{
  entity: Entity;        // Replace with your Entity type if available
  type: string;
  thumbnail: (id: number) => Promise<any>;
  neighbours?: {
    previous: any | null;
    next: any | null;
  };
}>();

const neighbours = computed(() => props.neighbours ?? { previous: null, next: null });

const backgroundStyle = computed(() =>
  props.entity?.thumbnail ? `url(${props.entity.thumbnail})` : "none"
);

const editLink = computed(() => ({
  name: `${pascalType.value}Edit`,
  params: {
    Id: props.entity.id,
    Link: props.entity.slug || props.entity.title.replace(/\s+/g, "-")
  }
}));

function formatDate(val: string | null | undefined) {
  if (!val) return "";
  return new Date(val).toLocaleDateString();
}


const pascalType = usePascalType(props.type);
</script>

<style scoped>
.capitalize-first::first-letter {
  text-transform: uppercase;
}
</style>