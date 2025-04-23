<template>
    <div class="max-w-3xl mx-auto p-6 space-y-10">
        <h1 class="text-3xl font-bold text-primary">Settings</h1>

        <!-- Profile Picture -->
        <section class="border-sky-900 border-2  rounded-xl shadow p-6">
            <h2 class="text-xl font-semibold mb-2">Profile Picture</h2>
            <p class="text-sm text-sky-600 mb-4">Upload a profile picture for your account.</p>
            <div class="h-1/2 w-1/2">
                <ImageUploader v-model="imagesrc" @image-change="onImageChange" />
            </div>
        </section>

        <!-- Preferred Currency -->
        <section class="border-sky-900 border-2 rounded-xl shadow p-6">
            <h2 class="text-xl font-semibold mb-2">Preferred Currency</h2>
            <p class="text-sm text-sky-600 mb-4">Select your preferred currency for price display.</p>
            <select v-model="preferredCurrency"
                class="w-full p-3 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500">
                <option v-for="currency in currencyList" :key="currency.code" :value="currency.code">
                    {{ currency.code }} - {{ currency.currency }}
                </option>
            </select>
        </section>

        <section class="border-sky-900 border-2 rounded-xl shadow p-6">
            <h2 class="text-xl font-semibold mb-2">Change Password</h2>
            <p class="text-sm text-sky-600 mb-4">Update your account password.</p>
            <div class="space-y-4">
                <input type="password" v-model="oldPassword" placeholder="Old Password"
                    class="w-full p-3 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500" />
                <input type="password" v-model="newPassword" placeholder="New Password"
                    class="w-full p-3 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500" />
            </div>
        </section>

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
    <NotificationToast position="bottom-center" />
</template>


<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'
import { useUserStore } from '@/store/user'
import currencyCodes from 'currency-codes'
import ImageUploader from '@/components/createSeries/ImageUploader.vue'
import AuthenticationService from '@/services/AuthenticationService'
import { useToast } from "primevue/usetoast";

const preferredCurrency = ref()
const userStore = useUserStore()
const toast = useToast();

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


</script>