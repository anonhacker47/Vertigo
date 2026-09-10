<template>
    <div v-if="showIssueSection" class="card h-full w-full flex flex-col gap-6 shadow-2xl bg-base-100 p-8">
        <div class="flex gap-4">
            <label class="label" for="issue-count">Number of Issues</label>
            <input id="issue-count" type="number" v-model.number="seriesData.issue_count" min="1"
                class="input input-bordered" />
        </div>

        <div class="flex flex-col md:flex-row gap-4 md:gap-16 justify-around">
            <div class="flex gap-4 w-full">
                <label class="label cursor-pointer flex items-center gap-4"
                    :class="haveAll ? 'text-primary' : 'text-white'">
                    <span>Have All?</span>
                    <input type="checkbox" v-model="haveAll" @change="toggleAll('have')" class="checkbox"
                        :class="haveAll ? 'checkbox-primary' : ''" />
                </label>
            </div>
            <div class="w-full">
                <label class="label cursor-pointer flex items-center gap-4"
                    :class="readAll ? 'text-accent' : 'text-white'">
                    <span>Read Already?</span>
                    <input type="checkbox" v-model="readAll" @change="toggleAll('read')" class="checkbox"
                        :class="readAll ? 'checkbox-accent' : ''" />
                </label>
            </div>
        </div>

        <div class="grid place-items-center w-full md:gap-6 md:max-h-[28rem] overflow-y-auto overflow-x-hidden"
            style="grid-template-columns: repeat(auto-fill, minmax(11rem, 1fr)); gap: 1rem;">
            <div v-for="(issue, index) in issues" :key="index"
                class="relative card border w-full md:w-fit shadow-md rounded-md flex flex-col items-center"
                :class="{ 'border-primary': issue.have, 'border-accent': issue.read }">

                <div class="relative w-full md:h-52 h-40">
                    <img :src="coverPreview(issue)" alt="Issue Thumbnail"
                        class="w-full h-full object-cover rounded-md transition duration-300"
                        :class="hasOwnCover(issue) ? 'brightness-100' : 'brightness-50 saturate-50 hover:brightness-75'" />
                    <p
                        class="absolute inset-0 flex items-center justify-center text-white text-3xl font-bold bg-black/50 rounded-md">
                        #{{ index + 1 }}</p>
         
                    <button v-if="hasOwnCover(issue)" type="button" @click="clearCover(issue)"
                        title="Use series cover"
                        class="absolute top-1 right-1 btn btn-xs btn-circle border-0 bg-black/70 text-white hover:bg-error">
                        &times;
                    </button>
                </div>

                <div class="flex flex-col w-full px-4 pt-4 gap-1 text-sm md:text-md">
                    <label><span class="text-white">Title</span></label>
                    <input type="text" v-model.trim="issue.title" maxlength="280" :placeholder="`#${index + 1}`"
                        class="input input-bordered w-full" />
                </div>

                <div class="flex flex-col w-full px-4 pt-3 gap-1 text-sm md:text-md">
                    <label class="flex items-baseline justify-between">
                        <span class="text-white">Cover</span>
                        <span class="text-xs opacity-60">optional</span>
                    </label>
                    <input type="file" accept="image/*" :ref="(el) => setFileInputRef(el, index)"
                        @change="onCoverFile(issue, $event)"
                        class="file-input file-input-bordered file-input-sm w-full" />
                    <input type="text" :value="typeof issue.cover === 'string' ? issue.cover : ''"
                        @input="onCoverUrl(issue, $event)" placeholder="or paste image URL"
                        class="input input-bordered input-sm w-full" />
                </div>

                <div class="flex w-full justify-around gap-2 text-sm md:text-md md:gap-4 p-4">
                    <label class="cursor-pointer flex items-center gap-2"
                        :class="issue.have ? 'text-primary' : 'text-white'">
                        <span>Have</span>
                        <input type="checkbox" v-model="issue.have" class="checkbox"
                            :class="issue.have ? 'checkbox-primary' : ''" />
                    </label>
                    <label class="cursor-pointer flex items-center gap-2"
                        :class="issue.read ? 'text-green-500' : 'text-white'">
                        <span>Read</span>
                        <input type="checkbox" v-model="issue.read" class="checkbox"
                            :class="issue.read ? 'checkbox-accent' : ''" />
                    </label>
                </div>

                <div class="flex flex-col w-full pb-4 px-4 gap-2 text-sm md:text-md"
                    v-if="issue.have || issue.read">
                    <label class="flex flex-col" v-if="issue.have">
                        <span class="text-white">Purchase Date</span>
                        <input type="date" v-model="issue.purchaseDate" class="input input-bordered w-full" />
                    </label>
                    <label class="flex flex-col" v-if="issue.read">
                        <span class="text-white">Read Date</span>
                        <input type="date" v-model="issue.readDate" class="input input-bordered w-full" />
                    </label>
                    <label class="flex flex-col" v-if="issue.have">
                        <span class="text-white">Price</span>
                        <input type="number" v-model="issue.price" class="input input-bordered w-full"
                            step="0.01" />
                    </label>
                </div>

                <div class="flex flex-col w-full pb-4 px-4 gap-2 text-sm md:text-md">
                    <label><span class="text-white">Metron ID</span></label>
                    <input type="number" v-model.number="issue.metron_id" class="input input-bordered w-full" />

                    <label><span class="text-white">Metron URL</span></label>
                    <input type="text" v-model="issue.metron_url" class="input input-bordered w-full" />
                </div>
            </div>
        </div>

        <div class="flex justify-between mt-6">
            <button class="btn btn-danger" @click="$emit('cancel')">Go Back / Cancel</button>
            <button class="btn btn-primary" :disabled="seriesData.issue_count < 1"
                @click.prevent="$emit('submit')">Create Series</button>
        </div>
    </div>
