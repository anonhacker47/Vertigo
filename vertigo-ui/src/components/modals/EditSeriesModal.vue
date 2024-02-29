<template>
  <dialog  class="modal w-full h-full" :class="modalRef ?'modal-open':'modal'"  @keydown.esc="$emit('esc')">
        <div class="modal-box border-b-2 border-sky-600" style="max-width: calc(94vw);">
          <h3 class="font-bold text-lg">{{ title }}</h3>
          <p class="py-4"></p>
          <!-- <div> -->
            <slot>

            </slot>
          <!-- </div> -->
          <div class="modal-action">
            <form method="dialog"  >
              <!-- if there is a button in form, it will close the modal -->
              <button class="btn" @click="$emit('close')">Close</button>
              <button class="btn btn-primary ml-5">Submit</button>
            </form>
          </div>
        </div>
      </dialog>
</template>
<script setup>
import EditIcon from '../../assets/EditIcon.vue';
import { ref } from 'vue';

const props = defineProps({
  title: String,
  modalRef: Boolean
});

const isOpen = ref(false)


</script>

<style></style>