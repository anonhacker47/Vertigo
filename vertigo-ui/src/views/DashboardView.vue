<template>
  <div class="flex flex-col h-[88vh] w-screen">
    <!-- <div class="w-full h-24 flex items-center ml-10 pt-4 pb-4">
      <span class="text-4xl font-bold text-primary">Hello, anonhacker</span>
    </div> -->
    <div class="w-full flex gap-12 items-center h-40 pt-4 pl-8 pr-8 justify-around">
      <InsightCardItem :border="true" :icon="collectionIcon" :multipleData="true" titleA="My Series" titleB="My Issues"
        :valueANumerator="seriesInfo.collectedSeriesCount" :value-a-denominator="seriesInfo.totalSeriesCount" :value-b-numerator="seriesInfo.totalSeriesCount" :valueBNumerator="issueInfo.collectedIssueCount" :valueBDenominator="issueInfo.totalIssueCount" />
        
      <InsightCardItem :border="true" :icon="readIcon" :multipleData="false" titleA="Series Read"
        :valueANumerator="seriesInfo.readSeriesCount" :valueADenominator="seriesInfo.totalSeriesCount" />

      <InsightCardItem :border="true" :icon="readIssueIcon" :multipleData="false" titleA="Issues Read"
        titleB="Issues Read" :valueANumerator="issueInfo.readIssueCount"  :valueADenominator="issueInfo.totalIssueCount" />

      <AddSeriesCardItem />
    </div>
    <div class="w-full flex mt-8 justify-around gap-8 pl-8 pr-8 mb-8 h-full">
      <div class="card relative flex justify-center w-full  basis-1/2  items-center bg-base-100 shadow-xl">
        <PieChartItem :title="chartTitle" :data="chartData" />

        <div class="dropdown dropdown-end absolute top-3 right-3">
          <div tabindex="0" role="button" class="btn btn-circle btn-ghost btn-xs text-info">
            <svg tabindex="0" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"
              class="w-4 h-4 stroke-current">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
            </svg>
          </div>
          <div tabindex="0" class="card compact dropdown-content z-[1] shadow bg-base-100 rounded-box w-64">
            <div tabindex="0" class="card-body">
              <h2 class="card-title">You needed more info?</h2>
              <p>Here is a description!</p>
            </div>
          </div>
        </div>

        <div class="flex  gap-4 pb-4 pr-4 pl-4 w-full">
          <div class="relative w-1/2">
            <select class="select select-primary select-bordered w-full" v-model="selectedType" @change="fetchData">
              <option v-for="(item, i) in chartTypeList" :key="i" :value="item.field">{{item.Name}}</option>
            </select>
          </div>
          <div class="relative w-1/2">
            <select class="select  select-primary select-bordered w-full" v-model="selectedCategory" @change="fetchData">
              <option v-for="item in chartCategoryList" :key="item.Name" :value="item.field">{{item.Name}}</option>
            </select>
          </div>
        </div>

      </div>
      
      <div class="card card-compact relative basis-1/3 w-full bg-base-100 shadow-xl">
        <div
          class="card-title text-xl text-center font-['Microsoft_YaHei'] justify-center pt-[1.3rem] font-extrabold text-[#F9FAFB]">
          Recent Purchases </div>
        <div class="mt-6">
          <SwiperCardItem :recentPurchasedIssues="recentPurchasedIssues" />
        </div>
      </div>
        
        <div class="card relative basis-1/2 w-full flex bg-base-100 shadow-xl">
        <LineChartItem :x-data="purchaseData" :y-data="dates" />
        </div>

    </div>
  </div>
</template>

<script setup>
import HeaderItem from '../components/HeaderItem.vue';
import collectionIcon from '@/assets/collection.svg'
import readIcon from '@/assets/read.svg'
import forwardIcon from '@/assets/forward.svg'
import addIcon from '@/assets/add.svg'
import readIssueIcon from '@/assets/readIssue.svg'
import InsightCardItem from '../components/cards/InsightCardItem.vue'
import AddSeriesCardItem from '../components/cards/AddSeriesCardItem.vue'

