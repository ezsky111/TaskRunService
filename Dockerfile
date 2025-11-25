FROM python:3.11-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 复制后端依赖并安装（CI 已构建前端到 `frontend/dist`）
COPY backend/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# 复制后端代码
COPY backend/ /app/

# 复制由 CI 预构建的前端静态资源到镜像根目录下的 /frontend/dist
# 注意：不要在本地 Docker 构建上下文中忽略 `frontend/dist`，否则这一步会失败。
COPY frontend/dist /frontend/dist

# 创建必要的目录
RUN mkdir -p /app/tasks /app/logs

# 暴露端口
EXPOSE 5000

# 健康检查（保持与应用相同的接口）
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:5000/api/system/health || exit 1

# 启动应用（在容器中运行时，请在 /app 下执行 run.py）
CMD ["python", "run.py"]
