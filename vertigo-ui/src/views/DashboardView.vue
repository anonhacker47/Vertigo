<template>
  <div class="flex flex-col w-screen">
    <div class="w-full flex flex-col md:flex-row md:gap-12 gap-8 items-center md:h-40 mt-8 px-8 justify-around">
      <InsightCardItem :border="true" icon="collection" :multipleData="true" titleA="My Series" titleB="My Issues"
        :valueANumerator="seriesInfo.collectedSeriesCount" :value-a-denominator="seriesInfo.totalSeriesCount"
        :valueBNumerator="issueInfo.collectedIssueCount" :valueBDenominator="issueInfo.totalIssueCount" />

      <InsightCardItem :border="true" icon="readSeries" :multipleData="false" titleA="Series Read"
        :valueANumerator="seriesInfo.readSeriesCount" :valueADenominator="seriesInfo.totalSeriesCount" />

      <InsightCardItem :border="true" icon="readIssue" :multipleData="false" titleA="Issues Read" titleB="Issues Read"
        :valueANumerator="issueInfo.readIssueCount" :valueADenominator="issueInfo.totalIssueCount" />

      <AddSeriesCardItem />
    </div>
    <div class="w-full flex flex-col md:flex-row mt-8 flex-grow justify-around gap-8 pl-8 pr-8 mb-8 md:min-h-[66vh]">
      <div class="card relative basis-1/2 sm:w-[35%] items-center bg-base-100 shadow-xl">
        <PieChartItem :title="chartTitle" :data="chartData" />

        <div class="dropdown dropdown-end absolute top-3 right-3">
          <button @click="handleInfoClick" class="btn btn-circle btn-ghost btn-xs text-info">
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" class="w-4 h-4 stroke-current">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
            </svg>
          </button>
          <div
            class="card compact dropdown-content z-[1] shadow bg-base-100 border-green-400 border-2 rounded-box w-64">
            <div class="card-body">
              <h2 class="card-title">Explore insights from your collection!</h2>
              <p>Use the dropdowns below to filter and compare stats across different aspects of your collection.</p>
            </div>
          </div>
        </div>

        <div class="flex gap-4 pb-4 pr-4 pl-4">
          <div class="relative w-1/2">
            <select class="select select-primary select-bordered w-full" v-model="selectedType" @change="fetchData">
              <option v-for="(item, i) in chartTypeList" :key="i" :value="item.field">{{ item.Name }}</option>
            </select>
          </div>
          <div class="relative w-1/2">
            <select class="select  select-primary select-bordered w-full" v-model="selectedCategory"
              @change="fetchData">
              <option v-for="item in chartCategoryList" :key="item.Name" :value="item.field">{{ item.Name }}</option>
            </select>
          </div>
          <div class="relative w-1/2">
            <select class="select  select-primary select-bordered w-full" v-model="selectedCount" @change="fetchData">
              <option v-for="item in countList" :key="item.Name" :value="item.field">{{ item.Name }}</option>
            </select>
          </div>
        </div>

      </div>

      <div class="card w-full sm:w-[30%] card-compact relative bg-base-100 shadow-xl">
        <div
          class="card-title text-xl text-center justify-center pt-[1.3rem] font-extrabold text-[#F9FAFB]">
          Recent Purchases</div>
        <div class="mt-4 h-full w-full flex items-center justify-center">
          <SwiperCardItem v-if="recentPurchasedIssues && recentPurchasedIssues.length > 0"
            :recentPurchasedIssues="recentPurchasedIssues" />
          <div v-else class="flex items-center justify-center h-full text-gray-400 text-lg">
            No recent purchases found.
          </div>
        </div>
      </div>

      <div class="card relative basis-1/2 sm:w-[35%] flex items-center bg-base-100 shadow-xl">
        <LineChartItem :x-data="purchaseData" :y-data="dates" />
        <div class="mb-4 w-1/8 flex no-wrap items-center justify-center">
          <!-- <label for="year" class="mr-2 text-sm">Select Year:</label> -->
          <select v-model="selectedYear" id="year" class="select select-primary select-bordered w-full">
            <option v-for="year in years" :key="year" :value="year">{{ year }}</option>
          </select>
        </div>
      </div>

    </div>
  </div>
  <Dialog v-model:visible="showModal" modal header="💰 Total Spent" :style="{ width: '28rem' }"
    class="rounded-2xl shadow-2xl">
    <div class="flex flex-col items-center justify-center gap-4 p-6">
      <div class="text-4xl font-extrabold text-primary">
        {{ symbol }} {{ totalSpent }}
      </div>
      <div class="text-lg font-semibold text-gray-400">
        Impressive!
      </div>
      <div class="text-sm text-gray-400 italic">
        Keep collecting and expanding your library 📚
      </div>
    </div>
  </Dialog>
</template>

