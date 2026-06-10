<script setup lang="ts">
import AppSidebar from './AppSidebar.vue'
import AppTopbar from './AppTopbar.vue'
</script>

<template>
  <div class="flex" style="height:100vh;overflow:hidden;background:var(--color-bg)">
    <AppSidebar />
    <div class="flex-1 flex flex-col overflow-hidden">
      <AppTopbar />
      <main class="flex-1 overflow-y-auto p-5">
        <slot />
      </main>
    </div>
  </div>
</template>
