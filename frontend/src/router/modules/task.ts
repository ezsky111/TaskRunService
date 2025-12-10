import { AppRouteRecord } from '@/types/router'

export const taskRoutes: AppRouteRecord = {
  path: '/task',
  name: 'Task',
  component: '/index/index',
  meta: {
    title: 'menus.task.title',
    icon: 'ri:checkbox-circle-line'
  },
  children: [
    {
      path: 'list',
      name: 'TaskList',
      component: '/task/list',
      meta: {
        title: 'menus.task.list',
        icon: 'ri:checkbox-circle-line',
        keepAlive: true
      }
    },
    {
      path: 'run',
      name: 'TaskRun',
      component: '/task/run',
      meta: {
        title: 'menus.task.run',
        icon: 'ri:checkbox-circle-line',
        keepAlive: true
      }
    }
  ]
}
