<template>
    <div class="w-full h-fit flex items-center justify-center">
        <swiper :slidesPerView="1" :grabCursor="true" :loop="true" :autoplay="{
            delay: 3000,
            disableOnInteraction: false,
        }"  :modules="modules" class="w-full max-w-full h-full max-h-full px-2 py-4">
            <swiper-slide v-for="issue in recentPurchasedIssues" :key="issue.id ?? issue.title"
                style="display: flex; flex-direction: column;">
                <div class="flex items-center justify-center w-full px-6 py-2 h-auto md:h-82.5">
                    <RouterLink :to="{
                        name: 'SeriesDetail',
                        params: { Link: issue.slug, Id: issue.series_id },
                    }" class="block w-full max-w-50" :aria-label="issue.series">
                        <CoverImage :src="issue.image" :title="issue.series" :alt="issue.series" depth="lg" initials-class="text-4xl" />
                    </RouterLink>
                </div>
                <div class="flex flex-col items-center justify-center text-center px-4 h-25 overflow-hidden">
                    <div class="text-lg sm:text-base md:text-xl font-bold text-primary line-clamp-2">
                        {{ issue.series }}
                    </div>
                    <div class="text-md sm:text-sm md:text-lg font-semibold capitalize text-white truncate">
                        {{ issueDisplayLabel(issue.title, issue.number) }}
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
import { issueDisplayLabel } from "@/utils/issueTitle";
import CoverImage from "@/components/common/CoverImage.vue";

const modules = [EffectCards, Navigation, Autoplay];

const props = defineProps(["recentPurchasedIssues"]);
</script>

<style></style>
