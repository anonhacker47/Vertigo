<template>
    <div class="mx-auto p-6 space-y-10 text-center">
        <h1 class="text-3xl font-bold text-primary">Settings</h1>
        <div class="flex flex-col lg:flex-row flex-wrap gap-8 w-full justify-center items-stretch md:px-4">
            <!-- 🔹 PROFILE SETTINGS -->
            <section
                class="border-2 border-sky-900 rounded-xl flex flex-col lg:flex-row gap-6 p-6 w-full lg:w-auto max-w-[40rem]">
                <!-- Profile Picture -->
                <section class="w-full lg:w-1/2 rounded-xl">
                    <h2 class="text-xl font-semibold mb-2">Profile Picture</h2>
                    <p class="text-sm text-sky-600 mb-4">
                        Upload a profile picture for your account.
                    </p>
                    <div class="w-full">
                        <ImageUploader v-model="imagesrc" @image-change="onImageChange" />
                    </div>
                </section>

                <!-- Preferred Currency -->
                <section class="w-full lg:w-1/2 flex flex-col justify-between gap-6">
                    <div>
                        <h2 class="text-xl font-semibold mb-2">Preferred Currency</h2>
                        <p class="text-sm text-sky-600 mb-4">
                            Select your preferred currency.
                        </p>
                        <select v-model="preferredCurrency"
                            class="w-full select rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500">
                            <option v-for="currency in currencyList" :key="currency.code" :value="currency.code">
                                {{ currency.code }} - {{ currency.currency }}
                            </option>
                        </select>
                    </div>

                    <div class="flex justify-end gap-4">
                        <button @click="cancelSettings"
                            class="bg-gray-200 text-gray-700 px-6 py-2 rounded-lg hover:bg-gray-300 transition-all ">
                            Cancel
                        </button>
                        <button @click="saveProfileSettings"
                            class="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 transition-all ">
                            Save Profile
                        </button>
                    </div>
                </section>
            </section>

            <!-- PASSWORD SETTINGS -->
            <section
                class="border-2 border-sky-900 rounded-xl p-6 flex flex-col justify-between gap-6 w-full lg:w-[32rem]">
                <div>
                    <h2 class="text-xl font-semibold">Change Password</h2>
                    <p class="text-sm text-sky-600 mb-4">
                        Update your account password securely.
                    </p>

                    <div class="space-y-4 my-6">
                        <input type="password" v-model="oldPassword" placeholder="Old Password"
                            class="w-full p-3 input rounded-md focus:outline-none input-primary" />
                        <input type="password" v-model="newPassword" placeholder="New Password"
                            class="w-full p-3  rounded-md input focus:outline-none input-primary" />
                        <input type="password" v-model="confirmPassword" placeholder="Confirm New Password"
                            class="w-full p-3  rounded-md input input-primary" />
                    </div>
                </div>

                <div class="flex justify-end">
                    <button @click="changePassword"
                        class="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 transition-all ">
                        Change Password
                    </button>
                </div>
            </section>

            <!-- DATA MANAGEMENT -->
            <section class="border-2 border-sky-900 rounded-xl p-6 flex flex-col gap-6 w-full lg:w-[28rem]">
                <!-- Export Section -->
                <div class="space-y-3">
                    <h2 class="text-xl font-semibold">Export Collection</h2>
                    <p class="text-sm text-sky-600">
                        Download your comic series and issue data as an Excel (.xlsx) file.
                    </p>
                    <button @click="handleExport"
                        class="w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold py-3 px-4 rounded-md transition duration-200 ease-in-out focus:outline-none focus:ring-2 focus:ring-blue-500">
                        📤 Export to Excel
                    </button>
                </div>

                <div class="border-t border-gray-200 my-2"></div>

                <!-- Clean Section -->
                <div class="space-y-3">
                    <div class="flex items-center gap-2 text-red-600">
                        <svg class="w-5 h-5" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round"
                                d="M13 16h-1v-4h-1m1-4h.01M12 9v2m0 4v.01m0 0h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                        </svg>
                        <h3 class="text-md font-semibold">Clean Data</h3>
                    </div>
                    <p class="text-sm text-red-500">
                        This will permanently delete <strong>all your saved Series and Issues</strong>. This action
                        <u>cannot be undone</u>. Please proceed with caution.
                    </p>
                    <button @click="confirmClean"
                        class="w-full bg-red-600 hover:bg-red-700 text-white font-semibold py-3 px-4 rounded-md transition duration-200 ease-in-out focus:outline-none focus:ring-2 focus:ring-red-500">
                        🗑️ Clean Data Permanently
                    </button>
                </div>
            </section>

            <ConfirmDialog />
        </div>

    </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from "vue";
