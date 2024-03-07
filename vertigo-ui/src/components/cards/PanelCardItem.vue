<template>
    <div
      class="panel-card right-0 top-0 bottom-0 left-0 z-20 m-auto absolute w-fit h-fit rounded-lg shadow bg-gray-800 border border-gray-700"
    >
      <div class="p-6 space-y-4 sm:p-8">
        <slot>
            add something
        </slot>
    </div>
  </div>
</template>

<style scoped>
.panel-card{
  transform: rotateY(30deg) rotateX(-40deg) perspective(-800px) scale(.5)
}
</style>