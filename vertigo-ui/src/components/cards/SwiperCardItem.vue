<template>
    <swiper :slidesPerView="1" :grabCursor="true" :loop="true" :autoplay="{
        delay: 12500,
        disableOnInteraction: false,
    }" :navigation="true" :modules="modules" class="max-w-full h-full max-h-full px-2 py-4">
        <swiper-slide v-for="issue in recentPurchasedIssues" :key="issue.title"
            style="display: flex; flex-direction: column; padding: 30px;">
            <div class="rounded-md flex items-center justify-center w-full h-full">
                <RouterLink :to="{
                    name: 'SeriesDetail',
                    params: { Link: issue.slug, Id: issue.series_id },
                }">
                    <img :src="issue.image" alt="" class="rounded-md w-[14rem] h-[303px]" />
                </RouterLink>
            </div>
            <div class="flex flex-col items-center justify-center text-center mt-8">
                <!-- Series Title -->
                <div class="text-xl md:text-2xl font-bold text-primary">
                    {{ issue.series }}
                </div>

                <!-- Issue Title -->
                <div class="text-lg md:text-xl font-semibold capitalize text-white">
                    {{ issue.title }}
                </div>

                <!-- Bought Date -->
                <div class="text-sm md:text-lg text-gray-400">
                    {{ issue.bought_date }}
                </div>
            </div>
        </swiper-slide>
    </swiper>
</template>

<script setup lang="ts">
import { Swiper, SwiperSlide } from "swiper/vue";
import "swiper/css";
import "swiper/css/navigation";

import { EffectCards, Navigation, Autoplay } from "swiper/modules";

const modules = [EffectCards, Navigation, Autoplay];

const props = defineProps(["recentPurchasedIssues"]);
</script>

<style></style>