</template>

<script setup lang="ts">
import { onBeforeUnmount, watch, type ComponentPublicInstance } from "vue";
import type { IssueDraft } from "@/types/issue.types";

const props = defineProps<{
    showIssueSection: boolean;
    seriesData: any;
    imagesrc: string;
}>();

defineEmits(["cancel", "submit"]);

// Two-way bound models wired straight to parent components state
const readAll = defineModel<boolean>('readAll', { default: false });
const haveAll = defineModel<boolean>('haveAll', { default: false });
const issues = defineModel<IssueDraft[]>('issues', { default: () => [] });

// Preview object URLs for File covers, keyed by the File so each is created once and revoked once dropped.
const objectUrls = new Map<File, string>();
// Native file inputs per card, so they can be blanked when a cover becomes a URL or is cleared.
const fileInputs = new Map<number, HTMLInputElement>();

function setFileInputRef(el: Element | ComponentPublicInstance | null, index: number) {
    if (el instanceof HTMLInputElement) fileInputs.set(index, el);
    else fileInputs.delete(index);
}

function hasOwnCover(issue: IssueDraft): boolean {
    return issue.cover instanceof File || (typeof issue.cover === "string" && issue.cover.trim() !== "");
}

function coverPreview(issue: IssueDraft): string {
    const cover = issue.cover;
    if (cover instanceof File) {
        let url = objectUrls.get(cover);
        if (!url) {
            url = URL.createObjectURL(cover);
            objectUrls.set(cover, url);
        }
        return url;
    }
    if (typeof cover === "string" && cover.trim()) return cover.trim();
    return props.imagesrc;
}

function onCoverFile(issue: IssueDraft, event: Event) {
    const file = (event.target as HTMLInputElement).files?.[0];
    if (file) issue.cover = file;
}

function onCoverUrl(issue: IssueDraft, event: Event) {
    const value = (event.target as HTMLInputElement).value;
    issue.cover = value === "" ? null : value;
}

function clearCover(issue: IssueDraft) {
    issue.cover = null;
}

function releaseUnusedObjectUrls(current: IssueDraft[]) {
    const live = new Set<File>();
    current.forEach((issue) => {
        if (issue.cover instanceof File) live.add(issue.cover);
    });
    for (const [file, url] of objectUrls) {
        if (!live.has(file)) {
            URL.revokeObjectURL(url);
            objectUrls.delete(file);
        }
    }
}

watch(issues, (val) => {
    if (!val) return;
    const today = new Date().toISOString().split("T")[0];
    val.forEach((issue) => {
        if (issue.have && !issue.purchaseDate) issue.purchaseDate = today;
        if (issue.read && !issue.readDate) issue.readDate = today;
    });

    releaseUnusedObjectUrls(val);
    // A file input should only show a name while the cover is that File.
    fileInputs.forEach((input, index) => {
        if (!(val[index]?.cover instanceof File) && input.value) input.value = "";
    });
}, { deep: true });

onBeforeUnmount(() => {
    objectUrls.forEach((url) => URL.revokeObjectURL(url));
    objectUrls.clear();
});

function toggleAll(type: "read" | "have") {
    if (!issues.value) return;

    issues.value.forEach((issue) => {
        issue[type] = type === "read" ? readAll.value : haveAll.value;
    });
}
</script>
