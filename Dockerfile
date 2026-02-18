FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 安装系统依赖（akshare可能需要）
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制项目代码
COPY . .

# 暴露端口
EXPOSE 8000

# 启动命令 - 修改为读取 $PORT 环境变量
CMD sh -c "uvicorn app:app --host 0.0.0.0 --port ${PORT:-8000}"
