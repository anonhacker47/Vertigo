<template>
  <article class="issue-card" :class="{ 'issue-card--fallback': !hasOwnCover, 'motion-safe:animate-wiggle': editMode }">
    <div class="relative">
      <RouterLink :to="detailRoute" class="issue-card__cover" :style="borderStyle" :aria-label="`Open ${label}`">
        <img v-if="coverSrc && !coverFailed" :src="coverSrc" :alt="label" loading="lazy" decoding="async" @error="coverFailed = true" />
        <span v-else class="issue-card__placeholder" :style="{ background: placeholderGradient(series.title) }" role="img" :aria-label="label"></span>
      </RouterLink>

      <!-- Own cover: a small corner chip. Series cover standing in: a large ghost number over the dimmed art. -->
      <span v-if="hasOwnCover" class="issue-card__chip">{{ numberLabel }}</span>
      <span v-else class="issue-card__ghost" aria-hidden="true">{{ numberLabel }}</span>

      <Button
        v-if="editMode"
        icon="pi pi-times"
        rounded
        size="small"
        severity="danger"
        class="issue-card__delete"
        :aria-label="`Delete ${label}`"
        title="Delete issue"
        @click.prevent="$emit('deleteIssue')"
      />
    </div>

    <div class="issue-card__panel">
      <div class="issue-card__head">
        <RouterLink :to="detailRoute" class="issue-card__title" :title="titleText">{{ titleText }}</RouterLink>
        <template v-if="issue.is_owned">
          <InputNumber
            v-if="editing === 'price'"
            :model-value="issue.bought_price ?? null"
            mode="decimal"
            :min="0"
            :max-fraction-digits="2"
            size="small"
            placeholder="0.00"
            class="issue-card__input issue-card__input--price"
            :input-style="{ width: '5.5rem' }"
            aria-label="Price paid"
            @update:model-value="onPrice"
            @blur="editing = null"
            @keydown.escape="editing = null"
          />
          <button
            v-else
            type="button"
            class="issue-card__price"
            :class="{ 'is-empty': !hasPrice }"
            :title="hasPrice ? 'Change the price paid' : 'Add the price paid'"
            :aria-label="hasPrice ? `Paid ${symbol}${issue.bought_price}, change` : 'Add the price paid'"
            @click="open('price', $event)"
          >
            {{ hasPrice ? `${symbol}${issue.bought_price}` : "+ price" }}
          </button>
        </template>
      </div>

      <!-- One short row per state, date on the right. A date picker replaces the row while editing. -->
      <DatePicker
        v-if="editing === 'bought'"
        :model-value="ymdToDate(issue.bought_date)"
        date-format="d M yy"
        size="small"
        fluid
        class="issue-card__input"
        aria-label="Bought on"
        @update:model-value="onDate('is_owned', $event as Date | null)"
        @hide="editing = null"
        @keydown.escape="editing = null"
      />
      <div v-else class="issue-card__flag issue-card__flag--own" :class="{ 'is-on': issue.is_owned }">
        <button type="button" class="issue-card__toggle" :aria-pressed="issue.is_owned" @click="toggle('is_owned')">
          <i class="issue-card__dot"></i>{{ issue.is_owned ? "Owned" : "Not owned" }}
        </button>
        <button
          v-if="issue.is_owned"
          type="button"
          class="issue-card__when"
          :title="`Bought ${formatDate(issue.bought_date) || 'on an unknown date'}. Click to change.`"
          @click="open('bought', $event)"
        >
          {{ shortDate(issue.bought_date) || "set date" }}
        </button>
      </div>

      <DatePicker
        v-if="editing === 'read'"
        :model-value="ymdToDate(issue.read_date)"
        date-format="d M yy"
        size="small"
        fluid
        class="issue-card__input"
        aria-label="Read on"
        @update:model-value="onDate('is_read', $event as Date | null)"
        @hide="editing = null"
        @keydown.escape="editing = null"
      />
      <div v-else class="issue-card__flag issue-card__flag--read" :class="{ 'is-on': issue.is_read }">
        <button type="button" class="issue-card__toggle" :aria-pressed="issue.is_read" @click="toggle('is_read')">
          <i class="issue-card__dot"></i>{{ issue.is_read ? "Read" : "Unread" }}
        </button>
        <button
          v-if="issue.is_read"
          type="button"
          class="issue-card__when"
          :title="`Read ${formatDate(issue.read_date) || 'on an unknown date'}. Click to change.`"
          @click="open('read', $event)"
        >
          {{ shortDate(issue.read_date) || "set date" }}
        </button>
      </div>
    </div>
  </article>
</template>

