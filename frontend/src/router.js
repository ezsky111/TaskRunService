import { createRouter, createWebHistory } from 'vue-router'
import TaskList from './views/TaskList.vue'
import TaskEditor from './views/TaskEditor.vue'
import TaskLogs from './views/TaskLogs.vue'
import SystemMonitor from './views/SystemMonitor.vue'
import DbTaskEditor from './views/DbTaskEditor.vue'
import DbTaskRuns from './views/DbTaskRuns.vue'
import DbTaskExecute from './views/DbTaskExecute.vue'

const routes = [
  { path: '/', component: TaskList, name: 'TaskList' },
  { path: '/tasks', component: TaskList, name: 'Tasks' },
  { path: '/tasks/new', component: TaskEditor, name: 'NewTask' },
  { path: '/tasks/:id/edit', component: TaskEditor, name: 'EditTask' },
  { path: '/logs', component: TaskLogs, name: 'Logs' },
  { path: '/monitor', component: SystemMonitor, name: 'Monitor' },
  { path: '/dbtasks/new', component: DbTaskEditor, name: 'DbTaskNew' },
  { path: '/dbtasks/:taskId/runs', component: DbTaskRuns, name: 'DbTaskRuns', props: true },
  { path: '/dbtasks/:taskId/execute', component: DbTaskExecute, name: 'DbTaskExecute', props: true }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
