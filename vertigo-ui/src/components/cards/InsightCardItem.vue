<template>
	<div class="card relative w-full h-full  bg-base-100 shadow-xl" :class="props.border ? `border border-gray-700`:''">
		<div class="card-body flex-row justify-between items-center">
			<!-- Card A -->
			<div v-if="selectedOption == 1" class="flex flex-col">
				<h2 class="card-title">{{props.titleA}}</h2>
				<span class="font-black text-5xl pt-4 text-gray-50">
					<AnimatedNumber :number="props.valueANumerator" /><span v-if="props.valueADenominator" class="font-black text-3xl text-gray-400">{{ "/" + props.valueADenominator }}</span>
				</span>
			</div>
			<!-- Card B -->
			<div v-if="selectedOption == 2" class="flex flex-col" role="tabpanel">
				<h2 class="card-title">{{props.titleB}}</h2>
				<span class="font-black text-5xl pt-4 text-gray-50 overflow-hidden">
					<AnimatedNumber :number="props.valueBNumerator" /><span v-if="props.valueBDenominator" class="font-black text-3xl text-gray-400">{{ "/" + props.valueBDenominator }}</span>
				</span>
			</div>

			<img :src="props.icon" alt="" class=" absolute right-6 w-24 h-24 ml-2  pt-2" />
		</div>
		<div class="absolute top-3 right-3" v-if="multipleData">
			<input type="radio" :name="props.titleA" class="radio w-4 h-4 radio-primary" v-model="selectedOption" value="1"
				checked />
			<input type="radio" :name="props.titleA" class="radio w-4 ml-1 h-4  radio-primary" v-model="selectedOption"
				value="2" />
		</div>
	</div>
</template>
<script setup>
import { ref } from 'vue';
import AnimatedNumber from 'src/components/AnimatedNumber.vue'

const props = defineProps({
	icon: String,
	border:Boolean,
	multipleData:Boolean,
	titleA:String,
	valueANumerator:Number,
	valueADenominator:Number,
	valueBNumerator:Number,
	valueBDenominator:Number,
	titleB:String,
})
const selectedOption = ref('1');
const multipleData = props.multipleData || false


</script>

<style scoped></style>