import { ref, computed,onMounted } from 'vue';
import PieChartItem from '../components/charts/PieChartItem.vue';
import LineChartItem from '../components/charts/LineChartItem.vue';
import SwiperCardItem from '../components/cards/SwiperCardItem.vue';
import DashboardService from '../services/DashboardService';
import TokenService from '../services/TokenService';

const userId = TokenService.getUser();

const selectedType = ref('series');
const selectedCategory = ref('publisher');

const seriesInfo = ref({ totalSeriesCount: 0, collectedSeriesCount: 0, readSeriesCount: 0 });
const issueInfo = ref({ totalIssueCount: 0, collectedIssueCount: 0, readIssueCount: 0 });
const chartData =ref([]);

const recentPurchasedIssues = ref([]);

const chartTypeList = [
  { Name: 'Series', field: 'series' },
  { Name: 'Issue', field: 'issue' },
];
const chartCategoryList = [
  { Name: 'Publisher', field: 'publisher' },
  { Name: 'Genre', field: 'genre' },
  { Name: 'Main Char/Team', field: 'main_char' },
  { Name: 'Writer', field: 'writer' },
  { Name: 'Artist', field: 'artist' },
  { Name: 'Editor', field: 'editor' },
];
async function getSeriesInfo() {
  try {
    const response = await DashboardService.getUserSeriesStats(userId);
    seriesInfo.value.totalSeriesCount = response.data.totalSeriesCount;
    seriesInfo.value.collectedSeriesCount = response.data.collectedSeriesCount;
    seriesInfo.value.readSeriesCount = response.data.readSeriesCount;
  } catch (error) {
    console.log(error);
  }
}

async function getIssueInfo() {
  try {
    const response = await DashboardService.getUserIssueStats(userId);
    issueInfo.value.totalIssueCount = response.data.totalIssueCount;
    issueInfo.value.collectedIssueCount = response.data.collectedIssueCount;
    issueInfo.value.readIssueCount = response.data.readIssueCount;
    console.log(issueInfo.value.totalIssueCount);
  } catch (error) {
    console.log(error);
  }
}

async function fetchData() {
  await getUserFieldCountAsync(userId, selectedCategory.value, selectedType.value);
};

async function getUserFieldCountAsync(userId, field, type) {
  try {
    const response = await DashboardService.getUserFieldCount(userId, field, type);
    chartData.value = response.data;
    // console.log(chartData.value);
  } catch (error) {
    console.log(error);
  }
}

async function getRecentPurchases() {
  try {
    const response = await DashboardService.getRecentPurchaseList(userId);
    recentPurchasedIssues.value = response.data;
  } catch (error) {
    console.log(error);
  }
}

async function getPurchasesPerMonth() {
  try {
    const response = await DashboardService.getPurchasesPerMonth(userId);
    dates.value = response.data.map(item => item.month)
    purchaseData.value = response.data.map(item => item.count)
    
  } catch (error) {
    console.log(error);
  }
}


onMounted(async () => {
  await getSeriesInfo();
  await getIssueInfo();
  await fetchData();
  await getRecentPurchases();
  await getPurchasesPerMonth();
});

// const dates = ref(['Jan', 'Feb', 'Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']);
// const purchaseData = ref(Array.from({length: 12}, () => Math.floor(Math.random() * 21)));

const dates = ref([]);
const purchaseData = ref([]);

const chartTitle = computed(() => {
  const selectedTypeName = selectedType.value === 'series' ? 'Series' : 'Issues';
  const selectedCategoryItem = chartCategoryList.find(item => item.field === selectedCategory.value);
  return `${selectedTypeName} by ${selectedCategoryItem.Name}`;
});

</script>

<style scoped></style>