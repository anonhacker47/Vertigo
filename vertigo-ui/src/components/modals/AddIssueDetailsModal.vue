<template>
	<Dialog v-model:visible="modalRef" modal header="Add Series" :style="{ width: '30rem' }">
	  <span class="text-surface-500 dark:text-surface-400 block mb-4">
		Configure your series details below.
	  </span>
  
	  <div class="mb-4">
		<label for="title" class="font-semibold block mb-1">Series Title</label>
		<InputText id="title" v-model="seriesData.title" class="w-full" autocomplete="off" disabled />
	  </div>
  
	  <div class="flex justify-between mb-2">
		<label>
		  <input type="checkbox" v-model="readAll" @change="toggleReadAll" /> Read All
		</label>
		<label>
		  <input type="checkbox" v-model="ownedAll" @change="toggleOwnedAll" /> Owned All
		</label>
	  </div>
  
	  <div v-for="(issue, index) in issues" :key="index" class="flex items-center gap-2 border p-2 rounded my-1">
		<input v-model="issue.title" class="border p-1 flex-grow" :placeholder="'Issue ' + (index + 1)" />
		<input type="checkbox" v-model="issue.read" />
		<input type="checkbox" v-model="issue.owned" />
		<button @click="removeIssue(index)" class="bg-red-500 text-white p-1 rounded">✕</button>
	  </div>
  
	  <button @click="addIssue" class="bg-green-500 text-white p-2 rounded mt-2 w-full">Add Issue</button>
  
	  <div class="flex justify-end gap-2 mt-4">
		<Button type="button" label="Cancel" severity="secondary" @click="modalRef = false"></Button>
		<Button type="button" label="Save" @click="saveSeries"></Button>
	  </div>
	</Dialog>
  </template>
  
  <script setup lang="ts">
  import { defineProps, watch, ref, reactive } from "vue";
  
  const modalRef = defineModel<boolean>('modalRef', { required: true });
  
  const props = defineProps({
	seriesData: Object
  });
  

  </script>
  