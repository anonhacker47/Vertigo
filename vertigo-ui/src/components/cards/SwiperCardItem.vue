<template>
    <div class="w-full h-fit flex items-center justify-center">
        <swiper :slidesPerView="1" :grabCursor="true" :loop="true" :autoplay="{
            delay: 12500,
            disableOnInteraction: false,
        }" :navigation="true" :modules="modules" class="max-w-full h-full max-h-full px-2 py-4">
            <swiper-slide v-for="issue in recentPurchasedIssues" :key="issue.title"
                style="display: flex; flex-direction: column;">
                <div class="rounded-md flex items-stretch justify-center w-full px-4 h-auto md:h-[350px]">
                    <RouterLink :to="{
                        name: 'SeriesDetail',
                        params: { Link: issue.slug, Id: issue.series_id },
                    }">
                        <img :src="issue.image" alt=""
                            class="rounded-md w-full max-w-[14rem] h-auto md:h-[320px] object-cover" />
                    </RouterLink>
                </div>
                <div class="flex flex-col items-center justify-center text-center px-4 h-[100px] overflow-hidden">
                    <div class="text-lg sm:text-base md:text-xl font-bold text-primary line-clamp-2">
                        {{ issue.series }}
                    </div>
                    <div class="text-md sm:text-sm md:text-lg font-semibold capitalize text-white truncate">
                        Vol {{ issue.title }}
                    </div>
                    <div class="text-xs sm:text-[10px] md:text-sm text-gray-400 truncate">
                        {{ issue.bought_date }}
                    </div>
                </div>
            </swiper-slide>
        </swiper>
    </div>
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
