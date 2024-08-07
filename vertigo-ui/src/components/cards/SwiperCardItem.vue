
<template>
    <swiper :slidesPerView="1" :grabCursor="true" :loop="true" :autoplay="{
        delay: 12500,
        disableOnInteraction: false,
    }" :navigation="true" :modules="modules" class="w-[20rem] h=[16rem] max-w-full max-h-full px-2 py-4">
        <!-- <swiper-slide class="rounded-t-lg">
            <img src="https://rukminim2.flixcart.com/image/850/1000/l5ld8y80/book/k/x/k/preacher-the-25th-anniversary-omnibus-vol-2-original-imagg7uvmfh8yhbg.jpeg?"
                alt="Preacher" class="rounded-md" />
            <div class="flex flex-col pt-8 pb-2 justify-center items-center text-center">
                <div class="text-2xl text-primary font-bold">Preacher</div>
                <div class="text-lg">Issue #5</div>
            </div>
        </swiper-slide>
        <swiper-slide class="rounded-t-lg">
            <img src="https://mir-s3-cdn-cf.behance.net/project_modules/disp/2edde416735185.562b9a8a3893b.jpg"
                alt="Sandman" class="rounded-md" />
            <div class="flex flex-col pt-8 pb-2 justify-center items-center text-center">
                <div class=" text-2xl font-bold text-primary">Sandman</div>
                <div class="text-lg">Preludes and Nocturnes #1</div>
            </div>
        </swiper-slide>
        <swiper-slide class="rounded-t-lg">
            <img src="https://m.media-amazon.com/images/I/8170gjsPGhL._AC_UF1000,1000_QL80_.jpg"
                alt="Gotham Centra;" class="rounded-md" />
            <div class="flex flex-col pt-8 pb-2 justify-center items-center text-center">
                <div class="text-2xl text-primary font-bold">Gotham Central</div>
                <div class="text-lg">Issue #6</div>
            </div>
        </swiper-slide> -->
        <swiper-slide v-for="issue in recentPurchasedIssues" :key="issue.title" class="swiper-sl rounded-t-lg">
            <img :src="issue.image" alt="" class="rounded-md w-[11rem] h-[15rem] m-auto " />
            <div class="flex flex-col items-center text-center pt-4 rounded-lg shadow-md">
                <!-- Series Title -->
                <div class="text-xl font-bold text-primary">
                    {{ issue.series }}
                </div>

                <!-- Issue Title -->
                <div class="text-lg font-semibold capitalize text-white">
                    {{ issue.title }}
                </div>

                <!-- Bought Date -->
                <div class="text-sm text-gray-400">
                    {{ issue.bought_date }}
                </div>
            </div>
        </swiper-slide>

    </swiper>
</template>

<script setup>
import { Swiper, SwiperSlide } from 'swiper/vue';
import 'swiper/css';
// import 'swiper/css/effect-cards';
import 'swiper/css/navigation';

import { EffectCards, Navigation, Autoplay } from 'swiper/modules';

const modules = [EffectCards, Navigation, Autoplay];

const props = defineProps(['recentPurchasedIssues'])

</script>

<style> 
/* .swiper {
    width: 20rem;
    height: 16rem;
    padding-inline: .5rem !important;
    padding-block: 1rem !important;
} */

.swiper-sl {
    flex-direction: column !important;
    align-items: center !important;
    justify-content: center !important;
}
/*
  .swiper-slide img {
      width: auto;
      height: auto;
      width: 58%;
      height: 65%;
      box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
  } */
</style>