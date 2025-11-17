# 项目部署和使用指南

## 快速开始

### 方式1: 使用Docker Compose（推荐）

```bash
# 克隆项目
git clone https://github.com/ezsky111/TaskRunService.git
cd TaskRunService

# 启动服务
docker-compose up -d

# 查看日志
docker-compose logs -f task-service

# 停止服务
docker-compose down
```

访问应用: http://localhost:5000

### 方式2: 使用Docker直接运行

```bash
# 构建镜像
docker build -t task-run-service .

# 运行容器
docker run -d \
  --name task-service \
  -p 5000:5000 \
  -v $(pwd)/tasks:/app/tasks \
  -v $(pwd)/logs:/app/logs \
  -e LOG_LEVEL=INFO \
  task-run-service

# 查看日志
docker logs -f task-service

# 停止容器
docker stop task-service
docker rm task-service
```

### 方式3: 本地开发

#### 后端开发环境

```bash
cd backend

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 运行应用
python run.py
```

应用将运行在 http://localhost:5000

#### 前端开发环境

```bash
cd frontend

# 安装依赖
npm install

# 开发模式
npm run dev

# 生产构建
npm run build
```

前端开发服务器运行在 http://localhost:5173

## 项目配置

### 环境变量

在容器中可以通过环境变量配置应用：

| 变量名 | 默认值 | 说明 |
|--------|--------|------|
| FLASK_ENV | production | Flask环境 |
| FLASK_DEBUG | 0 | 调试模式 |
| TASKS_DIR | /app/tasks | 任务文件存储目录 |
| LOGS_DIR | /app/logs | 日志存储目录 |
| MAX_TASK_WORKERS | 5 | 最大并发任务数 |
| TASK_TIMEOUT | 3600 | 任务执行超时时间（秒） |
| LOG_LEVEL | INFO | 日志级别 |

### Docker Compose 配置

在 `docker-compose.yml` 中修改环境变量：

```yaml
services:
  task-service:
    environment:
      - FLASK_ENV=production
      - MAX_TASK_WORKERS=10
      - TASK_TIMEOUT=7200
      - LOG_LEVEL=DEBUG
```

## 使用说明

### 1. 任务管理

#### 创建任务

1. 访问 http://localhost:5000
2. 点击"新建任务"
3. 输入任务ID和Python代码
4. 点击"保存"

#### 编写任务示例

```python
#!/usr/bin/env python3
import sys
import time

def main():
    print("任务开始执行...")
    
    # 处理参数
    if len(sys.argv) > 1:
        name = sys.argv[1]
        print(f"参数: {name}")
    
    # 执行任务逻辑
    for i in range(3):
        print(f"处理步骤 {i+1}")
        time.sleep(1)
    
    print("任务完成！")
    return 0

if __name__ == '__main__':
    sys.exit(main())
```

#### 执行任务

1. 在任务列表中选择任务
2. 点击"执行"按钮
3. 在"执行中的任务"部分查看实时状态
4. 点击"查看日志"查看执行结果

### 2. 日志查询

- **任务执行日志**: 在"执行日志"页面查看每个任务的执行输出
- **应用日志**: 查看应用本身的运行日志
- **下载日志**: 支持下载任务执行日志进行离线分析

### 3. 系统监控

在"系统监控"页面可以查看：

- **CPU使用率**: 实时CPU占用百分比
- **内存使用**: 内存占用和可用大小
- **磁盘使用**: 磁盘占用情况
- **进程信息**: 应用进程的详细信息
- **Python进程列表**: 所有运行中的Python进程

## 进程唯一性保障

系统通过进程锁机制保障同一任务的唯一性：

1. **检查机制**: 执行任务前会检查是否已在运行
2. **锁定机制**: 获取任务锁，防止并发执行
3. **释放机制**: 任务完成后立即释放锁
4. **超时保护**: 避免死锁，设置锁定超时时间

如果尝试执行已在运行的任务，系统将返回错误消息：
```json
{
  "success": false,
  "message": "任务 task_id 已在执行中，保障了进程唯一性"
}
```

## API调用示例

### 使用curl