<script setup lang="ts">
import { computed, nextTick, ref, watch } from "vue";
import getSymbolFromCurrency from "currency-symbol-map";
import Button from "primevue/button";
import DatePicker from "primevue/datepicker";
import InputNumber from "primevue/inputnumber";
import { dateToYmd, todayYmd, ymdToDate } from "@/utils/dateInput";
import type { Issue } from "@/types/issue.types";
import IssueService from "@/services/IssueService";
import { placeholderGradient } from "@/utils/placeholderGradient";
import { hasCustomIssueTitle, issueNumberLabel } from "@/utils/issueTitle";

const props = defineProps({
  issue: { type: Object as () => Issue, required: true },
  /** Series cover, shown dimmed when the issue has none of its own. */
  image: String,
  themecolor: String,
  preferred_currency: String,
  edit_mode: Boolean,
  series: { type: Object, required: true },
});

const emit = defineEmits(["updateStatus", "deleteIssue"]);

const editMode = computed(() => props.edit_mode);
const editing = ref<"bought" | "read" | "price" | null>(null);

const hasCustomTitle = computed(() => hasCustomIssueTitle(props.issue.title, props.issue.number));
const numberLabel = computed(() => issueNumberLabel(props.issue.number, props.issue.title));
// Without a real title the line names the entry by its number, so it does not just repeat the chip.
const titleText = computed(() => {
  if (hasCustomTitle.value) return props.issue.title;
  return props.series.manga ? `Volume ${props.issue.number}` : `Issue ${numberLabel.value}`;
});
const label = computed(() => (hasCustomTitle.value ? `${numberLabel.value} ${props.issue.title}` : titleText.value));
const hasOwnCover = computed(() => !!props.issue.thumbnail);
const hasPrice = computed(() => props.issue.bought_price !== null && props.issue.bought_price !== undefined);

// The cover frame wears the series' accent colour; owned and read state lives in the panel below it.
const borderStyle = computed(() => (props.themecolor ? { borderColor: `rgb${props.themecolor}` } : {}));

// The issue's own cover (cache-busted by last_updated) wins; otherwise the series cover passed as `image`.
const coverSrc = computed(() =>
  hasOwnCover.value ? IssueService.getIssueImageById(props.issue.id, props.issue.last_updated) : props.image || null
);
const coverFailed = ref(false);
watch(coverSrc, () => { coverFailed.value = false; });

const detailRoute = computed(() => ({
  name: "IssueDetail",
  params: { seriesId: props.series.id, slug: props.series.slug, number: props.issue.number },
}));

const symbol = getSymbolFromCurrency(props.preferred_currency || "") || "";

function parseDate(value: Date | string | null | undefined): Date | null {
  if (!value) return null;
  const date = new Date(value);
  return Number.isNaN(date.getTime()) ? null : date;
}

function formatDate(value: Date | string | null | undefined): string {
  const date = parseDate(value);
  return date ? date.toLocaleDateString("en-GB", { day: "numeric", month: "short", year: "numeric" }) : "";
}

// "7 Oct" this year, "7 Oct 24" otherwise; the full date sits in the tooltip.
function shortDate(value: Date | string | null | undefined): string {
  const date = parseDate(value);
  if (!date) return "";
  const sameYear = date.getFullYear() === new Date().getFullYear();
  return date.toLocaleDateString("en-GB", sameYear ? { day: "numeric", month: "short" } : { day: "numeric", month: "short", year: "2-digit" });
}

const today = () => todayYmd();

// Switching on stamps today, matching the create page; the date beside it is there to change it.
function toggle(status: "is_owned" | "is_read") {
  if (props.issue[status]) emit("updateStatus", { status, value: false });
  else emit("updateStatus", { status, value: true, date: today() });
}

function open(field: "bought" | "read" | "price", event: Event) {
  const card = (event.currentTarget as HTMLElement | null)?.closest(".issue-card");
  editing.value = field;
  nextTick(() => card?.querySelector<HTMLInputElement>(".issue-card__input input")?.focus());
}

function onDate(status: "is_owned" | "is_read", value: Date | null) {
  const date = dateToYmd(value);
  if (date) emit("updateStatus", { status, value: true, date });
  editing.value = null;
}

function onPrice(value: number | null) {
  emit("updateStatus", { status: "bought_price", value });
  editing.value = null;
}
</script>

<style scoped>
/* Framed cover on top, plain panel underneath. The frame takes the series' accent colour. */
.issue-card {
  display: flex;
  width: 100%;
  min-width: 0;
  flex-direction: column;
}

