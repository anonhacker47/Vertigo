<template>
	<div class="card relative w-full h-full border bg-slate-800   text-gray-800 border-gray-700 first-letter:marker:shadow-xl">
		<RouterLink :to="{ name: 'addnew' }" class="card-body  flex-row justify-between items-center group">
			<div class="flex flex-col">
				<span class="card-title text-xl text-primary">Add New Series</span>
			</div>
			<img :src="props.icon" alt="Icon For Adding Image"
				class="absolute right-6 w-24 h-24 ml-2 pt-2 transition duration-500 ease-in-out transform group-hover:rotate-90" />
		</RouterLink>
	</div>
</template>

<script setup>
const props = defineProps({
	icon: String,
})
</script>
