<template>
  <div class="flex items-center justify-center min-h-96 md:h-full w-full relative">
    <template v-if="hasData">
      <v-chart class="flex shrink-0 justify-center w-full h-full" :option="option" :autoresize="true" />
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
  title: {
    text: "Purchase per Month",
    left: 'center',
    padding: [25, 0, 0, 0],
    textStyle: {
      fontSize: '1.25rem',
      color: '#F9FAFB',
      fontFamily: 'Nunito',
      fontWeight: 'bold',

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
