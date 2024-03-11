<template>
  <div class="flex flex-col h-screen w-screen">
    <HeaderItem />
    <!-- <div class="w-full h-24 flex items-center ml-10 pt-4 pb-4">
      <span class="text-4xl font-bold text-primary">Hello, anonhacker</span>
    </div> -->
    <div class="w-full flex gap-12 items-center h-40 pt-4 pl-8 pr-8 justify-around">
      <InsightCardItem :border="true" :icon="collectionIcon" :multipleData="true" titleA="My Series" titleB="My Issues"
        :valueANumerator="15" :valueBNumerator="35" :valueBDenominator="80" />
      <InsightCardItem :border="true" :icon="readIcon" :multipleData="false" titleA="Series Read" titleB="Issues Read"
        :valueANumerator="15" :valueBNumerator="35" :valueBDenominator="80" />
      <InsightCardItem :border="true" :icon="readIssueIcon" :multipleData="false" titleA="Issues Read"
        titleB="Issues Read" :valueANumerator="15" :valueBNumerator="35" :valueBDenominator="80" />
      <AddSeriesCardItem :icon="addIcon" />
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
            <select class="select select-primary select-bordered w-full" v-model="selectedType">
              <option>Series</option>
              <option>Issues</option>
            </select>
          </div>
          <div class="relative w-1/2">
            <select class="select  select-primary select-bordered w-full" v-model="selectedCategory">
              <option>Publisher</option>
              <option>Genre</option>
              <option>Main Char/Team</option>
              <option>Writer</option>
              <option>Artist</option>
            </select>
          </div>
        </div>

      </div>
      
      <div class="card card-compact relative basis-1/3 w-full flex bg-base-100 shadow-xl">
        <div
          class="card-title text-xl text-center font-['Microsoft_YaHei'] justify-center pt-[1.3rem] font-extrabold text-[#F9FAFB]">
          Recent Purchases </div>
        <SwiperCardItem />
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
import addIcon from '@/assets/add.svg'
import readIssueIcon from '@/assets/readIssue.svg'
import InsightCardItem from '../components/cards/InsightCardItem.vue'
import AddSeriesCardItem from '../components/cards/AddSeriesCardItem.vue'

import { ref, computed } from 'vue';
import PieChartItem from '../components/charts/PieChartItem.vue';
import LineChartItem from '../components/charts/LineChartItem.vue';
import SwiperCardItem from '../components/cards/SwiperCardItem.vue';

const selectedType = ref('Series');
const selectedCategory = ref('Publisher');

const chartData = [
  { value: 1548, name: 'Marvel' },
  { value: 310, name: 'DC Comics' },
  { value: 345, name: 'Dark Horse Comics' },
  { value: 1234, name: 'Vertigo' },
  { value: 135, name: 'Image Comics' },
  { value: 190, name: 'Milestone Media' },
];

const dates = ['Jan', 'Feb', 'Mar','Apr','May']
const purchaseData = [2,8, 10,3,5]

const chartTitle = computed(() => {
  let title = '';
  if (selectedType.value === 'Series') {
    title = 'Series by ';
  } else if (selectedType.value === 'Issues') {
    title = 'Issues by ';
  }

  title += selectedCategory.value;
  return title;
});

</script>

<style scoped></style>