<script setup lang="ts">
import { useUserStore } from "../store/user";
import InsightCardItem from '../components/cards/InsightCardItem.vue'
import AddSeriesCardItem from '../components/cards/AddSeriesCardItem.vue'

import { ref, computed, onMounted, watch } from 'vue';
import PieChartItem from '../components/charts/PieChartItem.vue';
import LineChartItem from '../components/charts/LineChartItem.vue';
import SwiperCardItem from '../components/cards/SwiperCardItem.vue';
import DashboardService from '../services/DashboardService';

import { Series } from "@/types/series.types";
import { Dialog } from "primevue";
import getSymbolFromCurrency from "currency-symbol-map";

const userstore = useUserStore();
const { id: userId } = userstore.getUser();
const selectedType = ref('series');
const selectedCategory = ref('publisher');
const selectedCount = ref(10);

const seriesInfo = ref({ totalSeriesCount: 0, collectedSeriesCount: 0, readSeriesCount: 0 });
const issueInfo = ref({ totalIssueCount: 0, collectedIssueCount: 0, readIssueCount: 0 });
const chartData = ref([]);

const { preferred_currency: preferred_currency } = userstore.getUser();
const symbol = getSymbolFromCurrency(preferred_currency)


const recentPurchasedIssues = ref([]);

const selectedYear = ref(new Date().getFullYear())
const years = Array.from({ length: 8 }, (_, i) => new Date().getFullYear() - i)

const infoClickCount = ref(0);
const showModal = ref(false);
const totalSpent = ref(0);

const chartTypeList = [
  { Name: 'Series', field: 'series' },
  { Name: 'Issue', field: 'issue' },
];
const chartCategoryList = [
  { Name: 'Publisher', field: 'publisher' },
  { Name: 'Genre', field: 'genre' },
  { Name: 'Character', field: 'character' },
  { Name: 'Creator', field: 'creator' },
];

const countList = [
  { Name: '5', field: '5' },
  { Name: '10', field: '10' },
  { Name: '50', field: '50' },
  { Name: '100', field: '100' },
  { Name: 'All', field: '-1' },
];

async function getSeriesInfo() {
  try {
    const response = await DashboardService.getUserSeriesStats();
    seriesInfo.value.totalSeriesCount = response.data.totalSeriesCount;
    seriesInfo.value.collectedSeriesCount = response.data.collectedSeriesCount;
    seriesInfo.value.readSeriesCount = response.data.readSeriesCount;
  } catch (error) {
    console.log(error);
  }
}

async function getIssueInfo() {
  try {
    const response = await DashboardService.getUserIssueStats();
    issueInfo.value.totalIssueCount = response.data.totalIssueCount;
    issueInfo.value.collectedIssueCount = response.data.collectedIssueCount;
    issueInfo.value.readIssueCount = response.data.readIssueCount;
  } catch (error) {
    console.log(error);
  }
}

async function fetchData() {
  await getUserFieldCountAsync(Number(userId), selectedCategory.value, selectedType.value, selectedCount.value);
};

async function getUserFieldCountAsync(userId: Series["user"]["id"], field: string, type: string, count: number = 10) {
  try {
    const response = await DashboardService.getUserFieldCount(field, type, count);
    chartData.value = response.data;
  } catch (error) {
    console.log(error);
  }
}

async function getRecentPurchases() {
  try {
    const response = await DashboardService.getRecentPurchaseList();
    recentPurchasedIssues.value = response.data;
  } catch (error) {
    console.log(error);
  }
}

async function getPurchasesPerMonth(year: number) {
  try {
    const response = await DashboardService.getPurchasesPerMonth(year);
    dates.value = response.data.map((item: { month: any }) => item.month)
    purchaseData.value = response.data.map((item: { count: any }) => item.count)
  } catch (error) {
    console.log(error);
  }
}

watch(selectedYear, (newYear) => {
  getPurchasesPerMonth(newYear)
})

onMounted(async () => {
  await getSeriesInfo();
  await getIssueInfo();
  await fetchData();
  await getRecentPurchases();
  await getPurchasesPerMonth(selectedYear.value);
});

const dates = ref([]);
const purchaseData = ref([]);

const chartTitle = computed(() => {
  const selectedTypeName = selectedType.value === 'series' ? 'Series' : 'Issues';
  const selectedCategoryItem = chartCategoryList.find(item => item.field === selectedCategory.value);
  return `${selectedTypeName} by ${selectedCategoryItem.Name}`;
});

async function handleInfoClick() {
  infoClickCount.value++;

  if (infoClickCount.value === 5) {
    await getTotalSpent();
    showModal.value = true;
    infoClickCount.value = 0; // reset counter after showing
  }
}

async function getTotalSpent() {
  try {
    const response = await DashboardService.getTotalSpent();
    totalSpent.value = response.data.totalSpent; // adjust based on actual response
  } catch (error) {
    console.error(error);
  }
}

</script>

<style scoped></style>
