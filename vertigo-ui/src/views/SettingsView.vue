<template>
    <div class="mx-auto p-6 space-y-10">
        <h1 class="text-3xl font-bold text-primary">Settings</h1>

        <div class="flex flex-row gap-4 w-full justify-around ">

            <!-- Profile Picture -->
            <section class="max-w-2xl border-sky-900 border-2  rounded-xl shadow p-6">
                <h2 class="text-xl font-semibold mb-2">Profile Picture</h2>
                <p class="text-sm text-sky-600 mb-4">Upload a profile picture for your account.</p>
                <div class="h-[36rem] w-full">
                    <ImageUploader v-model="imagesrc" @image-change="onImageChange" />
                </div>
            </section>

            <!-- Preferred Currency -->
            <section class="border-sky-900 border-2 rounded-xl shadow p-6 flex flex-col gap-4">
                <div>

                    <h2 class="text-xl font-semibold mb-2">Preferred Currency</h2>
                    <p class="text-sm text-sky-600 mb-4">Select your preferred currency for price display.</p>
                    <select v-model="preferredCurrency"
                        class="w-full p-3 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500">
                        <option v-for="currency in currencyList" :key="currency.code" :value="currency.code">
                            {{ currency.code }} - {{ currency.currency }}
                        </option>
                    </select>
                </div>
                <div>

                    <h2 class="text-xl font-semibold my-2">Change Password</h2>
                    <p class="text-sm text-sky-600 mb-4">Update your account password.</p>
                    <div class="space-y-4">
                        <input type="password" v-model="oldPassword" placeholder="Old Password"
                            class="w-full p-3 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500" />
                        <input type="password" v-model="newPassword" placeholder="New Password"
                            class="w-full p-3 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500" />
                    </div>
                </div>
            </section>


            <section class="border-2 border-sky-900 rounded-xl shadow p-6 flex flex-col gap-6">
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

                <!-- Divider -->
                <div class="border-t border-gray-200 my-2"></div>

                <!-- Clean Section -->
                <div class="space-y-3">
                    <div class="flex items-center gap-2 text-red-600">
                        <svg class="w-5 h-5" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round"
                                d="M13 16h-1v-4h-1m1-4h.01M12 9v2m0 4v.01m0 0h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                        </svg>
                        <h3 class="text-md font-semibold">Danger Zone: Clean Data</h3>
                    </div>
                    <p class="text-sm text-red-500">
                        This will permanently delete <strong>all your saved series and issues</strong>. This action
                        <u>cannot be undone</u>. Please proceed with caution.
                    </p>
                    <button @click="confirmClean"
                        class="w-full bg-red-600 hover:bg-red-700 text-white font-semibold py-3 px-4 rounded-md transition duration-200 ease-in-out focus:outline-none focus:ring-2 focus:ring-red-500">
                        🗑️ Clean Data Permanently
                    </button>
                </div>
            </section>

            <!-- PrimeVue ConfirmDialog component -->
            <ConfirmDialog />

        </div>
        <div class="flex justify-end gap-4">
            <button @click="cancelSettings"
                class="bg-gray-200 text-gray-700 px-6 py-2 rounded-lg hover:bg-gray-300 transition-all shadow">
                Cancel
            </button>
            <button @click="saveSettings"
                class="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 transition-all shadow">
                Save Settings
            </button>
        </div>
    </div>
</template>


<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'
import { useUserStore } from '@/store/user'
import currencyCodes from 'currency-codes'
import ImageUploader from '@/components/createSeries/ImageUploader.vue'
import AuthenticationService from '@/services/AuthenticationService'
import { useToast } from "primevue/usetoast";
import { useConfirm } from 'primevue/useconfirm'

const preferredCurrency = ref()
const userStore = useUserStore()
const toast = useToast();
const confirm = useConfirm()

// Reactive ref for profile picture source
const imagesrc = ref('')
const image = ref('')
// Computed property for user's profile picture from the store
const user = computed(() => userStore.getUser() ?? {})

const oldPassword = ref('')
const newPassword = ref('')

watch(
    () => user.value?.preferred_currency,
    (newVal) => {
        if (newVal) {
            console.log(newVal);

            preferredCurrency.value = newVal
        }
    },
    { immediate: true }
)

