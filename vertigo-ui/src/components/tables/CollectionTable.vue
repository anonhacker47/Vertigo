<template>
	<DataTable class="" :value="cards" :paginator="true" :rows="10">
		<Column field="image_url" header="Image">
			<template #body="{ data }">
				<img :src="SeriesService.getImagebyId(data.id)" class="h-30 w-20" />
			</template>
		</Column>
		<Column field="title" header="Title" />
		<Column field="series_format" header="Format" />
		<Column field="timestamp" header="Date Added" />
		<Column field="rating" header="Rating">
			<template #body="{ data }">
				<Rating :modelValue="data.rating" :readonly="true" :stars="5" :cancel="false" />
			</template>
		</Column>
		<Column field="owned_count" header="Owned Count" />
		<Column field="read_count" header="Read Count" />
	</DataTable>
</template>
  

<script setup>
import DataTable from 'primevue/datatable';
import Column from 'primevue/column';
import { ref, defineProps } from 'vue';
import SeriesService from '../../services/SeriesService';
import Rating from 'primevue/rating'

const props = defineProps({
	cards: {
		type: Array,
		required: true
	}
})

</script>
