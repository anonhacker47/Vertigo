<template>
    <span ref="element">{{ animatedValue }}</span>
</template>

<script setup> 
import { ref, onMounted } from 'vue';
import { gsap } from 'gsap';

const props = defineProps({
    number: {
        type: Number,
        required: true,
    },
})
const element = ref(null);
const animatedValue = ref(0);

onMounted(() => {
    gsap.to(element.value, { duration: 1, textContent: props.number, roundProps: { textContent: 1 } });
});
</script>