const confirmClean = () => {
    confirm.require({
        message: 'This will permanently delete all your series and issues. Continue?',
        header: 'Confirm Deletion',
        icon: 'pi pi-exclamation-triangle',
        acceptLabel: 'Yes, Delete',
        rejectLabel: 'Cancel',
        acceptClass: 'p-button-danger',
        accept: async () => {
            try {
                await handleClean()
                toast.add({
                    severity: 'success',
                    summary: 'Data Deleted',
                    detail: 'Your collection was deleted successfully.',
                    life: 3000
                })
            } catch (err) {
                console.error('Failed to delete user data:', err)
                toast.add({
                    severity: 'error',
                    summary: 'Error',
                    detail: 'Failed to delete your data.',
                    life: 3000
                })
            }
        },
        reject: () => {
            toast.add({
                severity: 'info',
                summary: 'Cancelled',
                detail: 'Your data is safe.',
                life: 3000
            })
        }
    })
}

// On image change
function onImageChange(file: File | string) {
    image.value = file
    if (file instanceof File) {
        imagesrc.value = URL.createObjectURL(file)
    } else if (typeof file === 'string') {
        imagesrc.value = file
    }

    console.log("Image Changed:", image.value)
}

// Filter unique currencies
const uniqueCurrencies = Array.from(
    new Map(currencyCodes.data.map(c => [c.code, c])).values()
)
const currencyList = uniqueCurrencies.filter(c => !!c.code && !!c.currency)


async function saveSettings() {
    try {
        const formData = new FormData()

        // If it's a file input (e.g., from <input type="file">)
        formData.append('profile_picture', image.value)


        if (preferredCurrency.value) {
            formData.append('preferred_currency', preferredCurrency.value)
        }

        if (newPassword.value) {
            if (!oldPassword.value) {
                toast.add({
                    severity: 'warn',
                    summary: 'Missing Field',
                    detail: 'Old password is required to change password.',
                    life: 3000
                })
                return
            }
            formData.append('old_password', oldPassword.value)
            formData.append('password', newPassword.value)
        }

        // Make the request with multipart/form-data
        const response = await AuthenticationService.updateUser(formData)

        console.log(response.data)
        userStore.addUser(response.data)
        oldPassword.value = ''
        newPassword.value = ''
        toast.add({
            severity: 'success',
            summary: 'Updated',
            detail: 'Settings updated successfully',
            life: 3000
        })

    } catch (error) {
        console.error('Failed to update settings:', error)

        toast.add({
            severity: 'error',
            summary: 'Failed',
            detail: 'Failed to update settings.',
            life: 3000
        })
    }
}

onMounted(async () => {
    const user = userStore.getUser();

    if (user && user.profile_picture) {
        try {
            imagesrc.value = await AuthenticationService.getUserPicture();
        } catch (error) {
            console.error("Failed to load profile picture:", error);
        }
    }

    if (user && user.preferred_currency) {
        preferredCurrency.value = user.preferred_currency;
    }
});

async function cancelSettings() {
    const user = userStore.getUser();

    // Reset image and preferred currency
    try {
        imagesrc.value = await AuthenticationService.getUserPicture();
    } catch (error) {
        console.error("Failed to load profile picture:", error);
    }

    image.value = '';
    oldPassword.value = ''
    newPassword.value = ''
    preferredCurrency.value = user?.preferred_currency ?? '';
}

const handleExport = async () => {
    try {
        const data = await AuthenticationService.exportCollection();
        const url = window.URL.createObjectURL(new Blob([data]));
        const link = document.createElement('a');
        link.href = url;
        link.setAttribute('download', 'comic_collection.xlsx');
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        window.URL.revokeObjectURL(url);

        toast.add({
            severity: 'success',
            summary: 'Export Successful',
            detail: 'Your comic collection has been downloaded.',
            life: 3000
        });
    } catch (error) {
        console.error('Export failed:', error);

        toast.add({
            severity: 'error',
            summary: 'Export Failed',
            detail: 'There was a problem exporting your collection.',
            life: 4000
        });
    }
};

const handleClean = async () => {
    await AuthenticationService.deleteAllData()
}
</script>