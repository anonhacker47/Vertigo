<template>
  <div class="w-full flex flex-col items-center justify-center mt-4">
    <h1 class="text-3xl font-bold text-white"> {{ props.mode === 'edit' ? "Update" : "Add" }} {{ pascalType }}
    </h1>
  </div>
  <div class="flex flex-col md:flex-row items-center md:items-start justify-center p-6 gap-10 w-full">
    <div class="w-[20rem] max-h-[36rem]">
      <ImageUploader v-model="imageSrc" @image-change="onImageChange" />
    </div>


    <form @submit.prevent="onSubmit" class="card bg-base-100 shadow-2xl p-8 w-full max-w-xl flex flex-col gap-6">
      <div class="">
        <label class="label" for="entity-title">
          <span class="label-text font-medium">
            {{ pascalType }} Name
          </span>
        </label>
        <input type="text" id="entity-title" v-model="entityData.title" placeholder="Enter Name"
          class="input input-bordered w-full" required />
      </div>

      <div class="flex flex-col w-full">
        <label class="label" for="entity-description">
          <span class="label-text font-medium">
            Description
          </span>
          <span class="label-text-alt opacity-60">
            (Optional)
          </span>
        </label>

        <textarea v-model="entityData.description" id="entity-description" placeholder="Add an optional description"
          class="textarea textarea-bordered h-32 w-full" @input="countCharacters"></textarea>

        <p class="text-sm mt-1" :class="{ 'text-error': charCount > 3000, 'opacity-70': charCount <= 3000 }">
          {{ charCount }}/3000
        </p>
      </div>

      <div class="flex flex-col gap-2 w-full p-2">

        <div class="flex w-full gap-2">
          <button class="btn btn-neutral flex-1" @click.prevent="router.back()">Cancel</button>
          <button class="btn btn-primary flex-1" type="submit" :disabled="charCount > 3000 || !entityData.title">
            {{ props.mode === 'edit' ? "Update" : "Create" }} {{ pascalType }}
          </button>
        </div>

        <button v-if="props.mode === 'edit'" class="btn border-2 border-error w-full"
          @click.prevent="confirmDelete(entityData)">
          Delete {{ pascalType }}
        </button>

      </div>
    </form>

  </div>
</template>

<script setup lang="ts">
import { ref, watch } from "vue";
import { useRouter } from "vue-router";
import ImageUploader from "@/components/createSeries/ImageUploader.vue";
import { usePascalType } from "@/composables/usePascalType";
import { Entity } from "@/types/entity.types";
import { useToast } from "primevue";
import { useConfirmAction } from "@/composables/useConfirmAction";

const toast = useToast();
const { confirmAction } = useConfirmAction();
const thumbnailChanged = ref(false);

const props = defineProps<{
  type: string;
  title: string;
  initial?: Partial<Entity>;
  onSubmit: (data: FormData) => Promise<any>;
  onDelete?: () => Promise<any>;
  mode?: "create" | "edit";
}>();

const entityData = ref<Partial<Entity>>({
  title: props.initial?.title || "",
  description: props.initial?.description || "",
  thumbnail: props.initial?.thumbnail || "",
});

const router = useRouter();

const imageSrc = ref(new URL("../assets/dummy.webp", import.meta.url).href);

const charCount = ref(0);
function countCharacters() {
  charCount.value = entityData.value.description?.length || 0;
}

const pascalType = usePascalType(props.type);

function onImageChange(file: File | string) {
  thumbnailChanged.value = true;
  entityData.value.thumbnail = file;

  if (file instanceof File) {
    imageSrc.value = URL.createObjectURL(file);
  } else {
    imageSrc.value = file;
  }
}

watch(
  () => props.initial,
  (val) => {
    if (!val) return;
    entityData.value.title = val.title ?? "";
    entityData.value.description = val.description ?? "";
    entityData.value.thumbnail = val.thumbnail ?? "";

    if (val.thumbnail) imageSrc.value = val.thumbnail;
  },
  { deep: true }
);

async function onSubmit() {
  if (!entityData.value.title.trim()) return;

  const formData = new FormData();
  formData.append("title", entityData.value.title);
  formData.append("description", entityData.value.description || "");

if (thumbnailChanged.value) {
  formData.append("thumbnail", entityData.value.thumbnail as any);
}

  try {
    const response = await props.onSubmit(formData);
    const entityId = response?.id;

    if (entityId) {
      toast.add({ severity: 'success', summary: 'Success', detail: `${pascalType.value} created successfully!`, life: 3000 });
      router.push({ name: `${pascalType.value}Detail`, params: { Id: entityId, Link: response.slug } });
    } else {
      toast.add({ severity: 'error', summary: 'Failure', detail: `${pascalType} creation failed.`, life: 3000 });
    }
  } catch (error) {
    console.error(`Error creating ${pascalType}:`, error);
    toast.add({ severity: 'error', summary: 'Error', detail: error.message || 'Unexpected error.', life: 3000 });
  }
}

const confirmDelete = (entity: Partial<Entity>) => {
  confirmAction({
    message: `${pascalType.value} ${entity.title}`,
    header: "Confirm Deletion",
    acceptLabel: "Delete",
    severity: "danger",
    successMessage: `${pascalType.value} ${entity.title} deleted`,
    onAccept: () => deleteIssue(),
  });
};

const deleteIssue = async () => {
  try {
    await props.onDelete();
    toast.add({ severity: 'success', summary: 'Success', detail: `${pascalType.value} deleted successfully!`, life: 3000 });
    router.push({ name: `${pascalType.value}List` });
  } catch (error) {
    console.error(`Error creating ${pascalType}:`, error);
    toast.add({ severity: 'error', summary: 'Error', detail: error.message || `${pascalType} deletion failed.`, life: 3000 });
  }
}
</script>
