<template>
  <span :class="['inline-flex items-center rounded-full px-3 py-1 text-sm font-medium', variantClasses]">
    <slot />
  </span>
</template>

<script>
export default {
  name: 'Badge',
  props: {
    variant: {
      type: String,
      default: 'blue', // blue, green, red, yellow, slate
      validator: (val) => ['blue', 'green', 'red', 'yellow', 'slate'].includes(val)
    }
  },
  computed: {
    variantClasses() {
      const variants = {
        blue: 'bg-blue-100 text-blue-800',
        green: 'bg-green-100 text-green-800',
        red: 'bg-red-100 text-red-800',
        yellow: 'bg-yellow-100 text-yellow-800',
        slate: 'bg-slate-100 text-slate-800'
      }
      return variants[this.variant]
    }
  }
}
</script>
