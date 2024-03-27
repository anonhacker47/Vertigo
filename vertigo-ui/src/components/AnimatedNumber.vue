<template>
    <span ref="element">{{ animatedValue }}</span>
</template>

<script setup> 
import { ref, onMounted, watch } from 'vue';
import { gsap } from 'gsap';

const props = defineProps({
    number: {
        type: Number,
        required: true,
    },
})
const element = ref(null);
const animatedValue = ref(0);

watch(
    () => props.number,
    (newValue) => {
        gsap.to(element.value, {
            duration: 1,
            textContent: newValue,
            roundProps: { textContent: 1 },
        });
    },
);
</script>
