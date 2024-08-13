<template>
	<v-chart class="flex justify-center h-full w-full relative" :option="option" :autoresize="true" />
</template>

<script setup lang="ts">
import { use } from 'echarts/core';
import { PieChart } from 'echarts/charts';
import {
	TitleComponent,
	TooltipComponent,
	LegendComponent,
} from 'echarts/components';
import { SVGRenderer } from 'echarts/renderers'
import VChart, { THEME_KEY } from 'vue-echarts';
import { ref, provide, watch } from 'vue';

const props = defineProps({
	title: {
		type: String,
		required: true,
	},
	data: {
		type: Array,
		required: true,
	},
});

use([
	SVGRenderer,
	PieChart,
	TitleComponent,
	TooltipComponent,
	LegendComponent,
]);

provide(THEME_KEY, 'dark');


const option: any = ref({
  backgroundColor: 'transparent',
  darkMode: 'true',
  title: {
    text: props.title,
    left: 'center',
    padding: [25, 0, 0, 0],
    textStyle: {
      fontSize: '1.25rem',
      color: '#F9FAFB'
    }
  },
  tooltip: {
    trigger: 'item',
    formatter: '{b} : {c} ({d}%)',
  },
  
  // legend: {
  //   top: '15%',
  //   left: 'center'
  // },
  series: [
    {
      name: 'Comic Publishers',
      type: 'pie',
      radius: '45%',
      // padAngle: 5,
      center: ['50%', '53	%'],
	 minShowLabelAngle:2,
      // itemStyle: {
      //   borderRadius: 10,
      //   borderColor: '#0F172A',
      //   borderWidth: 2
      // },
      // label: {
      //   show: false,
      //   position: 'center',
      //   color:'white'
      // },
	//   label:{
	// 	show:true,
	// 	fontWeight:'medium',
	// 	color:'#c7d0dd'
	//   },
      data: props.data,
      emphasis: {
        itemStyle: {
          shadowBlur: 10,
          shadowOffsetX: 0,
          shadowColor: 'rgba(0, 0, 0, 0.5)',
        },
      },

    },
  ],
});

watch(() => props.title, (newValue) => {
  option.value.title.text = newValue;
});

watch(() => props.data, (newValue) => {
  option.value.series[0].data = newValue;
});



</script>
