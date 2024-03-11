<template>
	<v-chart class="flex justify-center h-full w-full relative" :option="option" :autoresize="true" />
</template>

<script setup>
import { use } from 'echarts/core'
import { LineChart } from 'echarts/charts'
import { GridComponent } from 'echarts/components'
import { SVGRenderer } from 'echarts/renderers'

use([GridComponent, LineChart, SVGRenderer])

import VChart, { THEME_KEY } from 'vue-echarts';
import { ref, provide, watch } from 'vue';

const props = defineProps({
	// title: {
	// 	type: String,
	// 	required: true,
	// },
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

const option = {
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
};

// watch(() => props.title, (newValue) => {
//   option.value.title.text = newValue;
// });

// watch(() => props.data, (newValue) => {
//   option.value.series[0].data = newValue;
// });



</script>
