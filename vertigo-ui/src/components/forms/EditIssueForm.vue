<template>
    <div class="card h-full w-full md:w-2/4 flex flex-col gap-6 shadow-2xl bg-base-100 p-8">
        <div class="flex flex-col md:flex-row gap-6">
            <label class="flex flex-col gap-1 w-full">
                <span class="text-sm text-slate-300">Title</span>
                <input type="text" v-model.trim="issue.title" maxlength="280" placeholder="Issue title"
                    class="input input-bordered w-full" required />
            </label>
            <label class="flex flex-col gap-1 w-full md:w-40">
                <span class="text-sm text-slate-300">Number</span>
                <input type="number" v-model.number="issue.number" min="0" step="1"
                    class="input input-bordered w-full" required />
            </label>
            <label class="flex flex-col gap-1 w-full md:w-56">
                <span class="text-sm text-slate-300">Cover Date</span>
                <input type="date" v-model="issue.cover_date" class="input input-bordered w-full" />
            </label>
        </div>

        <div class="flex flex-col gap-1">
            <span class="text-sm text-slate-300">Description</span>
            <textarea class="textarea textarea-bordered w-full h-28" maxlength="570" placeholder="Summary"
                v-model="issue.description"></textarea>
            <p class="text-sm" :class="descriptionLength > 570 ? 'text-red-500' : 'text-gray-400'">
                {{ descriptionLength }}/570 characters
            </p>
        </div>

        <div class="flex flex-col gap-1">
            <span class="text-sm text-slate-300">Notes</span>
            <textarea class="textarea textarea-bordered w-full h-28" maxlength="3000" placeholder="Personal notes"
                v-model="issue.notes"></textarea>
            <p class="text-sm" :class="notesLength > 3000 ? 'text-red-500' : 'text-gray-400'">
                {{ notesLength }}/3000 characters
            </p>
        </div>

        <div class="flex flex-col md:flex-row gap-6">
            <div class="flex flex-col gap-3 w-full rounded-xl border border-base-300 p-4">
                <label class="cursor-pointer flex items-center gap-3"
                    :class="issue.is_owned ? 'text-primary' : 'text-white'">
                    <input type="checkbox" v-model="issue.is_owned" class="checkbox"
                        :class="issue.is_owned ? 'checkbox-primary' : ''" />
                    <span class="font-semibold">Owned</span>
                </label>
                <template v-if="issue.is_owned">
                    <label class="flex flex-col gap-1">
                        <span class="text-sm text-slate-300">Bought Date</span>
                        <input type="date" v-model="issue.bought_date" class="input input-bordered w-full" />
                    </label>
                    <label class="flex flex-col gap-1">
                        <span class="text-sm text-slate-300">Price</span>
                        <input type="number" v-model.number="issue.bought_price" min="0" step="0.01"
                            placeholder="0.00" class="input input-bordered w-full" />
                    </label>
                </template>
            </div>

            <div class="flex flex-col gap-3 w-full rounded-xl border border-base-300 p-4">
                <label class="cursor-pointer flex items-center gap-3"
                    :class="issue.is_read ? 'text-accent' : 'text-white'">
                    <input type="checkbox" v-model="issue.is_read" class="checkbox"
                        :class="issue.is_read ? 'checkbox-accent' : ''" />
                    <span class="font-semibold">Read</span>
                </label>
                <label v-if="issue.is_read" class="flex flex-col gap-1">
                    <span class="text-sm text-slate-300">Read Date</span>
                    <input type="date" v-model="issue.read_date" class="input input-bordered w-full" />
                </label>
            </div>
        </div>

        <div class="flex flex-col md:flex-row gap-6">
            <label class="flex flex-col gap-1 w-full md:w-48">
                <span class="text-sm text-slate-300">Metron ID</span>
                <input type="number" v-model.number="issue.metron_id" min="0" step="1"
                    class="input input-bordered w-full" />
            </label>
            <label class="flex flex-col gap-1 w-full">
                <span class="text-sm text-slate-300">Metron URL</span>
                <input type="url" v-model.trim="issue.metron_url" placeholder="https://metron.cloud/issue/..."
                    class="input input-bordered w-full" />
            </label>
        </div>

        <div class="flex flex-col-reverse sm:flex-row sm:items-center sm:justify-between gap-3 pt-6 border-t border-base-300">
            <button type="button" @click="$emit('delete')" :disabled="saving"
                class="btn btn-ghost text-error hover:bg-error/10 w-full sm:w-auto">
                <i class="pi pi-trash"></i>
                Delete Issue
            </button>
            <div class="flex flex-col-reverse sm:flex-row gap-3 w-full sm:w-auto">
                <button type="button" @click="$router.back()" :disabled="saving" class="btn btn-ghost w-full sm:w-auto">
                    Cancel
                </button>
                <button type="button" @click="$emit('save')" :disabled="!canSave || saving"
                    class="btn btn-primary w-full sm:w-auto sm:min-w-40">
                    <span v-if="saving" class="loading loading-spinner loading-sm"></span>
                    {{ saving ? 'Saving...' : 'Save Details' }}
                </button>
            </div>
        </div>
    </div>
</template>

<script setup lang="ts">
import { computed, watch } from "vue";
import type { IssueEditFields } from "@/types/issue.types";

defineProps<{
    saving?: boolean;
}>();

defineEmits<{
    (e: "save"): void;
    (e: "delete"): void;
}>();

// Bound straight to the parent's form state; fields are edited in place.
const issue = defineModel<IssueEditFields>({ required: true });

const descriptionLength = computed(() => (issue.value.description || "").length);
const notesLength = computed(() => (issue.value.notes || "").length);

const canSave = computed(() => {
    const number = issue.value.number;
    return issue.value.title.trim() !== ""
        && typeof number === "number" && Number.isInteger(number) && number >= 0
        && descriptionLength.value <= 570
        && notesLength.value <= 3000;
});

const today = () => new Date().toISOString().split("T")[0];

// Same convenience as the create form: turning a status on defaults its date to today.
watch(() => issue.value.is_owned, (owned) => {
    if (owned && !issue.value.bought_date) issue.value.bought_date = today();
});
watch(() => issue.value.is_read, (read) => {
    if (read && !issue.value.read_date) issue.value.read_date = today();
});
</script>
