<script setup lang="ts">
import { computed } from "vue";

import EntityCreateLayout from "@/components/entities/EntityFormLayout.vue";

import PublisherService from "@/services/PublisherService";
import CreatorService from "@/services/CreatorService";
import CharacterService from "@/services/CharacterService";

const props = defineProps<{ type: string }>();

const config = {
  publisher: {
    title: "Add Publisher",
    create: PublisherService.createPublisher,
  },
  creator: {
    title: "Add Creator",
    create: CreatorService.createCreator,
  },
  character: {
    title: "Add Character",
    create: CharacterService.createCharacter,
  },
};

const configItem = computed(() => config[props.type]);
const title = computed(() => configItem.value.title);
const create = computed(() => configItem.value.create);
</script>

<template>
  <EntityCreateLayout :key="type" :title="title" :type="props.type" mode="create" :onSubmit="create" />
</template>
