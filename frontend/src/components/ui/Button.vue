<template>
  <button
    :class="[
      'inline-flex items-center justify-center gap-2 rounded-lg font-semibold transition',
      sizeClasses,
      variantClasses,
    ]"
    :type="type"
    :disabled="disabled"
  >
    <slot />
  </button>
</template>

<script>
export default {
  name: 'Button',
  props: {
    type: {
      type: String,
      default: 'button'
    },
    variant: {
      type: String,
      default: 'primary', // primary, secondary, danger, ghost
      validator: (val) => ['primary', 'secondary', 'danger', 'ghost'].includes(val)
    },
    size: {
      type: String,
      default: 'md', // sm, md, lg
      validator: (val) => ['sm', 'md', 'lg'].includes(val)
    },
    disabled: Boolean
  },
  computed: {
    sizeClasses() {
      const sizes = {
        sm: 'px-3 py-1.5 text-sm',
        md: 'px-4 py-2 text-base',
        lg: 'px-6 py-3 text-lg'
      }
      return sizes[this.size]
    },
    variantClasses() {
      const variants = {
        primary: 'bg-blue-600 text-white shadow-md hover:bg-blue-700 hover:shadow-lg disabled:bg-blue-300 disabled:cursor-not-allowed',
        secondary: 'bg-slate-200 text-slate-900 hover:bg-slate-300 disabled:bg-slate-100 disabled:cursor-not-allowed',
        danger: 'bg-red-600 text-white shadow-md hover:bg-red-700 hover:shadow-lg disabled:bg-red-300 disabled:cursor-not-allowed',
        ghost: 'text-slate-600 hover:bg-slate-100 disabled:text-slate-300 disabled:cursor-not-allowed'
      }
      return variants[this.variant]
    }
  }
}
</script>
