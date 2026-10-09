<template>
  <section class="fm-section" aria-labelledby="issues-title">
    <div class="fm-section__head">
      <div>
        <h2 id="issues-title" class="fm-section__title">{{ manga ? "Volumes" : "Issues" }}</h2>
        <p class="fm-hint mt-1">{{ summary }}</p>
      </div>
      <div class="flex flex-wrap items-center gap-x-5 gap-y-3">
        <RunStrip v-if="issues.length" :run="run" :max="32" />
        <div class="stepper" role="group" :aria-label="`Number of ${unitPlural}`">
          <button type="button" class="fm-iconbtn fm-iconbtn--sm border-0" :aria-label="`One fewer ${unit}`" :disabled="issueCount <= 1" @click="setCount(issueCount - 1)">
            <i class="pi pi-minus" style="font-size: 10px"></i>
          </button>
          <input
            :value="issueCount"
            type="number"
            min="1"
            step="1"
            inputmode="numeric"
            class="stepper__input"
            :aria-label="`Number of ${unitPlural}`"
            @change="setCount(Number(($event.target as HTMLInputElement).value))"
          />
          <button type="button" class="fm-iconbtn fm-iconbtn--sm border-0" :aria-label="`One more ${unit}`" @click="setCount(issueCount + 1)">
            <i class="pi pi-plus" style="font-size: 10px"></i>
          </button>
        </div>
      </div>
    </div>

    <div class="mt-4 flex flex-wrap items-center gap-2">
      <button type="button" class="fm-toggle fm-toggle--own" :aria-pressed="haveAll" @click="setAll('have', !haveAll)">Own all</button>
      <button type="button" class="fm-toggle fm-toggle--read" :aria-pressed="readAll" @click="setAll('read', !readAll)">Read all</button>
      <p class="fm-hint basis-full sm:ml-auto sm:basis-auto">Marking {{ aUnit }} owned or read stamps today's date and opens the row so you can change it.</p>
    </div>

    <ol class="issue-list mt-4">
      <li v-for="(issue, index) in visibleIssues" :key="index" class="issue" :class="{ 'issue--own': issue.have, 'issue--read': issue.read }">
        <div class="issue__row">
          <span class="issue__num">{{ index + 1 }}</span>

          <button
            type="button"
            class="issue__cover"
            :title="hasOwnCover(issue) ? `Replace this ${unit}'s cover` : `Add a cover for this ${unit}`"
            @click="fileInputs.get(index)?.click()"
          >
            <img :src="coverPreview(issue)" alt="" :class="{ 'opacity-40': !hasOwnCover(issue) }" />
            <i class="pi pi-camera"></i>
          </button>
          <input
            type="file"
            accept="image/*"
            class="sr-only"
            tabindex="-1"
            :ref="(el) => setFileInputRef(el, index)"
            @change="onCoverFile(issue, $event)"
          />

          <input
            v-model.trim="issue.title"
            type="text"
            maxlength="280"
            class="fm-input issue__title"
            :placeholder="`${unitLabel} ${index + 1}`"
            :aria-label="`Title of ${unit} ${index + 1}`"
          />

          <div class="issue__actions">
            <button type="button" class="fm-toggle fm-toggle--own fm-toggle--sm" :aria-pressed="issue.have" @click="toggleFlag(issue, index, 'have')">Own</button>
            <button type="button" class="fm-toggle fm-toggle--read fm-toggle--sm" :aria-pressed="issue.read" @click="toggleFlag(issue, index, 'read')">Read</button>
            <button
              type="button"
              class="fm-iconbtn fm-iconbtn--sm"
              :aria-expanded="isOpen(index)"
              :aria-label="`More details for ${unit} ${index + 1}`"
              @click="toggleOpen(index)"
            >
              <i class="pi pi-chevron-down issue__chev" :class="{ 'issue__chev--open': isOpen(index) }" style="font-size: 11px"></i>
            </button>
          </div>
        </div>

        <div v-if="isOpen(index)" class="issue__details grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          <label v-if="issue.have">
            <span class="fm-label">Bought on</span>
            <input v-model="issue.purchaseDate" type="date" class="fm-input" />
          </label>
          <label v-if="issue.have">
            <span class="fm-label">Price</span>
            <input v-model.number="issue.price" type="number" min="0" step="0.01" placeholder="0.00" class="fm-input" />
          </label>
          <label v-if="issue.read">
            <span class="fm-label">Read on</span>
            <input v-model="issue.readDate" type="date" class="fm-input" />
          </label>
          <label>
            <span class="fm-label">Cover link</span>
            <input :value="coverLink(issue)" type="text" placeholder="https://" class="fm-input" @input="onCoverUrl(issue, $event)" />
          </label>
          <template v-if="!manga">
            <label>
              <span class="fm-label">Metron ID</span>
              <input v-model.number="issue.metron_id" type="number" class="fm-input" />
            </label>
            <label>
              <span class="fm-label">Metron URL</span>
              <input v-model="issue.metron_url" type="text" placeholder="https://metron.cloud/issue/" class="fm-input" />
            </label>
          </template>
          <p v-if="hasOwnCover(issue)" class="fm-hint sm:col-span-2 lg:col-span-3">
            {{ isFileCover(issue) ? `Cover: ${coverFileName(issue)}.` : "Cover from the link above." }}
            <button type="button" class="font-bold text-sky-400 hover:text-sky-300" @click="clearCover(issue)">Use the series cover instead</button>
          </p>
        </div>
      </li>
    </ol>

    <div v-if="issues.length > visibleIssues.length" class="mt-3">
      <button type="button" class="text-sm font-bold text-sky-400 hover:text-sky-300" @click="showAll = true">
        Show all {{ issues.length }} {{ unitPlural }}
      </button>
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed, onBeforeUnmount, ref, watch, type ComponentPublicInstance } from "vue";
import type { IssueDraft } from "@/types/issue.types";
import type { RunTick } from "@/types/insights.types";
import RunStrip from "@/components/insights/RunStrip.vue";

