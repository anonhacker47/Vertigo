<template>
    <Transition class="md:flex hidden" enter-active-class="animate__animated animate__fadeIn"
        leave-active-class="animate__animated animate__fadeOut animate__faster">
        <div class="flex flex-col md:flex-row justify-between items-center py-4 border-b bg-base-100 border-slate-700">
            <div class="flex md:flex-row justify-between gap-4 items-center container mx-auto max-w-7xl px-8">
                <RouterLink :to="{ name: `Add${pascalType}` }" custom v-slot="{ navigate }">
                    <Button class="md:flex-none" @click="navigate">
                        Add {{ pascalType }}
                    </Button>
                </RouterLink>
                <div class="flex flex-col items-center">
                    <h1 class="text-3xl font-bold text-white">{{ title }}</h1>
                    <p class="text-sm text-slate-400 mt-1">
                        Total {{ title.toLowerCase() }}: {{ pagination.base_total }}
                    </p>
                </div>
                <Button label="Delete Mode" severity="secondary" class="md:flex-none"
                    :class="{ 'p-button-danger animate-wiggle': deleteMode }" @click="toggleDelete" />
            </div>
        </div>
    </Transition> 

    <Transition class="flex md:hidden" enter-active-class="animate__animated animate__fadeIn"
        leave-active-class="animate__animated animate__fadeOut animate__faster">

        <div v-if="true"
            class="flex-col md:flex-row justify-between items-center py-4 border-b bg-base-100 border-slate-700 px-4 md:px-12 gap-4">

            <div class="flex flex-col items-center">
                <h1 class="text-3xl font-bold text-white">{{ title }}</h1>
                <p class="text-sm text-slate-400 mt-1">
                    Total {{ title.toLowerCase() }}: {{ pagination.base_total }}
                </p>
            </div>

            <CollectionDropDownMenu :getScreenWidth="getScreenWidth" :selectedGrid="selectedGrid"
                :changeGrid="changeGrid" :orderDirection="orderDirection" :orderByProperties="orderByProperties"
                v-model:viewMode="viewMode" v-model:orderBy="orderBy" v-model:orderDir="orderDir"
                v-model:itemsPerPage="pagination.limit" />
            <div class="flex flex-row items-center justify-center w-full md:w-auto gap-4 md:gap-4">
                <RouterLink :to="{ name: `Add${pascalType}` }" custom v-slot="{ navigate }">
                    <Button class="md:flex-none" @click="navigate">
                        Add {{ pascalType }}
                    </Button>
                </RouterLink>
                <Button label="Delete Mode" severity="secondary" class="md:flex-none"
                    :class="{ 'p-button-danger animate-wiggle': deleteMode }" @click="toggleDelete" />
            </div>
        </div>
    </Transition>

    <div class="flex md:flex-row flex-col items-center justify-center gap-3 w-full max-w-6xl mx-auto p-4">
        <InputText v-model="searchQuery" :placeholder="`Search ${title}...`" class="w-full md:w-52"
            @keyup.enter="applySearch" />
        <Button label="Search" icon="pi pi-search" class="p-button-info w-full md:w-32" @click="applySearch" />
        <Button v-if="isSearched" label="Reset" icon="pi pi-times" class="p-button-danger w-full md:w-32"
            @click="resetSearch" />
    </div>

    <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 py-2 gap-4 px-8 max-w-7xl mx-auto">
        <EntityListCard :delete-mode="deleteMode" @onDelete="confirmDelete(item.id, item.title)"
            v-for="item in filteredData" :key="item.id" :to="path + `/` + item.id + `-` + item.slug" :title="item.title"
            :image="thumbnail(item.id)" />
    </div>

    <div v-if="!filteredData.length && !isSearched" class="text-center text-slate-400 py-10">
        No {{ title.toLowerCase() }} found.
    </div>

    <div v-if="!filteredData.length && isSearched" class="text-center text-slate-400 py-10">
        No results match your search.
    </div>

    <Paginator v-if="pagination.total" :rows="pagination.limit" :totalRecords="pagination.total"
        :first="pagination.offset" @page="onPageChange" class="mx-auto max-w-fit py-4" />
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import InputText from "primevue/inputtext"
import Button from "primevue/button"
import Paginator from "primevue/paginator"
import { useToast } from "primevue/usetoast"
import EntityListCard from './EntityListCard.vue'
import { usePascalType } from '@/composables/usePascalType'
import { useConfirmAction } from '@/composables/useConfirmAction'

const { confirmAction } = useConfirmAction();


const props = defineProps<{
    title: string;
    type: string;
    fetch: (limit: number, offset: number, query: string) => Promise<any>;
    thumbnail: (id: number) => Promise<any>;
    onDelete: (id: number) => Promise<void>
}>();

const toast = useToast()
const searchQuery = ref('')
const isSearched = ref(false)
const items = ref<any[]>([])
const filteredData = ref<any[]>([])
const deleteMode = ref(false);

const pagination = ref({
    total: 0,
    limit: 24,
    offset: 0,
    base_total: 0
})

const toggleDelete = (): void => {
    deleteMode.value = !deleteMode.value;
};

const path = computed(() => `/${props.type}`);

const loadData = async (query = '') => {
    try {
        const result = await props.fetch(
            pagination.value.limit,
            pagination.value.offset,
            query
        )

        items.value = result.data
        filteredData.value = [...items.value]

        pagination.value = { ...result.pagination }

    } catch (err) {
        console.error(err)
        toast.add({
            severity: "error",
            summary: `Failed to Load ${props.title}`,
            detail: 'There was an issue fetching data.',
            life: 3000
        })
    }
}

onMounted(loadData)

const applySearch = async () => {
    if (!searchQuery.value.trim()) return
    isSearched.value = true
    pagination.value.offset = 0
    await loadData(searchQuery.value)
}

const resetSearch = async () => {
    searchQuery.value = ''
    isSearched.value = false
    pagination.value.offset = 0
    await loadData()
}

const onPageChange = (event: any) => {
    pagination.value.offset = event.first
    pagination.value.limit = event.rows
    loadData(searchQuery.value)
}

const pascalType = usePascalType(props.type);

const confirmDelete = (id: number, title: string) => {
    confirmAction({
        message: `${pascalType.value} ${title}`,
        header: "Confirm Deletion",
        acceptLabel: "Delete",
        severity: "danger",
        successMessage: `${pascalType.value} ${title} deleted`,
        onAccept: () => deleteIssue(id),
    });
};

const deleteIssue = async (id: number) => {
    try {
        await props.onDelete(id);
        await loadData();
        toast.add({ severity: 'success', summary: 'Success', detail: `${pascalType.value} deleted successfully!`, life: 3000 });
    } catch (error) {
        console.error(`Error creating ${pascalType}:`, error);
        toast.add({ severity: 'error', summary: 'Error', detail: error.message || `${pascalType} deletion failed.`, life: 3000 });
    }
}

</script>