```bash
# 获取任务列表
curl http://localhost:5000/api/tasks

# 创建任务
curl -X POST http://localhost:5000/api/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "task_id": "my_task",
    "content": "print(\"Hello\")"
  }'

# 执行任务
curl -X POST http://localhost:5000/api/tasks/my_task/execute \
  -H "Content-Type: application/json" \
  -d '{
    "params": ["arg1", "arg2"]
  }'

# 获取任务执行状态
curl http://localhost:5000/api/tasks/runs/abc12345

# 获取任务日志
curl http://localhost:5000/api/logs/my_task_abc12345.log

# 获取系统信息
curl http://localhost:5000/api/system/info
```

### 使用Python

```python
import requests

# 基础URL
BASE_URL = 'http://localhost:5000/api'

# 获取任务列表
response = requests.get(f'{BASE_URL}/tasks')
print(response.json())

# 创建任务
data = {
    'task_id': 'my_task',
    'content': 'print("Hello World")'
}
response = requests.post(f'{BASE_URL}/tasks', json=data)
print(response.json())

# 执行任务
response = requests.post(f'{BASE_URL}/tasks/my_task/execute')
run_id = response.json()['run_id']
print(f"任务已提交，run_id: {run_id}")

# 检查执行状态
response = requests.get(f'{BASE_URL}/tasks/runs/{run_id}')
print(response.json())
```

## 问题排查

### 任务无法执行

1. 检查任务代码是否有语法错误
2. 查看应用日志了解具体错误信息
3. 确认任务文件是否存在于 `/app/tasks` 目录

### 进程卡住

1. 检查日志查看任务是否死循环
2. 通过系统监控查看CPU/内存占用
3. 调整 `TASK_TIMEOUT` 参数强制终止长时间运行的任务

### 内存溢出

1. 减少 `MAX_TASK_WORKERS` 的值
2. 优化任务代码减少内存占用
3. 监控系统内存使用

## GitHub Actions自动化

项目包含两个工作流：

### 1. 构建和推送（build-and-push.yml）

- **触发条件**:
  - push到main或develop分支
  - 创建新的tag
  - Pull Request到main分支

- **工作内容**:
  - 构建Docker镜像
  - 运行测试
  - 执行漏洞扫描
  - 推送到GitHub Container Registry

### 2. 发布（release.yml）

- **触发条件**: 创建新的Release

- **工作内容**:
  - 构建Docker镜像
  - 推送到Docker Hub

### 配置GitHub Secrets

为了使用发布工作流，需要配置以下secrets：

```
Settings > Secrets and variables > Actions > New repository secret
```

需要配置的secrets：
- `DOCKER_USERNAME`: Docker Hub用户名
- `DOCKER_PASSWORD`: Docker Hub密码或Token

## 监控和维护

### 定期备份

```bash
# 备份任务文件
tar -czf tasks_backup_$(date +%Y%m%d).tar.gz tasks/

# 备份日志
tar -czf logs_backup_$(date +%Y%m%d).tar.gz logs/
```

### 日志清理

```bash
# 删除7天前的日志
find logs/ -name "*.log" -mtime +7 -delete
```

### 容器监控

```bash
# 查看容器状态
docker-compose ps

# 查看容器资源占用
docker stats

# 查看容器日志
docker-compose logs -f --tail 100
```

## 安全建议

1. **修改SECRET_KEY**: 在生产环境中修改Flask的SECRET_KEY
2. **限制访问**: 使用反向代理（如Nginx）限制API访问
3. **认证机制**: 添加用户认证保护任务管理接口
4. **HTTPS**: 在生产环境使用HTTPS
5. **定期更新**: 及时更新依赖包和Docker镜像

## 性能优化

1. **并发限制**: 调整 `MAX_TASK_WORKERS` 适应硬件配置
2. **超时设置**: 根据任务特性调整 `TASK_TIMEOUT`
3. **日志轮转**: 设置日志文件定期轮转避免占用过多空间
4. **资源限制**: 在Docker中设置CPU和内存限制

## 扩展开发

### 添加新的API端点

在 `backend/app/routes/` 中创建新的蓝图：

```python
from flask import Blueprint, jsonify

bp = Blueprint('custom', __name__, url_prefix='/api/custom')

@bp.route('/endpoint', methods=['GET'])
def custom_endpoint():
    return jsonify({'message': 'Custom endpoint'})
```

在 `backend/app/__init__.py` 中注册：

```python
from app.routes import custom_routes
app.register_blueprint(custom_routes.bp)
```

### 添加前端新页面

在 `frontend/src/views/` 中创建新的Vue组件，并在 `frontend/src/router.js` 中配置路由。

## 许可证

MIT

## 支持

如有问题或建议，欢迎提交Issue或Pull Request！