import { useUserStore } from "@/store/user";
import ImageUploader from "@/components/createSeries/ImageUploader.vue";
import AuthenticationService from "@/services/AuthenticationService";
import { useToast } from "primevue/usetoast";
import { useConfirm } from "primevue/useconfirm";
import currencyCodes from "currency-codes";

const toast = useToast();
const confirm = useConfirm();
const userStore = useUserStore();

const imagesrc = ref("");
const image = ref("");
const preferredCurrency = ref("");
const oldPassword = ref("");
const newPassword = ref("");
const confirmPassword = ref("");

const user = computed(() => userStore.getUser() ?? {});

const uniqueCurrencies = Array.from(
    new Map(currencyCodes.data.map((c) => [c.code, c])).values()
);
const currencyList = uniqueCurrencies.filter((c) => !!c.code && !!c.currency);

watch(
    () => user.value?.preferred_currency,
    (newVal) => {
        if (newVal) preferredCurrency.value = newVal;
    },
    { immediate: true }
);

function onImageChange(file: File | string) {
    image.value = file;
    imagesrc.value = file instanceof File ? URL.createObjectURL(file) : file;
}

// 🔹 Save profile (image + currency)
async function saveProfileSettings() {
    try {
        const formData = new FormData();
        if (image.value) formData.append("profile_picture", image.value);
        if (preferredCurrency.value)
            formData.append("preferred_currency", preferredCurrency.value);

        const response = await AuthenticationService.updateUser(formData);
        userStore.addUser(response.data);

        toast.add({
            severity: "success",
            summary: "Updated",
            detail: "Profile updated successfully.",
            life: 3000,
        });
    } catch (error: any) {
        toast.add({
            severity: "error",
            summary: "Failed",
            detail: error.message || "Failed to update profile.",
            life: 3000,
        });
    }
}

// 🔹 Change password only
async function changePassword() {
    if (!oldPassword.value || !newPassword.value || !confirmPassword.value) {
        toast.add({
            severity: "warn",
            summary: "Missing Fields",
            detail: "All password fields are required.",
            life: 3000,
        });
        return;
    }

    if (newPassword.value !== confirmPassword.value) {
        toast.add({
            severity: "warn",
            summary: "Mismatch",
            detail: "New passwords do not match.",
            life: 3000,
        });
        return;
    }

    try {
        await AuthenticationService.updateUser({
            old_password: oldPassword.value,
            password: newPassword.value,
        });
        toast.add({
            severity: "success",
            summary: "Password Changed",
            detail: "Your password was updated successfully.",
            life: 3000,
        });
        oldPassword.value = "";
        newPassword.value = "";
        confirmPassword.value = "";
    } catch (error: any) {
        toast.add({
            severity: "error",
            summary: "Failed",
            detail: error.message || "Failed to change password.",
            life: 3000,
        });
    }
}

async function cancelSettings() {
    const user = userStore.getUser();
    try {
        imagesrc.value = await AuthenticationService.getUserPicture();
    } catch (e) {
        console.error("Failed to load profile picture:", e);
    }
    image.value = "";
    preferredCurrency.value = user?.preferred_currency ?? "";
}

const handleExport = async () => {
    try {
        const data = await AuthenticationService.exportCollection();
        const url = window.URL.createObjectURL(new Blob([data]));
        const link = document.createElement("a");
        link.href = url;
        link.setAttribute("download", "comic_collection.xlsx");
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        window.URL.revokeObjectURL(url);
        toast.add({
            severity: "success",
            summary: "Export Successful",
            detail: "Your comic collection has been downloaded.",
            life: 3000,
        });
    } catch (error) {
        toast.add({
            severity: "error",
            summary: "Export Failed",
            detail: "There was a problem exporting your collection.",
            life: 4000,
        });
    }
};

const confirmClean = () => {
    confirm.require({
        message: "This will permanently delete all your series and issues. Continue?",
        header: "Confirm Deletion",
        icon: "pi pi-exclamation-triangle",
        acceptLabel: "Yes, Delete",
        rejectLabel: "Cancel",
        acceptClass: "p-button-danger",
        accept: async () => {
            try {
                await AuthenticationService.deleteAllData();
                toast.add({
                    severity: "success",
                    summary: "Data Deleted",
                    detail: "Your collection was deleted successfully.",
                    life: 3000,
                });
            } catch {
                toast.add({
                    severity: "error",
                    summary: "Error",
                    detail: "Failed to delete your data.",
                    life: 3000,
                });
            }
        },
        reject: () => {
            toast.add({
                severity: "info",
                summary: "Cancelled",
                detail: "Your data is safe.",
                life: 3000,
            });
        },
    });
};

onMounted(async () => {
    const user = userStore.getUser();
    if (user?.profile_picture) {
        try {
            imagesrc.value = await AuthenticationService.getUserPicture();
        } catch (e) {
            console.error("Failed to load profile picture:", e);
        }
    }
});
</script>
