<template>
  <div class="mx-auto flex w-full max-w-page flex-col gap-7 px-4 pb-8 pt-6 md:min-h-[calc(100vh-var(--spacing-header))] md:px-8">
    <!-- the shelf in numbers -->
    <div class="grid grid-cols-2 items-center gap-x-6 gap-y-5 border-b border-white/8 pb-5 md:grid-cols-[1fr_1fr_1fr_auto]">
      <ShelfFigure :value="seriesInfo.totalSeriesCount" unit="series"
        :label="`${seriesInfo.collectedSeriesCount} fully collected · ${seriesInfo.readSeriesCount} fully read`"
        :ratio="pct(seriesInfo.collectedSeriesCount, seriesInfo.totalSeriesCount)" />
      <ShelfFigure :value="issueInfo.collectedIssueCount" :unit="`of ${issueInfo.totalIssueCount} issues`" label="owned"
        :ratio="pct(issueInfo.collectedIssueCount, issueInfo.totalIssueCount)" />
      <ShelfFigure :value="issueInfo.readIssueCount" unit="read" :label="`of the ${issueInfo.collectedIssueCount} you own`"
        :ratio="pct(issueInfo.readIssueCount, issueInfo.collectedIssueCount)" tone="read" />
        <RouterLink :to="{ name: 'AddSeries' }" custom v-slot="{ navigate }">
          <Button label="Add series"  icon="pi pi-plus" size="small" @click="navigate" />
        </RouterLink>
    </div>

    <!-- three panels, side by side, no scrolling on a desktop -->
    <div class="grid flex-1 grid-cols-1 gap-10 md:grid-cols-[7fr_6fr_7fr] md:gap-8">
      <section class="min-w-0" aria-label="Breakdown">
        <BreakdownDonut>
          <template #aside>
            <button class="btn btn-circle btn-ghost btn-xs text-info" type="button" aria-label="About this chart" @click="handleInfoClick">
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" class="h-4 w-4 stroke-current">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
              </svg>
            </button>
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

  <Dialog v-model:visible="showModal" modal header="💰 Total Spent" :style="{ width: '28rem' }" class="rounded-2xl shadow-2xl">
    <div class="flex flex-col items-center justify-center gap-4 p-6">
      <div class="text-4xl font-extrabold text-primary">{{ symbol }} {{ totalSpent }}</div>
      <div class="text-lg font-semibold text-gray-400">Impressive!</div>
      <div class="text-sm italic text-gray-400">Keep collecting and expanding your library 📚</div>
    </div>
  </Dialog>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue';
import { Dialog } from "primevue";
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
const totalSpent = ref(0);

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
      totalSpent.value = response.data.totalSpent;
      showModal.value = true;
    } catch (error) {
      console.error(error);
    }
  }
}

onMounted(() => {
  Promise.all([getSeriesInfo(), getIssueInfo(), getRecentPurchases()]);
});
</script>
