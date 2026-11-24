<template>
  <div class="flex flex-col items-center gap-4 px-6 py-24 text-center">
    <p class="text-6xl font-bold text-slate-500">404</p>
    <h1 class="text-2xl font-bold text-white">Page not found</h1>
    <p class="text-sm text-slate-400">Nothing lives at this address.</p>
    <RouterLink :to="{ name: 'Dashboard' }" class="font-semibold text-sky-300 hover:underline">
      Back to the dashboard
    </RouterLink>
  </div>
</template>
