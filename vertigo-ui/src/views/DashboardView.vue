<template>
  <div class="mx-auto flex w-full max-w-page flex-col gap-7 px-4 pb-8 pt-6 md:min-h-[calc(100vh-var(--spacing-header))] md:px-8">
    <!-- the shelf in numbers -->
    <div class="grid grid-cols-2 gap-x-6 gap-y-5 border-b border-white/8 pb-5 md:grid-cols-[1fr_1fr_1fr_auto]">
      <ShelfFigure :value="seriesInfo.totalSeriesCount" unit="series"
        :label="`${seriesInfo.collectedSeriesCount} fully collected · ${seriesInfo.readSeriesCount} fully read`"
        :ratio="pct(seriesInfo.collectedSeriesCount, seriesInfo.totalSeriesCount)" />
      <ShelfFigure :value="issueInfo.collectedIssueCount" unit="owned" :label="`of ${issueInfo.totalIssueCount} issues`"
        :ratio="pct(issueInfo.collectedIssueCount, issueInfo.totalIssueCount)" />
      <ShelfFigure :value="issueInfo.readIssueCount" unit="read" :label="`of the ${issueInfo.collectedIssueCount} you own`"
        :ratio="pct(issueInfo.readIssueCount, issueInfo.collectedIssueCount)" tone="read" />
      <RouterLink :to="{ name: 'AddSeries' }" custom v-slot="{ navigate }">
        <Button label="Add series" icon="pi pi-plus" size="small" class="w-full self-start md:w-auto md:self-center" @click="navigate" />
      </RouterLink>
    </div>

    <!-- three panels, side by side, no scrolling on a desktop -->
    <div class="grid flex-1 grid-cols-1 gap-10 md:grid-cols-[7fr_6fr_7fr] md:gap-8">
      <section class="min-w-0" aria-label="Breakdown">
        <BreakdownDonut>
          <template #aside>
            <div class="tooltip tooltip-left shrink-0" data-tip="How your shelf splits by publisher, genre, creator or character, counted in series or issues.">
              <button class="btn btn-circle btn-ghost btn-xs text-info" type="button" aria-label="About this chart" @click="handleInfoClick">
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" class="h-4 w-4 stroke-current">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                </svg>
              </button>
            </div>
          </template>
        </BreakdownDonut>
      </section>

      <section class="flex min-w-0 flex-col" aria-label="Recent purchases">
        <h2 class="text-xl font-extrabold text-center text-[#F9FAFB]">Recent Purchases</h2>
        <div class="flex flex-1 items-center justify-center">
          <SwiperCardItem v-if="recentPurchasedIssues && recentPurchasedIssues.length > 0" :recentPurchasedIssues="recentPurchasedIssues" />
          <div v-else class="py-10 text-slate-400">No recent purchases found.</div>
        </div>
      </section>

      <section class="min-w-0" aria-label="Purchases per month">
        <PurchasesChart :currency-symbol="symbol" />
      </section>
    </div>
  </div>

  <Dialog v-model:visible="showModal" modal header="Total spent" :style="{ width: '26rem' }" :draggable="false" class="rounded-2xl shadow-2xl" @hide="countUp?.kill()">
    <div class="flex items-center justify-center px-4 pb-6 pt-2 text-[44px] font-black leading-none tracking-tight text-white tabular-nums">{{ symbol }}{{ shownTotal }}</div>
  </Dialog>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue';
import { Dialog } from "primevue";
import { gsap } from 'gsap';
import getSymbolFromCurrency from "currency-symbol-map";
import { useUserStore } from "../store/user";
import ShelfFigure from '../components/dashboard/ShelfFigure.vue';
import SwiperCardItem from '../components/cards/SwiperCardItem.vue';
import BreakdownDonut from '../components/dashboard/BreakdownDonut.vue';
import PurchasesChart from '../components/dashboard/PurchasesChart.vue';
import DashboardService from '../services/DashboardService';

const userstore = useUserStore();
const preferred_currency = userstore.getUser()?.preferred_currency ?? '';
const symbol = getSymbolFromCurrency(preferred_currency) ?? '';

const seriesInfo = ref({ totalSeriesCount: 0, collectedSeriesCount: 0, readSeriesCount: 0 });
const issueInfo = ref({ totalIssueCount: 0, collectedIssueCount: 0, readIssueCount: 0 });
const recentPurchasedIssues = ref([]);

const pct = (part: number, whole: number) => (whole ? (100 * part) / whole : 0);

const infoClickCount = ref(0);
const showModal = ref(false);
const shownTotal = ref('0.00');
let countUp: gsap.core.Tween | null = null;

const money = (value: number) => value.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 });

// The total counts up from zero when the dialog opens.
function startCounting(total: number) {
  countUp?.kill();
  if (window.matchMedia?.('(prefers-reduced-motion: reduce)').matches) {
    shownTotal.value = money(total);
    return;
  }
  const counter = { value: 0 };
  shownTotal.value = money(0);
  countUp = gsap.to(counter, { value: total, duration: 1.4, ease: 'power3.out', onUpdate: () => { shownTotal.value = money(counter.value); } });
}

async function getSeriesInfo() {
  try {
    const response = await DashboardService.getUserSeriesStats();
    seriesInfo.value = response.data;
  } catch (error) {
    console.error(error);
  }
}

async function getIssueInfo() {
  try {
    const response = await DashboardService.getUserIssueStats();
    issueInfo.value = response.data;
  } catch (error) {
    console.error(error);
  }
}

async function getRecentPurchases() {
  try {
    const response = await DashboardService.getRecentPurchaseList();
    recentPurchasedIssues.value = response.data;
  } catch (error) {
    console.error(error);
  }
}

// Five taps on the info icon reveal the total spent. Kept deliberately hidden.
async function handleInfoClick() {
  infoClickCount.value++;
  if (infoClickCount.value === 5) {
    infoClickCount.value = 0;
    try {
      const response = await DashboardService.getTotalSpent();
      showModal.value = true;
      startCounting(response.data.totalSpent);
    } catch (error) {
      console.error(error);
    }
  }
}

onMounted(() => {
  Promise.all([getSeriesInfo(), getIssueInfo(), getRecentPurchases()]);
});
</script>
