<template>
	<DataTable class="mt-5 rounded-lg rounded-table" :value="cards" @row-click="navigate"  rowHover showGridlines :rows="10">
		<Column field="Series" header="Series" >
			<template #body="{ data }">
					<div class="flex items-center max-w-xs gap-4">
						<img :src="SeriesService.getImagebyId(data.id)" class="h-20 w-25 ml-2 rounded-lg"
							alt="Series Thumbnail" />
						<span class="text-large font-extrabold overflow-hidden whitespace-nowrap text-ellipsis">{{ data.title }}</span>
					</div>
			</template>
		</Column>
		<Column field="publisher" header="Publisher">
			<template #body="{ data }">
				<div class="flex justify-center">
					{{ data.publisher }}
				</div>
			</template>
		</Column>
		<Column field="series_format" header="Format">
			<template #body="{ data }">
				<div class="flex justify-center">
					{{ data.series_format }}
				</div>
			</template>
		</Column>
		<Column field="timestamp" header="Date Added">
			<template #body="{ data }">
				<div class="flex justify-center">
					{{ new Date(data.timestamp).toLocaleDateString('en-US', { day: 'numeric', month: 'long', year: 'numeric' }) }}
				</div>
			</template>
		</Column>
		<Column field="rating" header="Rating">
			<template #body="{ data }">
				<div class="flex justify-center">
					<Rating :modelValue="data.user_rating" readonly disabled :stars="5" :cancel="false" />
				</div>
			</template>
		</Column>
		<Column field="owned_count" header="Owned/Books" :bodyStyle="{ 'text-align': 'center' }">
			<template #body="{ data }">
				{{ data.owned_count+'/'+data.issue_count }}
			</template>
		</Column>
		<Column field="read_count" header="Read/Books" :bodyStyle="{ 'text-align': 'center' }">
			<template #body="{ data }">
				{{ data.read_count+'/'+data.issue_count }}
			</template>
		</Column>
		<Column headerStyle="width: 5rem" bodyClass="text-center" header="Actions" v-if="deleteMode">
			<template #body="{ data }">
				<div class="flex justify-center">
					<button class="p-button-rounded p-button-danger p-button-text" @click="confirmDelete(data.id,data.title)"><i class="pi pi-trash text-red-500 hover:cursor-pointer"/></button>
				</div>
			</template>
		</Column>
	</DataTable>
</template>
  

<script setup>
import DataTable from 'primevue/datatable';
import Column from 'primevue/column';
import { ref, defineProps } from 'vue';
import { useRouter } from 'vue-router';
import SeriesService from '../../services/SeriesService';
import Rating from 'primevue/rating'
import 'primeicons/primeicons.css'


const props = defineProps({
	cards: {
		type: Array,
		required: true
	},
	deleteMode: {
		type: Boolean,
		required: true
	},
	confirmDelete: {
		type: Function,
		required: true
	}
})

const router = useRouter();

const navigate = (event) => {
	const data = event.data;
	router.push({
		name: 'series',
		params: { Link: data.slug, Id: data.id },
		id: data.id,
	});
};

</script>

<style>
.p-datatable-column-header-content{
	justify-content: center !important;
}

.p-datatable .p-datatable-tbody > tr:hover {
	cursor: pointer;
}
.rounded-table {
	border-radius: 10px;
	overflow: hidden; /* Ensure content does not overflow the rounded corners */
}

/* Optional: Apply border and box shadow for better visibility */
.rounded-table .p-datatable {
	border-radius: 10px;
	box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

.rounded-table .p-datatable .p-datatable-tbody > tr {
	border-radius: 10px;
}

.rounded-table .p-datatable thead th {
	border-radius: 10px 10px 0 0;
}

.rounded-table .p-datatable tbody tr:last-child td {
	border-radius: 0 0 10px 10px;
}
</style>