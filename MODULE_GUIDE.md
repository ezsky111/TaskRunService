# Task Run Service - 核心模块导读

本文档帮助开发者快速理解项目各模块的功能和关键代码。

## 📚 模块导览

### 后端核心模块

#### 1. 任务管理器 (`backend/app/core/task_manager.py`)

**职责**: 任务生命周期管理、执行、监控

**关键类**: `TaskManager`

**关键方法**:

| 方法 | 功能 | 返回值 |
|------|------|--------|
| `list_tasks()` | 列出所有任务 | 任务列表 |
| `get_task_info(task_id)` | 获取任务详情 | 任务信息 |
| `create_task(task_id, content)` | 创建任务 | (success, message) |
| `update_task(task_id, content)` | 更新任务 | (success, message) |
| `delete_task(task_id)` | 删除任务 | (success, message) |
| `execute_task(task_id, params)` | **执行任务（核心方法）** | (run_id, message) |
| `get_task_status(run_id)` | 获取执行状态 | 状态信息 |
| `get_active_tasks()` | 获取活跃任务 | 活跃任务列表 |

**执行流程**（`execute_task` 方法）:

```python
def execute_task(self, task_id, params=None):
    # 1. 检查并发数
    if len(self.active_tasks) >= self.max_workers:
        return None, "已达到最大并发任务数"
    
    # 2. 验证任务存在
    task_path = os.path.join(self.tasks_dir, f"{task_id}.py")
    if not os.path.exists(task_path):
        return None, "任务不存在"
    
    # 3. 检查进程锁（防止重复执行）✨ 关键！
    if self.process_lock.is_task_running(task_id):
        return None, f"任务 {task_id} 已在执行中，保障了进程唯一性"
    
    # 4. 获取锁
    if not self.process_lock.acquire_lock(task_id):
        return None, f"无法获取任务锁: {task_id}"
    
    # 5. 启动后台线程执行
    thread = threading.Thread(
        target=self._execute_task_thread,
        args=(task_id, run_id, task_path, params)
    )
    thread.daemon = False
    thread.start()
    
    # 6. 记录活跃任务
    self.active_tasks[run_id] = {
        'task_id': task_id,
        'run_id': run_id,
        'status': 'running',
        'start_time': datetime.now().isoformat(),
        'thread': thread
    }
    
    return run_id, "任务已提交执行"
```

#### 2. 进程锁 (`backend/app/utils/process_lock.py`)

**职责**: 确保任务唯一性执行

**关键类**: `ProcessLock`

**工作原理**:

```
锁字典结构:
{
    'task_a': Lock对象,
    'task_b': Lock对象,
    ...
}

工作流程:
1. 首次执行任务A → 创建Lock并acquire → 锁定状态
2. 尝试再次执行任务A → acquire返回False → 拒绝执行
3. 任务A完成 → release锁 → 从字典删除 → 可继续执行
```

**关键方法**:

```python
def acquire_lock(self, task_id, timeout=5):
    """获取任务锁，如果无法获取则返回False"""
    # 尝试在timeout时间内获取锁
    # 返回: True/False
    
def release_lock(self, task_id):
    """释放锁，清理锁对象"""
    
def is_task_running(self, task_id):
    """检查任务是否正在运行"""
    # 返回: True/False
```

#### 3. 进程监控 (`backend/app/core/process_manager.py`)

**职责**: 系统和进程监控

**关键类**: `ProcessManager`

**关键方法**:

```python
def get_system_info():
    """返回 {cpu_percent, memory{...}, disk{...}}"""

def get_process_info():
    """返回当前Flask进程的详细信息"""

def get_all_processes():
    """返回所有Python进程列表"""
```

#### 4. 日志工具 (`backend/app/utils/logger.py`)

**职责**: 日志记录

**关键函数**:

```python
def setup_logger(name):
    """为任何模块创建配置好的logger"""
    # 自动添加console和file handlers
    # 返回: configured logger
```

### 前端模块

#### 1. API客户端 (`frontend/src/api/index.js`)

**职责**: 与后端通信

**对象**:

- `taskApi` - 任务相关API
- `logApi` - 日志相关API
- `systemApi` - 系统相关API

**使用示例**:

```javascript
// 执行任务
const res = await taskApi.executeTask('hello')
const run_id = res.data.run_id

// 查看日志
const logRes = await logApi.getLog('hello', run_id)
console.log(logRes.data.content)

// 系统监控
const sysRes = await systemApi.getSystemInfo()
console.log(sysRes.data.cpu_percent)
```

#### 2. 路由配置 (`frontend/src/router.js`)

**支持的路由**:

| 路径 | 组件 | 功能 |
|------|------|------|
| `/` | TaskList | 任务列表 |
| `/tasks` | TaskList | 任务列表 |
| `/tasks/new` | TaskEditor | 创建新任务 |
| `/tasks/:id/edit` | TaskEditor | 编辑任务 |
| `/logs` | TaskLogs | 查看日志 |
| `/monitor` | SystemMonitor | 系统监控 |

#### 3. 页面组件

- **TaskList.vue** - 任务列表和管理
  ```javascript
  loadTasks()        // 加载任务列表
  executeTask()      // 执行任务
  deleteTask()       // 删除任务
  checkStatus()      // 检查执行状态
  ```

- **TaskEditor.vue** - 任务编辑
  ```javascript
  loadTask()         // 加载任务内容
  saveTask()         // 保存任务
  ```

- **TaskLogs.vue** - 日志查看
  ```javascript
  loadLogs()         // 加载日志列表
  viewLog()          // 查看特定日志
  ```

- **SystemMonitor.vue** - 系统监控
  ```javascript
  loadMonitorData()   // 加载监控数据（自动刷新）
  refreshMonitor()    // 手动刷新
  ```

## 🔄 数据流

### 任务执行数据流

```
前端UI (TaskList.vue)
  │ click "执行"
  │
  ├─► axios.post('/api/tasks/hello/execute')
  │
  后端 (task_routes.py)
  │ @bp.route('/<task_id>/execute', methods=['POST'])
  │
  ├─► task_manager.execute_task(task_id)
  │
  任务管理器 (task_manager.py)
  │
  ├─► 检查并发数 ✓
  ├─► 验证任务存在 ✓
  ├─► process_lock.is_task_running(task_id) ← 检查进程锁
  ├─► process_lock.acquire_lock(task_id) ← 获取进程锁
  ├─► 启动后台线程 (_execute_task_thread)
  │    │
  │    ├─► subprocess.run(python task_id.py)
  │    ├─► 捕获输出到日志文件
  │    ├─► 更新任务状态
  │    └─► process_lock.release_lock(task_id) ← 释放锁
  │
  └─► 返回 run_id
  
  前端接收 {success: true, run_id: 'abc123'}
  │
  └─► 显示在"执行中的任务"列表
```

## 🎯 关键设计决策

### 1. 为什么使用进程锁？

```
问题: 同一任务可能被多次快速触发执行
    ├─ 浪费资源
    ├─ 竞争条件
    └─ 数据不一致

解决: ProcessLock类
    ├─ 每个任务有唯一的Lock对象
    ├─ 任务执行前必须获取Lock
    ├─ 同一任务同时只有一个Lock被hold
    └─ 任务完成后立即释放
```

### 2. 为什么使用后台线程？

```
原因:
├─ 不阻塞API响应
├─ 支持长时间运行的任务
├─ 允许并发执行多个任务
└─ 用户可以在任务运行时继续操作

实现:
├─ _execute_task_thread() 在线程中运行
├─ 每个任务一个线程
├─ 使用active_tasks字典追踪
└─ 通过run_id查询执行状态
```

### 3. 为什么使用文件系统存储任务？

```
优势:
├─ 简化部署（不需要数据库）
├─ 易于版本控制
├─ 便于备份和迁移
├─ 支持大规模任务集

目录结构:
/app/tasks/
  ├─ hello.py
  ├─ data_process.py
  └─ user_task.py
```

## 🔧 扩展开发

### 添加新的API端点

1. 在 `backend/app/routes/` 中创建新文件

```python
# backend/app/routes/custom_routes.py
from flask import Blueprint, jsonify

bp = Blueprint('custom', __name__, url_prefix='/api/custom')

@bp.route('/endpoint', methods=['GET'])
def custom_endpoint():
    return jsonify({'data': 'value'})
```

2. 在 `backend/app/__init__.py` 中注册

```python
from app.routes import custom_routes
app.register_blueprint(custom_routes.bp)
```

3. 在前端中调用

