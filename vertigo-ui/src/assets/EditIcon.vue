<template>
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32" id="edit">
        <g data-name="81 Edit">
            <path :fill="fillColor"
                d="M24,29.5H6A3.5,3.5,0,0,1,2.5,26V8A3.5,3.5,0,0,1,6,4.5h9a1.5,1.5,0,0,1,0,3H6a.5.5,0,0,0-.5.5V26a.5.5,0,0,0,.5.5H24a.5.5,0,0,0,.5-.5V17a1.5,1.5,0,0,1,3,0v9A3.5,3.5,0,0,1,24,29.5Z">
            </path>
            <path :fill="fillColor"
                d="M12,21.5a1.5,1.5,0,0,1-1.49-1.69l.56-4.36a1.52,1.52,0,0,1,.42-.87L22.35,3.73a4.19,4.19,0,1,1,5.92,5.92L17.42,20.51a1.52,1.52,0,0,1-.87.42l-4.36.56Zm4.36-2.05h0ZM14,16.34l-.25,1.93L15.66,18,26.15,7.53a1.18,1.18,0,0,0,0-1.68,1.21,1.21,0,0,0-1.68,0Z">
            </path>
        </g>
    </svg>
</template>

<script setup lang="ts">
const props = defineProps({
  fillColor: String
});
</script>