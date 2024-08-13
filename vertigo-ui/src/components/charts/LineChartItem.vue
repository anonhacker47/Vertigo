<template>
  <v-chart class="flex justify-center h-full w-full relative" :option="option" :autoresize="true" />
</template>

<script setup lang="ts">
import { use } from 'echarts/core'
import { LineChart } from 'echarts/charts'
import { GridComponent } from 'echarts/components'
import { SVGRenderer } from 'echarts/renderers'
import { onMounted, ref, provide, watch } from 'vue';
use([GridComponent, LineChart, SVGRenderer])

import VChart, { THEME_KEY } from 'vue-echarts';

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
  title: {
    text: "Purchase per Month",
    left: 'center',
    padding: [25, 0, 0, 0],
    textStyle: {
      fontSize: '1.25rem',
      color: '#F9FAFB'
    }
  },
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

// onMounted(() => {
//   console.log("xData:", props.xData);
//   console.log("yData:", props.yData);
// });
</script>
