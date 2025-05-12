// declare module "*.svg" {
//   const content: any;
//   export default content;
// }

declare module 'swiper/vue' {
    import { DefineComponent } from 'vue';
    export const Swiper: DefineComponent;
    export const SwiperSlide: DefineComponent;
}