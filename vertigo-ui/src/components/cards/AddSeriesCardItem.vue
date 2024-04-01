<template>
	<div
		class="card relative w-full h-full border bg-slate-800   text-gray-800 border-gray-700 first-letter:marker:shadow-xl">
		<RouterLink :to="{ name: 'addnew' }" class="card-body  flex-row justify-between items-center group"
			@mouseover="isHovered = true" @mouseleave="isHovered = false">
			<div class="flex flex-col">
				<span class="card-title text-xl text-primary">Add New Series</span>

			</div>
			<div
				class="absolute right-6 w-24 h-24 ml-2 pt-2 transition duration-500 ease-in-out transform ">
				<label class="swap">
					<input type="checkbox" v-model="isHovered" />
					<img :src="addIcon" alt="Add Icon" class="swap-off w-20 h-20 group-hover:rotate-90" />
					<img :src="forwardIcon" alt="Forward Icon" class="swap-on w-20 h-20" />
				</label>
			</div>
		</RouterLink>
	</div>
</template>

<script setup>
import { ref } from 'vue'
import forwardIcon from '@/assets/forward.svg'
import addIcon from '@/assets/add.svg'

const isHovered = ref(false)

</script>
