<script setup lang="ts">
import EntitiyListLayout from "@/components/entities/EntitiyListLayout.vue"
import PublisherService from "@/services/PublisherService"
import CreatorService from "@/services/CreatorService"
import CharacterService from "@/services/CharacterService"
import { computed } from "vue";

const props = defineProps<{ type: string }>()

const config = {
  publisher: {
    title: "Publishers",
    fetch: PublisherService.fetchPublishers,
    thumbnail: PublisherService.getPublisherImageById,
    delete: PublisherService.deletePublisher
  },
  creator: {
    title: "Creators",
    fetch: CreatorService.fetchCreators,
    thumbnail: CreatorService.getCreatorImageById,
    delete: CreatorService.deleteCreator,
  },
  character: {
    title: "Characters",
    fetch: CharacterService.fetchCharacters,
    thumbnail: CharacterService.getCharacterImageById,
    delete: CharacterService.deleteCharacter,
  },
}

const configItem = computed(() => config[props.type])
const title = computed(() => configItem.value.title)
const fetch = computed(() => configItem.value.fetch)
const thumbnail = computed(() => configItem.value.thumbnail)
const deleteFn = computed(() => configItem.value.delete)
</script>

<template>
  <EntitiyListLayout :key="type" :onDelete="deleteFn" :title="title" :thumbnail="thumbnail" :type="props.type" :fetch="fetch" />
</template>
