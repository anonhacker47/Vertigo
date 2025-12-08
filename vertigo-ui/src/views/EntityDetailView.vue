<template>
  <EntitiyDetailLayout :entity="entityData" :neighbours="neighbours" :thumbnail="thumbnail" :type="props.type" />
</template>

<script setup lang="ts">
import EntitiyDetailLayout from '@/components/entities/EntitiyDetailLayout.vue';
import PublisherService from '@/services/PublisherService';
import CreatorService from '@/services/CreatorService';
import CharacterService from '@/services/CharacterService';

import { Entity } from '@/types/entity.types';
import { computed, onMounted, ref, watch } from "vue";
import { useRoute } from 'vue-router';

const props = defineProps<{ type: string }>();
const route = useRoute();

const entityData = ref<Entity | null>(null);
const neighbours = ref({ previous: null, next: null });
const configItem = computed(() => services[props.type])
const thumbnail = computed(() => configItem.value.thumbnail)

// Dynamic service selector
const services = {
  publisher: {
    fetch: PublisherService.getPublisherById,
    neighbors: PublisherService.getPublisherNeighbours,
    thumbnail: PublisherService.getPublisherImageById
  },
  creator: {
    fetch: CreatorService.getCreatorById,
    neighbors: CreatorService.getCreatorNeighbours,
    thumbnail: CreatorService.getCreatorImageById
  },
  character: {
    fetch: CharacterService.getCharacterById,
    neighbors: CharacterService.getCharacterNeighbours,
    thumbnail: CharacterService.getCharacterImageById
  },
};


async function loadEntity() {
  const id = Number(route.params.Id);
  const service = services[props.type];

  if (!service) return;

  try {
    // Fetch main entity
    const response = await service.fetch(id);
    entityData.value = response;

    // Fetch neighbors
    const resNeighbours = await service.neighbors(id);
    neighbours.value = resNeighbours.data || { previous: null, next: null };
  } catch (err) {
    console.error(err);
  }
}

onMounted(loadEntity);

watch(
  () => route.fullPath,
  () => loadEntity()
);
</script>
