<template>
  <main class="min-h-screen w-full pb-20">
    <UpNextHero />
    <ReadingQueueShelf />
    <GetNextShelf />
    <HabitsSection />
    <RecordsSection />
    <FactsSection />
  </main>
</template>

<script setup lang="ts">
import UpNextHero from "@/components/insights/UpNextHero.vue";
import ReadingQueueShelf from "@/components/insights/ReadingQueueShelf.vue";
import GetNextShelf from "@/components/insights/GetNextShelf.vue";
import HabitsSection from "@/components/insights/HabitsSection.vue";
import RecordsSection from "@/components/insights/RecordsSection.vue";
import FactsSection from "@/components/insights/FactsSection.vue";
</script>
