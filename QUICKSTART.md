# 🚀 Task Run Service - 快速启动指南

## 项目概览

Task Run Service 是一个Docker容器化的Python任务编排和执行服务，具有以下特性：

✅ **完整的Web管理界面** - Vue 3前端应用
✅ **任务编排执行** - Flask后端REST API
✅ **进程唯一性保障** - 防止同一任务重复执行
✅ **实时日志查看** - 任务执行输出追踪
✅ **系统监控** - CPU/内存/磁盘/进程监控
✅ **一键Docker部署** - 多阶段构建，前后端集成
✅ **CI/CD自动化** - GitHub Actions工作流

## ⚡ 5分钟快速开始

### 前置条件
- Docker和Docker Compose已安装
- Git已安装

### 步骤1: 克隆项目

```bash
git clone https://github.com/ezsky111/TaskRunService.git
cd TaskRunService
```

### 步骤2: 启动服务

```bash
docker-compose up -d
```

### 步骤3: 访问应用

打开浏览器访问: **http://localhost:5000**

就这么简单！🎉

## 📋 功能演示

### 1. 任务管理

进入"任务列表"页面，您可以：
- 👀 **查看所有任务** - 预置的示例任务（hello、data_process）
- ➕ **创建新任务** - 编写Python脚本
- ✏️ **编辑任务** - 修改已有任务代码
- ▶️ **执行任务** - 一键运行任务
- 🗑️ **删除任务** - 移除不需要的任务

示例：创建一个简单任务

```python
#!/usr/bin/env python3
import time
import json

print("任务开始...")

data = {
    'status': 'success',
    'message': '这是一个示例任务'
}

print(json.dumps(data, indent=2, ensure_ascii=False))
time.sleep(2)
print("任务完成！")
```

### 2. 执行日志查看

进入"执行日志"页面：
- 📜 **查看所有日志文件** - 任务执行的完整记录
- 👁️ **实时查看** - 查看任何已执行任务的输出
- ⬇️ **下载日志** - 下载日志进行离线分析

### 3. 系统监控

进入"系统监控"页面：
- 📊 **系统资源** - CPU、内存、磁盘实时使用情况
- 🔍 **当前进程** - Flask应用进程的详细信息
- 🐍 **Python进程列表** - 所有运行中的Python进程

## 🔑 关键特性讲解

### 进程唯一性保障

系统通过**进程锁机制**确保同一任务不会被并发执行：

```
尝试执行任务 "data_process"
    ↓
检查任务是否已在运行 ✓
    ↓
获取进程锁 ✓
    ↓
在后台线程中执行 Python 脚本
    ↓
任务完成后释放锁
    ↓
其他相同任务可继续执行
```

如果尝试在任务运行时再次执行它，会收到消息：
```
"任务 task_id 已在执行中，保障了进程唯一性"
```

### 日志记录系统

所有任务输出自动捕获到日志文件：

```
/app/logs/
├── app.log                      # 应用运行日志
├── hello_abc123ef.log           # 任务执行日志
├── data_process_def456ab.log    # 任务执行日志
└── ...
```

## 📚 API参考

### 基础URL
```
http://localhost:5000/api
```

### 任务相关API

```bash
# 列出所有任务
curl http://localhost:5000/api/tasks

# 获取特定任务
curl http://localhost:5000/api/tasks/hello

# 创建任务
curl -X POST http://localhost:5000/api/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "task_id": "my_task",
    "content": "print(\"Hello\")"
  }'

# 执行任务
curl -X POST http://localhost:5000/api/tasks/hello/execute

# 查看执行状态
curl http://localhost:5000/api/tasks/runs

# 获取日志
curl http://localhost:5000/api/logs/hello_abc123ef.log
```

## 🐳 Docker相关命令

```bash
# 查看容器状态
docker-compose ps

# 查看实时日志
docker-compose logs -f task-service

# 进入容器
docker-compose exec task-service bash

# 停止服务
docker-compose down

# 重启服务
docker-compose restart

# 清理所有数据（谨慎操作！）
docker-compose down -v
```

## 🛠️ 常见问题

### Q: 如何修改并发任务数？

在 `docker-compose.yml` 中修改：
```yaml
environment:
  - MAX_TASK_WORKERS=10  # 改为你需要的数字
```

### Q: 如何更改日志级别？

在 `docker-compose.yml` 中修改：
```yaml
environment:
  - LOG_LEVEL=DEBUG  # DEBUG, INFO, WARNING, ERROR
```

### Q: 如何查看应用的详细日志？

```bash
docker-compose logs -f --tail 100 task-service
```

### Q: 任务执行超时怎么办？

在 `docker-compose.yml` 中修改超时时间（秒）：
```yaml
environment:
  - TASK_TIMEOUT=7200  # 改为你需要的时间
```

### Q: 如何在本地测试而不使用Docker？

```bash
# 后端
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python run.py

# 前端（新终端）
cd frontend
npm install
npm run dev
```

## 📦 项目结构速览

```
TaskRunService/
├── backend/                # Python Flask应用
│   ├── app/
│   │   ├── core/          # 任务管理、进程管理
│   │   ├── routes/        # API端点
│   │   └── utils/         # 日志、进程锁
│   ├── requirements.txt    # Python依赖
│   └── run.py            # 启动脚本
│
├── frontend/              # Vue 3应用
│   ├── src/
│   │   ├── views/        # 页面组件
│   │   ├── api/          # API调用
│   │   └── App.vue       # 根组件
│   └── package.json      # 依赖配置
│
├── tasks/                 # 任务文件存储
│   ├── hello.py          # 示例1
│   └── data_process.py   # 示例2
│
├── Dockerfile            # Docker镜像定义
├── docker-compose.yml    # Docker Compose配置
└── .github/workflows/    # CI/CD工作流
```

## 🚀 下一步

### 1. 创建你的第一个任务

访问 http://localhost:5000 → 新建任务 → 编写代码 → 保存

### 2. 执行任务并查看日志

点击执行按钮 → 在"执行日志"页面查看结果

### 3. 监控系统状态

进入"系统监控"页面实时观察资源使用

### 4. 部署到生产环境

参考 `DEPLOYMENT.md` 文档进行生产部署配置

## 📖 完整文档

- **README.md** - 项目详细说明和功能列表
- **ARCHITECTURE.md** - 系统架构和设计说明
- **DEPLOYMENT.md** - 部署指南和使用说明

## 🔗 GitHub Actions自动化

推送代码时，自动触发：
1. ✅ Docker镜像构建
2. ✅ 自动化测试
3. ✅ 安全漏洞扫描
4. ✅ 推送到镜像仓库

创建Release时，自动推送到Docker Hub。

## 💡 最佳实践

1. **编写任务时**
   - 使用标准的返回码（0=成功，非0=失败）
   - 使用print()输出日志信息
   - 接受命令行参数进行参数化

2. **部署时**
   - 定期备份 `/tasks` 和 `/logs` 目录
   - 设置合理的 `TASK_TIMEOUT`
   - 根据硬件调整 `MAX_TASK_WORKERS`

3. **监控时**
   - 定期查看系统监控页面
   - 检查应用日志寻找问题
   - 清理过期日志文件

## 🤝 贡献

欢迎提交Issue和Pull Request！

## 📄 许可证

MIT

## 📞 支持

遇到问题？
1. 检查日志文件
2. 查看DEPLOYMENT.md中的问题排查部分
3. 提交GitHub Issue

---

**开始使用 Task Run Service，让任务管理变得简单！** 🎉
