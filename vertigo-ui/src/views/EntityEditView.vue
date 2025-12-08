<script setup lang="ts">
import { computed, onMounted, ref } from "vue";

import EntityFormLayout from "@/components/entities/EntityFormLayout.vue";

const props = defineProps<{ type: string }>();
const route = useRoute();

const entity = ref(null);

import PublisherService from "@/services/PublisherService";
import CreatorService from "@/services/CreatorService";
import CharacterService from "@/services/CharacterService";
import { useRoute } from "vue-router";

const config = {
  publisher: {
    title: "Add Publisher",
    update: PublisherService.updatePublisher,
    fetch: PublisherService.getPublisherById,
    thumbnail: PublisherService.getPublisherImageById,
    delete: PublisherService.deletePublisher
  },
  creator: {
    title: "Add Creator",
    update: CreatorService.updateCreator,
    fetch: CreatorService.getCreatorById,
    thumbnail: CreatorService.getCreatorImageById,
    delete: CreatorService.deleteCreator,

  },
  character: {
    title: "Add Character",
    create: CharacterService.createCharacter,
    fetch: CharacterService.getCharacterById,
    update: CharacterService.updateCharacter,
    thumbnail: CharacterService.getCharacterImageById,
    delete: CharacterService.deleteCharacter,
  },
};

const configItem = computed(() => config[props.type]);
const title = computed(() => configItem.value.title);
async function load() {
  try {
    const response = await config[props.type].fetch(Number(route.params.Id));
    entity.value = response;
    entity.value.thumbnail = `${config[props.type].thumbnail(Number(route.params.Id))}`
    // Fetch neighbors
  } catch (err) {
    console.error(err);
  }
}

onMounted(load);

const updateEntity = (fd: FormData) =>
  config[props.type].update(Number(route.params.Id), fd);

const deleteEntity = () =>
  config[props.type].delete(Number(route.params.Id));  
</script>

<template>
  <EntityFormLayout :key="type" :title="title" :initial="entity" :type="props.type" mode="edit" :onSubmit="updateEntity"
    :onDelete="deleteEntity" />
</template>
