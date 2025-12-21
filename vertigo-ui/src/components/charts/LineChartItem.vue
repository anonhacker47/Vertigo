<template>
  <div class="flex flex-col items-center justify-center h-96 md:h-full w-full relative">
    <div class="card-title text-xl text-center justify-center mt-[1.3rem] font-extrabold text-[#F9FAFB]">
      Purchase per Month</div>
    <template v-if="hasData">
      <v-chart class="flex  w-full h-fit" :option="option" :autoresize="true" />
    </template>
    <template v-else>
      <div class="text-gray-400 text-lg text-center">No purchase data available to display</div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { use } from 'echarts/core'
import { LineChart } from 'echarts/charts'
import { GridComponent } from 'echarts/components'
import { SVGRenderer } from 'echarts/renderers'
import { onMounted, ref, provide, watch, computed } from 'vue';
use([GridComponent, LineChart, SVGRenderer])

import VChart, { THEME_KEY } from 'vue-echarts';

const hasData = computed(() => props.xData.length > 0 && props.yData.length > 0)

const props = defineProps({
  xData: {
    type: Array,
    required: true,
  },
  yData: {
    type: Array,
    required: true,
  },
});

provide(THEME_KEY, 'dark');

const option: any = ref({
  backgroundColor: 'transparent',
  darkMode: 'true',
  tooltip: {
    trigger: 'item',
  },
  xAxis: {
    type: 'category',
    data: props.yData,
  },
  yAxis: {
    type: 'value'
  },
  series: [
    {
      data: props.xData,
      type: 'line',
      // smooth: true
    }
  ]
});

// Watch for changes in props.xData and props.yData
watch(
  () => [props.xData, props.yData],
  ([newXData, newYData]) => {
    option.value = {
      ...option.value,
      xAxis: {
        ...option.value.xAxis,
        data: newYData,
      },
      series: [
        {
          ...option.value.series[0],
          data: newXData,
        }
      ]
    }
  },
  { deep: true }
);
</script>
