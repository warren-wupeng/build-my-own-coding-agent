# Docker 运行环境

## 快速开始

### 1. 构建 Docker 镜像

```bash
docker build -t my-coding-agent-v5:latest .
```

### 2. 运行 Agent

```bash
# 设置 API key
export OPENROUTER_API_KEY="your-api-key"

# 使用便捷脚本运行
./docker-run.sh "your task description"

# 或使用 docker-compose
docker-compose run --rm agent python agent.py "your task description"
```

## 安全特性

### ✅ 文件系统隔离
- 项目代码以**只读**方式挂载（通过 tmpfs 处理 .venv）
- 只有 `./output` 目录可写，用于保存结果
- Agent 无法修改宿主机上的项目文件

### ✅ 用户权限
- 以非 root 用户（`agent`，UID 1000）运行
- 最小权限原则

### ✅ 资源限制
- 内存限制：8GB
- CPU 限制：4 核
- 可通过 docker-compose.yml 调整

### ✅ 自动清理
- 容器退出后自动删除（`--rm`）
- 临时文件使用 tmpfs，重启后清空

## 目录说明

```
容器内:
  /workspace/     # 项目代码（通过 tmpfs 处理 .venv，避免修改宿主机）
  /output/        # 输出目录（可写，映射到宿主机的 ./output）
  /tmp/           # 临时文件（tmpfs，重启后清空）

宿主机:
  ./              # 项目根目录（挂载到容器，但通过 tmpfs 保护 .venv）
  ./output/       # 输出目录（Agent 可以写入结果）
```

## 使用示例

### 运行 Agent 执行任务

```bash
./docker-run.sh "Create a Python web application"
```

### 运行 SWE-bench 推理

```bash
./docker-run.sh python examples/show_inference.py
```

### 运行测试

```bash
./docker-run.sh python -m pytest tests/ -m "not integration"
```

## 注意事项

1. **首次运行**: 需要构建镜像，可能需要几分钟
2. **网络访问**: 容器需要访问外网（LLM API、HuggingFace）
3. **输出目录**: 结果保存在 `./output` 目录
4. **API Key**: 通过环境变量 `OPENROUTER_API_KEY` 传递

## 故障排除

### Docker 未运行
```bash
# 检查 Docker 状态
docker info
```

### 权限问题
```bash
# 确保输出目录有写权限
chmod 755 output/
```

### 镜像构建失败
```bash
# 检查网络连接
# 或使用国内镜像源（需要修改 Dockerfile）
```

详细文档请参考: [docs/docker_usage.md](./docs/docker_usage.md)
