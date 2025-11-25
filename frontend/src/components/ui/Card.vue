<template>
  <div class="rounded-lg bg-white shadow-sm" :class="{ 'p-6': !noPadding }">
    <slot />
  </div>
</template>

<script>
export default {
  name: 'Card',
  props: {
    noPadding: Boolean
  }
}
</script>
