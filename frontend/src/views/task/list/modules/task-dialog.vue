
<template>
  <el-dialog v-model:model-value="visible" :title="dialogTitle" width="700px">

    <el-form :model="form" label-width="100px">
      <el-form-item label="任务名称">
        <el-input v-model="form.name" placeholder="输入任务名称" :disabled="isView" />
      </el-form-item>
      <el-form-item label="任务描述">
        <el-input v-model="form.description" placeholder="输入描述" :disabled="isView" />
      </el-form-item>
      <el-form-item label="脚本选择">
        <el-col :span="24">
        <!-- 已选脚本（支持拖拽排序） -->
          <div
            v-for="(script, idx) in form.scripts"
            :key="script + '_' + idx"
            draggable="true"
            @dragstart="dragStart($event, idx)"
            @dragover.prevent
            @drop="onDrop($event, idx)"
            @dragend="dragEnd"
            style="display:flex;align-items:center;margin-bottom:8px;padding:6px;border:1px solid #eee;border-radius:6px;background:#fff;"
          >
            <span style="cursor:grab;user-select:none;margin-right:8px;">⋮⋮</span>
            <span style="flex:1;">{{ script }}</span>
            <el-button size="small" @click="moveUp(idx)" :disabled="idx===0">↑</el-button>
            <el-button size="small" @click="moveDown(idx)" :disabled="idx===form.scripts.length-1">↓</el-button>
            <el-button size="small" type="danger" @click="removeScript(idx)">移除</el-button>
          </div>
        </el-col>
        <el-col :span="24">
        <!-- 可用脚本：垂直列表，不并排 -->
        <div style="margin-top:12px;">
          <div style="font-weight:600;margin-bottom:8px;">可用脚本:</div>
          <div style="display:flex;flex-direction:column;gap:8px;">
            <div v-for="script in availableScripts" :key="script" style="border:1px solid #eee;padding:8px;border-radius:6px;display:flex;justify-content:space-between;align-items:center;">
              <div>{{ script }}</div>
              <el-button size="small" type="primary" @click="addScript(script)">添加</el-button>
            </div>
          </div>
        </div>
        </el-col>
        </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="handleClose" :disabled="saving">取消</el-button>
      <el-button type="primary" @click="saveTask" :loading="saving" :disabled="saving">{{ saving ? '保存中...' : '保存' }}</el-button>
    </template>
  </el-dialog>
</template>


<script setup lang="ts">
import { ref, watch, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { fetchListScript, fetchUpdateDbTask, fetchCreateDbTask } from '@/api/task-db'
const dialogTitle = computed(() => {
  if (isAdd.value) return '新建编排任务'
  if (isEdit.value) return '编辑编排任务'
  return '编排任务详情'
})
const props = defineProps({
  modelValue: { type: Boolean, required: true },
  task: { type: Object, default: null },
  type: { type: String, default: 'add' }
})
const emit = defineEmits(['update:modelValue', 'submit'])

const visible = computed({
  get: () => props.modelValue,
  set: (v: boolean) => emit('update:modelValue', v)
})
const isView = computed(() => props.type === 'view')
const isEdit = computed(() => props.type === 'edit')
const isAdd = computed(() => props.type === 'add')

const form = ref({ name: '', description: '', scripts: [] as string[] })
const availableScripts = ref<string[]>([])
const saving = ref(false)
let dragIndex: number|null = null

function populateFromTask() {
  if (props.task) {
    form.value.name = props.task.name || ''
    form.value.description = props.task.description || ''
    form.value.scripts = Array.isArray(props.task.scripts) ? [...props.task.scripts] : []
  } else {
    form.value = { name: '', description: '', scripts: [] }
  }
}

async function loadScripts() {
  try {
    const res = await fetchListScript()
    availableScripts.value = (res || []).map((t: any) => t.name + '.py')
  } catch (e: any) {
    ElMessage.error('加载脚本列表失败: ' + (e.message || ''))
  }
}

function addScript(script: string) {
  if (!form.value.scripts.includes(script)) {
    form.value.scripts.push(script)
    ElMessage.info('已添加脚本: ' + script)
  }
}
function dragStart(e: DragEvent, idx: number) {
  dragIndex = idx
  try { e.dataTransfer?.setData('text/plain', String(idx)) } catch (err) {}
}

function dragEnd() {
  dragIndex = null
}

function onDrop(e: DragEvent, idx: number) {
  const from = dragIndex != null ? dragIndex : Number(e.dataTransfer?.getData('text/plain'))
  if (isNaN(from)) return
  const item = form.value.scripts.splice(from, 1)[0]
  // 插入到目标位置
  const to = idx
  form.value.scripts.splice(to, 0, item)
  dragIndex = null
}
function removeScript(idx: number) {
  const script = form.value.scripts[idx]
  form.value.scripts.splice(idx, 1)
  ElMessage.info('已移除脚本: ' + script)
}
function moveUp(idx: number) {
  if (idx > 0) {
    [form.value.scripts[idx - 1], form.value.scripts[idx]] = [form.value.scripts[idx], form.value.scripts[idx - 1]]
  }
}
function moveDown(idx: number) {
  if (idx < form.value.scripts.length - 1) {
    [form.value.scripts[idx], form.value.scripts[idx + 1]] = [form.value.scripts[idx + 1], form.value.scripts[idx]]
  }
}
function handleClose() {
  visible.value = false
}

async function saveTask() {
  if (!form.value.name) {
    ElMessage.warning('请填写任务名称')
    return
  }
  if (form.value.scripts.length === 0) {
    ElMessage.warning('请选择至少一个脚本')
    return
  }
  saving.value = true
  try {
      if (props.task && props.task.id) {
        const res = await fetchUpdateDbTask(props.task.id, {
          name: form.value.name,
          description: form.value.description,
          scripts: form.value.scripts
        })
        ElMessage.success( '更新成功')
        emit('submit')
      } else {
        const res = await fetchCreateDbTask({
          name: form.value.name,
          description: form.value.description,
          scripts: form.value.scripts
        })
        ElMessage.success('任务创建成功，ID: ' + (res.task_id || res.task_id))
        emit('submit')
      }
    visible.value = false
  } catch (e: any) {
    ElMessage.error('保存失败: ' + (e.response?.data?.message || e.message))
  } finally {
    saving.value = false
  }
}

watch(() => props.task, populateFromTask, { immediate: true })
watch(() => props.modelValue, (v) => { if (v) { loadScripts(); populateFromTask() } })

</script>

<style scoped></style>
