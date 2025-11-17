# Task Run Service - 项目结构说明

## 📁 项目结构

```
TaskRunService/
├── backend/                          # Python后端应用
│   ├── app/
│   │   ├── __init__.py              # Flask应用工厂
│   │   ├── core/
│   │   │   ├── __init__.py
│   │   │   ├── config.py            # 应用配置
│   │   │   ├── task_manager.py      # 任务管理和执行
│   │   │   └── process_manager.py   # 进程管理和监控
│   │   ├── routes/
│   │   │   ├── __init__.py
│   │   │   ├── task_routes.py       # 任务相关API
│   │   │   ├── log_routes.py        # 日志相关API
│   │   │   └── system_routes.py     # 系统信息API
│   │   ├── utils/
│   │   │   ├── __init__.py
│   │   │   ├── logger.py            # 日志记录工具
│   │   │   └── process_lock.py      # 进程锁 - 保障任务唯一性
│   │   ├── models/                  # 数据模型（可扩展）
│   │   └── services/                # 业务服务层（可扩展）
│   ├── logs/                        # 任务执行日志存储
│   ├── requirements.txt             # Python依赖
│   └── run.py                       # Flask启动脚本
│
├── frontend/                        # Vue前端应用
│   ├── src/
│   │   ├── main.js                 # 应用入口
│   │   ├── App.vue                 # 根组件
│   │   ├── router.js               # Vue路由配置
│   │   ├── api/
│   │   │   └── index.js            # API请求封装
│   │   ├── views/
│   │   │   ├── TaskList.vue        # 任务列表页面
│   │   │   ├── TaskEditor.vue      # 任务编辑页面
│   │   │   ├── TaskLogs.vue        # 执行日志页面
│   │   │   └── SystemMonitor.vue   # 系统监控页面
│   │   └── components/             # 可复用组件
│   ├── public/                     # 静态资源
│   ├── index.html                  # HTML模板
│   ├── package.json                # 依赖配置
│   └── vite.config.js             # Vite构建配置
│
├── tasks/                          # Python任务文件存储
│   ├── hello.py                   # 示例任务1
│   └── data_process.py            # 示例任务2
│
├── .github/workflows/             # GitHub Actions工作流
│   ├── build-and-push.yml         # 自动构建和推送镜像
│   └── release.yml                # 发布工作流
│
├── Dockerfile                     # 多阶段Docker镜像构建
├── docker-compose.yml             # Docker Compose部署配置
├── .dockerignore                  # Docker构建忽略文件
├── .gitignore                     # Git忽略文件
└── README.md                      # 项目文档
```

## 🚀 核心功能

### 1. 任务管理 (`backend/app/core/task_manager.py`)
- ✅ 列出所有Python任务文件
- ✅ 创建、编辑、删除任务
- ✅ 执行任务（后台线程）
- ✅ 任务执行日志记录
- ✅ **进程锁机制 - 保障同一任务不会并发执行**
- ✅ 最大并发任务数限制
- ✅ 任务执行超时控制

### 2. 进程管理 (`backend/app/core/process_manager.py`)
- ✅ 获取系统CPU、内存、磁盘信息
- ✅ 获取当前应用进程信息
- ✅ 列出所有Python进程

### 3. API接口

#### 任务API (`/api/tasks`)
- `GET /api/tasks` - 获取任务列表
- `GET /api/tasks/<task_id>` - 获取任务详情
- `POST /api/tasks` - 创建任务
- `PUT /api/tasks/<task_id>` - 更新任务
- `DELETE /api/tasks/<task_id>` - 删除任务
- `POST /api/tasks/<task_id>/execute` - 执行任务
- `GET /api/tasks/runs/<run_id>` - 获取执行状态
- `GET /api/tasks/runs` - 获取活跃任务

#### 日志API (`/api/logs`)
- `GET /api/logs` - 列出日志文件
- `GET /api/logs/<task_id>_<run_id>.log` - 获取执行日志
- `GET /api/logs/<task_id>_<run_id>.log/download` - 下载日志
- `GET /api/logs/app.log` - 获取应用日志

#### 系统API (`/api/system`)
- `GET /api/system/info` - 获取系统信息
- `GET /api/system/process` - 获取当前进程信息
- `GET /api/system/processes` - 获取所有Python进程
- `GET /api/system/health` - 健康检查

### 4. 前端功能

