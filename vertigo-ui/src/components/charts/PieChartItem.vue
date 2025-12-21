<template>
  <div class="flex flex-col justify-center h-96 items-center md:h-full w-full relative">
    <div class="card-title text-xl text-center justify-center pt-[1.3rem] font-extrabold text-[#F9FAFB]">
      {{props.title}}</div>
    <v-chart v-if="props.data.length" class="w-full h-fit" :option="option" :autoresize="true" />
    <div v-else class="flex items-center justify-center w-full h-full text-gray-400 text-lg">
      No data available to display
    </div>
  </div>
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
      center: ['50%', '46%'],
      minShowLabelAngle: 2,
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

watch(() => props.data, (newValue) => {
  option.value.series[0].data = newValue;
});



</script>
