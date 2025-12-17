<!-- components/createSeries/IssueSection.vue -->
<template>
    <div v-if="showIssueSection"
        class="card h-full w-full md:w-2/3 flex flex-col gap-6 shadow-2xl bg-base-100 p-8">
        <!-- Issue Count Input -->
        <div class="">
            <label class="label" for="issue-count">Number of Issues</label>
            <input id="issue-count" type="number" v-model.number="seriesData.issue_count" min="1" class="input input-bordered" />
        </div>

        <!-- Select All Toggles -->
        <div class="flex flex-col md:flex-row gap-4 md:gap-16 justify-around">
            <div class=" w-full">
                <label class="label cursor-pointer flex items-center gap-2"
                    :class="haveAll ? 'text-primary' : 'text-white'">
                    <span>Have All?</span>
                    <input type="checkbox" v-model="haveAll" @change="toggleAll('have')" class="checkbox"
                        :class="haveAll ? 'checkbox-primary' : ''" />
                </label>
            </div>
            <div class=" w-full">
                <label class="label cursor-pointer flex items-center gap-2"
                    :class="readAll ? 'text-accent' : 'text-white'">
                    <span>Read Already?</span>
                    <input type="checkbox" v-model="readAll" @change="toggleAll('read')" class="checkbox"
                        :class="readAll ? 'checkbox-accent' : ''" />
                </label>
            </div>
        </div>

        <!-- Issue Cards -->
        <div class="grid place-items-center w-full md:gap-6 md:max-h-[28rem] overflow-y-auto overflow-x-hidden"
            style="grid-template-columns: repeat(auto-fill, minmax(11rem, 1fr)); gap: 1rem;">
            <div v-for="n in seriesData.issue_count" :key="n"
                class="relative card border w-full md:w-fit shadow-md rounded-md flex flex-col items-center"
                :class="{ 'border-primary': issues[n - 1].have, 'border-accent': issues[n - 1].read }">
                <div class="relative w-full md:h-52 h-40">
                    <img :src="imagesrc" alt="Issue Thumbnail"
                        class="w-full h-full object-cover rounded-md brightness-80 hover:brightness-100 transition duration-300" />
                    <p
                        class="absolute inset-0 flex items-center justify-center text-white text-3xl font-bold bg-black/50 rounded-md">
                        #{{ n }}</p>
                </div>
                <div class="flex w-full justify-around gap-2 text-sm md:text-md md:gap-4 p-4">
                    <label class="cursor-pointer flex items-center gap-2"
                        :class="issues[n - 1].have ? 'text-primary' : 'text-white'">
                        <span>Have</span>
                        <input type="checkbox" v-model="issues[n - 1].have" class="checkbox"
                            :class="issues[n - 1].have ? 'checkbox-primary' : ''" />
                    </label>
                    <label class="cursor-pointer flex items-center gap-2"
                        :class="issues[n - 1].read ? 'text-green-500' : 'text-white'">
                        <span>Read</span>
                        <input type="checkbox" v-model="issues[n - 1].read" class="checkbox"
                            :class="issues[n - 1].read ? 'checkbox-accent' : ''" />
                    </label>
                </div>

                <div class="flex flex-col w-full pb-4 px-4 gap-2 text-sm md:text-md"
                    v-if="issues[n - 1].have || issues[n - 1].read">
                    <label class="flex flex-col" v-if="issues[n - 1].have">
                        <span class="text-white">Purchase Date</span>
                        <input type="date" v-model="issues[n - 1].purchaseDate" class="input input-bordered w-full" />
                    </label>
                    <label class="flex flex-col" v-if="issues[n - 1].read">
                        <span class="text-white">Read Date</span>
                        <input type="date" v-model="issues[n - 1].readDate" class="input input-bordered w-full" />
                    </label>
                    <label class="flex flex-col" v-if="issues[n - 1].have">
                        <span class="text-white">Price</span>
                        <input type="number" v-model="issues[n - 1].price" class="input input-bordered w-full"
                            step="0.01" />
                    </label>
                </div>
            </div>
        </div>

        <div class="flex justify-between mt-6">
            <button class="btn btn-danger" @click="$emit('cancel')">Go Back / Cancel</button>
            <button class="btn btn-primary" :disabled="seriesData.issue_count < 1" @click.prevent="$emit('submit')">Create Series</button>
        </div>
    </div>
</template>

<script setup lang="ts">
import { computed, ref, watch } from "vue";
const props = defineProps<{
    showIssueSection: boolean;
    seriesData: any;
    issues: any[];
    readAll: boolean;
    haveAll: boolean;
    imagesrc: string;
}>();
const emit = defineEmits(["cancel", "submit", "update:readAll", "update:haveAll", "update:issues"]);

const readAll = ref(props.readAll);
const haveAll = ref(props.haveAll);

const issues = computed({
  get: () => props.issues,
  set: (val) => emit("update:issues", val)
});

watch(() => props.seriesData.issue_count, (newCount) => {
    emit("update:readAll", false);
    emit("update:haveAll", false);

    const newIssues = Array.from({ length: newCount }, () => ({
        read: false,
        have: false,
        purchaseDate: null,
        readDate: null,
        price: null
    }));
    emit("update:issues", newIssues);
}, { immediate: true });

watch(issues, (val) => {
    const today = new Date().toISOString().split("T")[0];
    val.forEach((issue) => {
        if (issue.have && !issue.purchaseDate) issue.purchaseDate = today;
        if (issue.read && !issue.readDate) issue.readDate = today;
    });
}, { deep: true });

function toggleAll(type: "read" | "have") {
    const updated = [...issues.value];
    updated.forEach((issue) => {
        issue[type] = type === "read" ? readAll.value : haveAll.value;
    });
    emit("update:issues", updated);
}
</script>