const INITIAL_ROWS = 24;

const props = defineProps<{
  imagesrc: string;
  manga?: boolean;
}>();

const readAll = defineModel<boolean>("readAll", { default: false });
const haveAll = defineModel<boolean>("haveAll", { default: false });
const issues = defineModel<IssueDraft[]>("issues", { default: () => [] });
const issueCount = defineModel<number>("issueCount", { default: 1 });

const showAll = ref(false);
const openRows = ref(new Set<number>());

const objectUrls = new Map<File, string>();
const fileInputs = new Map<number, HTMLInputElement>();

const unit = computed(() => (props.manga ? "volume" : "issue"));
const unitPlural = computed(() => `${unit.value}s`);
const unitLabel = computed(() => (props.manga ? "Volume" : "Issue"));
const aUnit = computed(() => (props.manga ? "a volume" : "an issue"));

const visibleIssues = computed(() => (showAll.value ? issues.value : issues.value.slice(0, INITIAL_ROWS)));

const run = computed<RunTick[]>(() =>
  issues.value.map((issue, i) => ({ number: i + 1, state: issue.read ? "read" : issue.have ? "owned" : "missing" }))
);

const summary = computed(() => {
  const n = issues.value.length;
  const owned = issues.value.filter((i) => i.have).length;
  const read = issues.value.filter((i) => i.read).length;
  return `${n} ${n === 1 ? unit.value : unitPlural.value}, ${owned} owned, ${read} read`;
});

function setCount(next: number) {
  issueCount.value = Math.max(1, Math.floor(Number(next) || 1));
}

function setAll(type: "have" | "read", value: boolean) {
  if (type === "have") haveAll.value = value;
  else readAll.value = value;
  issues.value.forEach((issue) => { issue[type] = value; });
}

// Switching Own or Read on opens the row so the stamped date (and price) are right there to change.
function toggleFlag(issue: IssueDraft, index: number, type: "have" | "read") {
  issue[type] = !issue[type];
  if (issue[type]) openRow(index);
}

const isOpen = (index: number) => openRows.value.has(index);
function openRow(index: number) {
  if (openRows.value.has(index)) return;
  const next = new Set(openRows.value);
  next.add(index);
  openRows.value = next;
}
function toggleOpen(index: number) {
  const next = new Set(openRows.value);
  if (next.has(index)) next.delete(index);
  else next.add(index);
  openRows.value = next;
}