.issue-card__cover {
  position: relative;
  display: block;
  width: 100%;
  aspect-ratio: 2 / 3;
  overflow: hidden;
  border-radius: 10px 10px 0 0;
  /* border: 2px solid rgba(255, 255, 255, 0.12); */
  background: #1e293b;
}
.issue-card__cover:focus-visible { outline: 2px solid #fff; outline-offset: -2px; }
.issue-card__cover img,
.issue-card__placeholder {
  display: block;
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.15s ease;
}
.issue-card__cover:hover img { transform: scale(1.03); }
/* .issue-card__cover::after {
  content: "";
  position: absolute;
  inset: 0;
  z-index: 1;
  background: rgba(10, 18, 34, 0.654);
  mix-blend-mode: multiply;
  pointer-events: none;
  transition: opacity 0.15s ease;
} */
.issue-card__cover:hover::after { opacity: 0; }
.issue-card--fallback .issue-card__cover img {
  filter: brightness(0.45) saturate(0.6);
}

.issue-card__chip {
  position: absolute;
  top: 6px;
  left: 6px;
  z-index: 2;
  padding: 2px 7px;
  border-radius: 6px;
  background: rgba(11, 18, 32, 0.85);
  color: #fff;
  font-size: 13px;
  font-weight: 800;
  line-height: 1.4;
  pointer-events: none;
}
.issue-card__ghost {
  position: absolute;
  inset: 0;
  z-index: 2;
  display: grid;
  place-items: center;
  color: #fff;
  font-size: 30px;
  font-weight: 900;
  text-shadow: 0 2px 14px rgba(0, 0, 0, 0.7);
  pointer-events: none;
}

.issue-card__delete {
  position: absolute;
  top: 6px;
  right: 6px;
  z-index: 3;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.45);
}

/* ---- panel: title row, status rows, in its own dark box under the framed cover ---- */
.issue-card__panel {
  display: flex;
  flex-direction: column;
  gap: 1px;
  padding: 7px 8px 7px;
  border: 2px solid #0b1220;
  border-top: 0;
  border-radius: 0 0 10px 10px;
  background: #0b1220;
}
.issue-card__head {
  display: flex;
  min-height: 18px;
  margin-bottom: 3px;
  align-items: center;
  justify-content: space-between;
  gap: 6px;
}
.issue-card__title {
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  color: #fff;
  font-size: 12.5px;
  font-weight: 800;
  line-height: 1.3;
}
.issue-card__title:hover { color: #7dd3fc; }
.issue-card__price {
  flex: none;
  padding: 0 4px;
  border-radius: 4px;
  color: #86efac;
  font-size: 11.5px;
  font-weight: 800;
  line-height: 1.4;
  cursor: pointer;
  transition: color 0.12s ease, background-color 0.12s ease;
}
.issue-card__price.is-empty { color: #64748b; }
.issue-card__price:hover { background: rgba(255, 255, 255, 0.06); color: #fff; }
.issue-card__price:focus-visible { outline: 2px solid #38bdf8; outline-offset: 1px; }

.issue-card__flag {
  display: flex;
  min-height: 20px;
  min-width: 0;
  align-items: center;
  justify-content: space-between;
  gap: 6px;
  color: #64748b;
  font-size: 11.5px;
  font-weight: 700;
  line-height: 1.3;
}
.issue-card__flag--own.is-on { color: #7dd3fc; }
.issue-card__flag--read.is-on { color: #86efac; }

.issue-card__toggle,
.issue-card__when {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  padding: 1px 4px 1px 3px;
  border-radius: 5px;
  color: inherit;
  white-space: nowrap;
  cursor: pointer;
  transition: color 0.12s ease, background-color 0.12s ease;
}
.issue-card__when {
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  color: #94a3b8;
  font-size: 11px;
}
.issue-card__toggle:hover,
.issue-card__when:hover { background: rgba(255, 255, 255, 0.07); color: #fff; }
.issue-card__toggle:focus-visible,
.issue-card__when:focus-visible { outline: 2px solid #38bdf8; outline-offset: 1px; }

.issue-card__dot {
  display: block;
  width: 7px;
  height: 7px;
  flex: none;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.18);
}
.issue-card__flag--own.is-on .issue-card__dot { background: #38bdf8; }
.issue-card__flag--read.is-on .issue-card__dot { background: #4ade80; }

.issue-card__input {
  width: 100%;
  min-width: 0;
}
.issue-card__input--price {
  width: auto;
}

/* Single-column phones: the card is wide, so give the controls room for thumbs. */
@media (max-width: 639px) {
  .issue-card__panel { gap: 2px; padding: 10px 12px 10px; }
  .issue-card__head { min-height: 24px; margin-bottom: 4px; }
  .issue-card__title { font-size: 15px; }
  .issue-card__price { padding: 4px 8px; font-size: 13px; }
  .issue-card__flag { min-height: 36px; font-size: 14px; }
  .issue-card__toggle,
  .issue-card__when { padding: 6px 10px 6px 8px; border-radius: 8px; }
  .issue-card__when { font-size: 13px; }
  .issue-card__dot { width: 9px; height: 9px; }
  .issue-card__chip { padding: 3px 9px; font-size: 13px; }
  .issue-card__ghost { font-size: 40px; }
}

@media (prefers-reduced-motion: reduce) {
  .issue-card__cover img,
  .issue-card__price,
  .issue-card__toggle,
  .issue-card__when { transition: none; }
  .issue-card__cover:hover img { transform: none; }
  .issue-card__cover::after { transition: none; }
}
</style>