- 🎯 **任务列表页面** - 浏览、创建、编辑、删除、执行任务
- 📝 **任务编辑器** - 编写和修改Python代码
- 📊 **执行日志查看** - 实时查看和下载任务执行日志
- 📈 **系统监控** - 实时监控CPU、内存、磁盘和进程状态

## 🐳 Docker部署

### 特点
- 多阶段构建：先构建前端，再打包后端
- 前后端集成：前端dist打包入后端
- 自动健康检查
- 持久化存储：tasks和logs目录映射

### 快速启动

```bash
# 方式1: Docker Compose
docker-compose up -d

# 方式2: 直接Docker
docker build -t task-run-service .
docker run -p 5000:5000 \
  -v $(pwd)/tasks:/app/tasks \
  -v $(pwd)/logs:/app/logs \
  task-run-service
```

## 🔄 GitHub Actions工作流

### 1. 构建和推送流程 (`build-and-push.yml`)
- 每次push到main/develop分支自动构建
- Pull Request时只测试不推送
- 推送到GitHub Container Registry (ghcr.io)
- 自动版本标签和SHA标签
- 漏洞扫描（Trivy）

### 2. 发布流程 (`release.yml`)
- 创建Release时触发
- 构建并推送到Docker Hub
- 需要配置DOCKER_USERNAME和DOCKER_PASSWORD secrets

### 配置GitHub Secrets

```bash
# 1. DOCKER_USERNAME - Docker Hub用户名
# 2. DOCKER_PASSWORD - Docker Hub密码或Token
```

## 🔐 关键特性：进程唯一性保障

在`backend/app/utils/process_lock.py`中实现：

```python
class ProcessLock:
    """进程锁 - 确保同一任务不被并发执行"""
    def acquire_lock(self, task_id, timeout=5):
        # 获取任务锁，防止同时执行
    
    def is_task_running(self, task_id):
        # 检查任务是否正在运行
```

在`task_manager.py`中的使用：
- 执行任务前检查是否已在运行
- 获取锁后才能执行
- 任务完成后立即释放锁

## 📝 编写自定义任务

在`tasks/`目录中创建Python文件：

```python
#!/usr/bin/env python3
import sys

def main():
    print("任务开始...")
    # 你的代码逻辑
    print("任务完成!")
    return 0

if __name__ == '__main__':
    sys.exit(main())
```

任务可以：
- 接收命令行参数
- 输出日志（自动捕获stdout/stderr）
- 设置返回码（0=成功，非0=失败）

## 🛠️ 本地开发

### 后端开发
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python run.py
```

### 前端开发
```bash
cd frontend
npm install
npm run dev
```

### 生产构建
```bash
cd frontend
npm run build
# dist文件将被Docker构建时自动打包
```

## 📊 监控和日志

### 日志位置
- 应用日志: `/app/logs/app.log`
- 任务日志: `/app/logs/{task_id}_{run_id}.log`

### 配置日志级别
通过环境变量：
```bash
LOG_LEVEL=DEBUG|INFO|WARNING|ERROR
```

## 🔧 环境变量配置

```bash
# Flask配置
FLASK_ENV=production
FLASK_DEBUG=0

# 任务配置
TASKS_DIR=/app/tasks
LOGS_DIR=/app/logs
MAX_TASK_WORKERS=5          # 最大并发任务数
TASK_TIMEOUT=3600           # 任务超时时间（秒）

# 日志配置
LOG_LEVEL=INFO

# 进程检查
PROCESS_CHECK_INTERVAL=10   # 进程检查间隔（秒）
```

## 📦 依赖清单

### 后端
- Flask 3.0 - Web框架
- psutil 5.9 - 系统进程监控
- python-dotenv 1.0 - 环境变量管理
- APScheduler 3.10 - 任务调度（可选）

### 前端
- Vue 3.3 - UI框架
- Vite 5.0 - 打包工具
- Axios 1.6 - HTTP请求

## 🎯 项目亮点

1. **完整的Docker集成** - 一键部署
2. **CI/CD流程** - GitHub Actions自动化
3. **进程安全** - 锁机制防止重复执行
4. **前后端合一** - 简化部署
5. **可视化管理** - Vue提供友好界面
6. **完善的日志** - 追踪任务执行
7. **系统监控** - 实时资源使用情况

## 📄 许可证

MIT

## 🤝 贡献

欢迎提交Pull Request和Issue！