function setFileInputRef(el: Element | ComponentPublicInstance | null, index: number) {
  if (el instanceof HTMLInputElement) fileInputs.set(index, el);
  else fileInputs.delete(index);
}

const isFileCover = (issue: IssueDraft) => issue.cover instanceof File;
const coverFileName = (issue: IssueDraft) => (issue.cover instanceof File ? issue.cover.name : "");
const coverLink = (issue: IssueDraft) => (typeof issue.cover === "string" ? issue.cover : "");

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
  // A file input should only hold a file while the cover is that File.
  fileInputs.forEach((input, index) => {
    if (!(val[index]?.cover instanceof File) && input.value) input.value = "";
  });
}, { deep: true });

onBeforeUnmount(() => {
  objectUrls.forEach((url) => URL.revokeObjectURL(url));
  objectUrls.clear();
});
</script>

<style scoped>
.stepper {
  display: inline-flex;
  align-items: center;
  gap: 2px;
  padding: 3px;
  border-radius: 10px;
  border: 1px solid rgba(255, 255, 255, 0.08);
  background: #0b1220;
}
.stepper__input {
  width: 3.25rem;
  border: 0;
  outline: none;
  background: transparent;
  text-align: center;
  color: #fff;
  font-size: 14px;
  font-weight: 800;
  font-variant-numeric: tabular-nums;
  -moz-appearance: textfield;
  appearance: textfield;
}
.stepper__input::-webkit-inner-spin-button,
.stepper__input::-webkit-outer-spin-button {
  appearance: none;
  margin: 0;
}
.stepper__input:focus-visible {
  border-radius: 6px;
  box-shadow: 0 0 0 2px #38bdf8;
}

.issue-list {
  list-style: none;
  overflow: hidden;
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.08);
  background: #0b1220;
}
.issue {
  position: relative;
}
.issue + .issue {
  border-top: 1px solid rgba(255, 255, 255, 0.06);
}

.issue::before {
  content: "";
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 3px;
  background: transparent;
}
.issue--own::before { background: #38bdf8; }
.issue--read::before { background: #4ade80; }
.issue--own.issue--read::before { background: linear-gradient(to bottom, #38bdf8 50%, #4ade80 50%); }

.issue__row {
  display: grid;
  grid-template-columns: 2rem 2rem minmax(0, 1fr);
  align-items: center;
  gap: 10px;
  padding: 8px 10px 8px 12px;
}
@media (min-width: 640px) {
  .issue__row {
    grid-template-columns: 2rem 2rem minmax(0, 1fr) auto;
  }
}
.issue__num {
  font-size: 13px;
  font-weight: 800;
  color: #64748b;
  text-align: right;
  font-variant-numeric: tabular-nums;
}
.issue__cover {
  position: relative;
  width: 2rem;
  height: 3rem;
  overflow: hidden;
  border-radius: 2px;
  background: #1e293b;
  cursor: pointer;
}
.issue__cover img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}
.issue__cover i {
  position: absolute;
  inset: 0;
  display: grid;
  place-items: center;
  font-size: 12px;
  color: #fff;
  background: rgba(11, 18, 32, 0.6);
  opacity: 0;
}
.issue__cover:hover i,
.issue__cover:focus-visible i {
  opacity: 1;
}
.issue__cover:focus-visible {
  outline: 2px solid #38bdf8;
  outline-offset: 1px;
}
/* The title sits quietly in the row until it is hovered or focused. */
.issue__title {
  min-height: 36px;
  border-color: transparent;
  background: transparent;
}
.issue__title:hover {
  border-color: rgba(255, 255, 255, 0.12);
}
.issue__actions {
  display: flex;
  align-items: center;
  gap: 6px;
  grid-column: 2 / -1;
}
@media (min-width: 640px) {
  .issue__actions {
    grid-column: auto;
  }
}
.issue__chev {
  transition: transform 0.15s ease;
}
.issue__chev--open {
  transform: rotate(180deg);
}
.issue__details {
  padding: 10px 12px 14px 12px;
  border-top: 1px dashed rgba(255, 255, 255, 0.06);
}
@media (min-width: 640px) {
  .issue__details {
    padding-left: 5.25rem;
  }
}
@media (prefers-reduced-motion: reduce) {
  .issue__chev { transition: none; }
}
</style>