```javascript
// frontend/src/api/index.js
export const customApi = {
  getEndpoint: () => api.get('/custom/endpoint')
}
```

### 添加新的前端页面

1. 创建Vue组件

```vue
<!-- frontend/src/views/NewPage.vue -->
<template>
  <div class="new-page">
    <!-- 你的内容 -->
  </div>
</template>

<script>
export default {
  name: 'NewPage'
}
</script>
```

2. 在路由中注册

```javascript
// frontend/src/router.js
import NewPage from './views/NewPage.vue'

routes.push({
  path: '/newpage',
  component: NewPage,
  name: 'NewPage'
})
```

3. 在导航中添加链接

```vue
<!-- frontend/src/App.vue -->
<router-link to="/newpage">新页面</router-link>
```

## 📊 依赖关系图

```
Flask应用 (app/__init__.py)
    │
    ├─► TaskManager (core/task_manager.py)
    │    └─► ProcessLock (utils/process_lock.py)
    │    └─► Logger (utils/logger.py)
    │
    ├─► ProcessManager (core/process_manager.py)
    │    └─► Logger (utils/logger.py)
    │
    └─► Routes (routes/)
         ├─► task_routes.py
         ├─► log_routes.py
         └─► system_routes.py
```

## 🧪 测试关键组件

### 测试进程锁

```python
# 测试代码
from app.utils.process_lock import ProcessLock

lock = ProcessLock()

# 第一次获取应该成功
assert lock.acquire_lock('task1') == True
assert lock.is_task_running('task1') == True

# 第二次应该失败
assert lock.acquire_lock('task1') == False

# 释放后应该可以再次获取
lock.release_lock('task1')
assert lock.acquire_lock('task1') == True
```

### 测试任务执行

```python
# 测试代码
from app.core.task_manager import TaskManager

manager = TaskManager()

# 创建测试任务
manager.create_task('test', 'print("Hello")')

# 执行任务
run_id, msg = manager.execute_task('test')
assert run_id is not None

# 检查状态
import time
time.sleep(2)
status = manager.get_task_status(run_id)
assert status['status'] in ['success', 'running']
```

## 🚀 性能优化建议

1. **缓存**: 添加Redis缓存任务列表
2. **数据库**: 改用数据库存储任务历史
3. **异步**: 使用Celery替代线程
4. **分布式**: 使用Kubernetes集群部署

## 📚 完整流程示例

### 从UI到执行的完整流程

```
1. 用户在浏览器点击"执行hello任务"
   
2. 前端 (TaskList.vue)
   ├─ handleClick('execute', 'hello')
   ├─ axios.post('/api/tasks/hello/execute')
   └─ 等待响应

3. 后端 (task_routes.py - execute_task)
   ├─ 接收 POST /api/tasks/hello/execute
   ├─ 从请求体获取参数
   ├─ 调用 current_app.task_manager.execute_task('hello')
   └─ 返回 {success: true, run_id: 'xyz789'}

4. 任务管理器 (task_manager.py)
   ├─ 检查 active_tasks 长度 < max_workers
   ├─ 验证 /app/tasks/hello.py 存在
   ├─ 调用 process_lock.is_task_running('hello')
   │  └─ 返回 False（没有其他hello任务运行）
   ├─ 调用 process_lock.acquire_lock('hello')
   │  └─ 返回 True（成功获取锁）
   ├─ 启动线程执行 _execute_task_thread()
   │  ├─ 打开日志文件
   │  ├─ 执行: subprocess.run(['python', '/app/tasks/hello.py'])
   │  ├─ 捕获输出到日志文件
   │  ├─ 等待进程完成
   │  ├─ 更新 active_tasks[run_id]['status'] = 'success'
   │  └─ 调用 process_lock.release_lock('hello')
   └─ 返回 run_id

5. 前端接收响应
   ├─ run_id = 'xyz789'
   ├─ 在"执行中的任务"列表中显示
   ├─ 定时轮询 /api/tasks/runs/xyz789 获取状态
   └─ 任务完成后显示成功消息

6. 用户点击"查看日志"
   └─ 前端调用 axios.get('/api/logs/hello_xyz789.log')
      └─ 后端返回日志内容
         └─ 前端显示任务的所有输出
```

---

这份导读应该足以让您快速理解项目的核心模块。祝开发愉快！🚀
