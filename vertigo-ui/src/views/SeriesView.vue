<template>
  <HeaderItem />
</template>

<style scoped>
</style>

<script setup>
import { useRoute } from 'vue-router';
import HeaderItem from '../components/HeaderItem.vue';

const route = useRoute()

console.log('The id is: ' + route.params.Id);
</script>