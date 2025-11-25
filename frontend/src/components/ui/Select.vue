<template>
  <div class="relative" >
    <button
      @click="isOpen = !isOpen"
      class="w-full rounded-lg border border-slate-300 bg-white px-4 py-3 text-left font-medium text-slate-900 transition hover:border-slate-400 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-200"
    >
      <div class="flex items-center justify-between">
        <span v-if="selectedOption">{{ selectedOption.label }}</span>
        <span v-else class="text-slate-500">{{ placeholder }}</span>
        <ChevronDown
          :size="18"
          class="text-slate-600 transition"
          :class="{ 'rotate-180': isOpen }"
        />
      </div>
    </button>



    <transition
      enter-active-class="transition duration-100 ease-out"
      enter-from-class="opacity-0 scale-95"
      enter-to-class="opacity-100 scale-100"
      leave-active-class="transition duration-100 ease-in"
      leave-from-class="opacity-100 scale-100"
      leave-to-class="opacity-0 scale-95"
    >
      <div
        v-show="isOpen"
        class="top-full left-0 right-0 z-50 mt-2 max-h-64 origin-top overflow-y-auto rounded-lg border border-slate-300 bg-white shadow-xl"
      >
        <!-- 空选项 -->
        <button
          @click="selectOption(null)"
          class="w-full px-4 py-2.5 text-left text-slate-600 transition hover:bg-blue-50"
        >
          {{ placeholder }}
        </button>

        <!-- 选项列表 -->
        <button
          v-for="option in options"
          :key="option.value"
          @click="selectOption(option)"
          class="w-full px-4 py-2.5 text-left transition"
          :class="
            selectedOption?.value === option.value
              ? 'bg-blue-50 font-semibold text-blue-700'
              : 'text-slate-900 hover:bg-slate-50'
          "
        >
          {{ option.label }}
        </button>
      </div>
    </transition>
  </div>
</template>

<script>
import { ChevronDown } from 'lucide-vue-next'

export default {
  name: 'Select',
  components: { ChevronDown },
  props: {
    modelValue: [String, Number],
    options: {
      type: Array,
      default: () => []
    },
    placeholder: {
      type: String,
      default: '选择一个选项'
    }
  },
  emits: ['update:modelValue', 'change'],
  data() {
    return {
      isOpen: false
    }
  },
  watch: {
    isOpen(newVal) {
      if (newVal) {
        document.addEventListener('click', this.handleClickOutside)
      } else {
        document.removeEventListener('click', this.handleClickOutside)
      }
    }
  },
  beforeUnmount() {
    document.removeEventListener('click', this.handleClickOutside)
  },
  computed: {
    selectedOption() {
      return this.options.find((opt) => opt.value === this.modelValue)
    }
  },
  methods: {
    selectOption(option) {
      const value = option ? option.value : ''
      this.$emit('update:modelValue', value)
      this.$emit('change', value)
      this.isOpen = false
    },
    handleClickOutside(event) {
      if (!this.$el.contains(event.target)) {
        this.isOpen = false
      }
    }
  }
}
</script>
