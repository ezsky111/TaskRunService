<template>
  <ArtSearchBar
    ref="searchBarRef"
    v-model="formData"
    :items="formItems"
    :rules="rules"
    @reset="handleReset"
    @search="handleSearch"
  />
</template>

<script setup lang="ts">
interface Props {
  modelValue: Record<string, any>
}
interface Emits {
  (e: 'update:modelValue', value: Record<string, any>): void
  (e: 'search', params: Record<string, any>): void
  (e: 'reset'): void
}
const props = defineProps<Props>()
const emit = defineEmits<Emits>()

const searchBarRef = ref()
const formData = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val)
})

const rules = {}

const statusOptions = ref([
  { label: '全部', value: '' },
  { label: '待处理', value: 'pending' },
  { label: '运行中', value: 'running' },
  { label: '成功', value: 'success' },
  { label: '失败', value: 'failed' }
])

const formItems = computed(() => [
  {
    label: '关键词',
    key: 'keyword',
    type: 'input',
    placeholder: '任务名称、ID 等',
    clearable: true
  },
  {
    label: '状态',
    key: 'status',
    type: 'select',
    props: { placeholder: '请选择状态', options: statusOptions.value }
  }
])

function handleReset() {
  emit('reset')
}

async function handleSearch() {
  await searchBarRef.value.validate()
  emit('search', formData.value)
}
</script>
