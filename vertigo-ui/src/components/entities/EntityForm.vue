<template>
  <form
    @submit.prevent="handleSubmit"
    class="card bg-base-100 shadow-2xl p-8 w-full max-w-xl flex flex-col gap-6"
  >
    <!-- Title -->
    <div class="">
      <label class="label">
        <span class="label-text">{{pascalType}} Name</span>
      </label>
      <input
        type="text"
        v-model="local.title"
        placeholder="Enter Name"
        class="input input-bordered w-full"
        required
      />
    </div>

    <!-- Description -->
    <div class=" relative">
      <label class="label">
        <span class="label-text">Description (optional)</span>
      </label>

      <textarea
        v-model="local.description"
        placeholder="Add an optional description"
        class="textarea textarea-bordered h-32"
        @input="countCharacters"
      ></textarea>

      <p
        class="text-sm mt-1"
        :class="{ 'text-error': charCount > 1250, 'opacity-70': charCount <= 1250 }"
      >
        {{ charCount }}/1250
      </p>
    </div>

    <!-- Buttons -->
    <div class="flex justify-between mt-6">
      <button class="btn btn-error" @click.prevent="$emit('cancel')">Cancel</button>
      <button class="btn btn-primary" type="submit" :disabled="charCount > 1250 || !local.title">
        Create {{ pascalType }}
      </button>
    </div>
  </form>
</template>

<script setup lang="ts">
import { usePascalType } from "@/composables/usePascalType";
import { reactive, watch, ref } from "vue";

const props = defineProps({
  modelValue: Object,
  type:String
});
const emit = defineEmits(["update:modelValue", "submit", "cancel"]);

const local = reactive({ ...props.modelValue });

watch(local, () => {
  emit("update:modelValue", { ...local });
}, { deep: true });

const charCount = ref(0);
function countCharacters() {
  charCount.value = local.description?.length || 0;
}

watch(() => props.modelValue.thumbnail, (newThumb) => {
  local.thumbnail = newThumb;
});

function handleSubmit() {
  if (!local.title.trim()) return;
  emit("submit");
}

const pascalType = usePascalType(props.type);

</script>
