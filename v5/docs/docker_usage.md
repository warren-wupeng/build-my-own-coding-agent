# Docker 运行环境使用指南

## 概述

Docker 运行环境为 Agent 提供了一个完全隔离的执行环境，防止 Agent 在测试过程中误操作破坏宿主机上的文件。

## 安全特性

### 1. 文件系统隔离
- **只读挂载**: 项目代码以只读方式挂载，Agent 无法修改
- **输出目录**: 只有 `./output` 目录可写，用于保存结果
- **临时文件**: 使用 tmpfs，容器重启后自动清理

### 2. 用户权限
- **非 root 用户**: 容器内以 `agent` 用户（UID 1000）运行
- **最小权限**: 只授予必要的文件系统访问权限

### 3. 资源限制
- **内存限制**: 默认 8GB
- **CPU 限制**: 默认 4 核
- **可配置**: 可通过 docker-compose.yml 或命令行调整

### 4. 网络隔离
- **默认桥接网络**: 容器在隔离的网络中运行
- **可访问外网**: 用于 LLM API 调用和 HuggingFace 访问

## 快速开始

### 方法 1: 使用 docker-run.sh 脚本（推荐）

```bash
# 设置 API key
export OPENROUTER_API_KEY="your-api-key"

# 运行 Agent（显示帮助）
./docker-run.sh

# 运行 Agent 执行任务
./docker-run.sh "your task description"

# 运行 SWE-bench 推理示例
./docker-run.sh python examples/show_inference.py
```

### 方法 2: 使用 docker-compose

```bash
# 设置 API key
export OPENROUTER_API_KEY="your-api-key"

# 构建镜像
docker-compose build

# 运行 Agent
docker-compose run --rm agent python agent.py "your task description"

# 运行示例
docker-compose run --rm agent python examples/show_inference.py
```

### 方法 3: 直接使用 docker 命令

```bash
# 构建镜像
docker build -t my-coding-agent-v5:latest .

# 运行容器
docker run --rm -it \
  --user agent \
  --read-only \
  --tmpfs /tmp:noexec,nosuid,size=1g \
  -v "$(pwd)/output:/output" \
  -v "$(pwd):/workspace:ro" \
  -e OPENROUTER_API_KEY="${OPENROUTER_API_KEY}" \
  my-coding-agent-v5:latest \
  python agent.py "your task description"
```

## 目录结构

### 容器内目录

```
/workspace/          # 项目代码（只读）
  ├── core/
  ├── tools/
  ├── swebench/
  └── ...

/output/            # 输出目录（可写）
  ├── predictions.jsonl
  └── ...

/tmp/               # 临时文件（tmpfs，重启后清空）
```

### 宿主机目录

```
./                  # 项目根目录（只读挂载到容器）
./output/           # 输出目录（可写，挂载到容器 /output）
```

## 安全说明

### 容器内可以做什么

✅ **允许的操作**:
- 读取项目代码（只读）
- 在 `/output` 目录写入文件
- 在 `/tmp` 创建临时文件
- 调用 LLM API
- 访问网络（HuggingFace 等）

❌ **禁止的操作**:
- 修改项目源代码
- 访问宿主机其他目录
- 安装系统软件包
- 修改系统配置
- 以 root 权限运行

### 文件访问限制

| 路径 | 权限 | 说明 |
|------|------|------|
| `/workspace` | 只读 | 项目代码，Agent 无法修改 |
| `/output` | 读写 | 输出目录，用于保存结果 |
| `/tmp` | 读写 | 临时文件，容器重启后清空 |
| 其他路径 | 无 | 容器内其他路径不可访问 |

## 使用场景

### 1. 运行 Agent 执行任务

```bash
./docker-run.sh "Create a Python web application"
```

### 2. 运行 SWE-bench 推理

```bash
./docker-run.sh python examples/show_inference.py
```

### 3. 运行测试

```bash
# 运行单元测试
./docker-run.sh python -m pytest tests/ -m "not integration"

# 运行集成测试（需要网络）
./docker-run.sh python -m pytest tests/ -m integration
```

### 4. 交互式调试

```bash
# 进入容器 shell
docker run --rm -it \
  --user agent \
  --read-only \
  --tmpfs /tmp:noexec,nosuid,size=1g \
  -v "$(pwd)/output:/output" \
  -v "$(pwd):/workspace:ro" \
  -e OPENROUTER_API_KEY="${OPENROUTER_API_KEY}" \
  my-coding-agent-v5:latest \
  /bin/bash
```

## 配置选项

### 调整资源限制

编辑 `docker-compose.yml`:

```yaml
deploy:
  resources:
    limits:
      cpus: '8'      # 增加 CPU
      memory: 16G    # 增加内存
```

### 调整临时文件大小

编辑 `docker-run.sh`:

```bash
--tmpfs /tmp:noexec,nosuid,size=2g  # 增加到 2GB
```

### 添加环境变量

编辑 `docker-compose.yml`:

```yaml
environment:
  - OPENROUTER_API_KEY=${OPENROUTER_API_KEY}
  - CUSTOM_VAR=value
```

## 故障排除

### 问题 1: 容器无法启动

**错误**: `docker: Error response from daemon: ...`

**解决**:
- 检查 Docker 是否运行: `docker info`
- 检查镜像是否存在: `docker images`
- 重新构建镜像: `docker build -t my-coding-agent-v5:latest .`

### 问题 2: 权限错误

**错误**: `Permission denied`

**解决**:
- 确保使用 `--user agent` 参数
- 检查输出目录权限: `chmod 755 output/`

### 问题 3: 无法写入输出目录

**错误**: `Read-only file system`

**解决**:
- 检查挂载点是否正确: `docker inspect <container>`
- 确保使用 `-v "$(pwd)/output:/output"` 挂载

### 问题 4: API key 未设置

**错误**: `OPENROUTER_API_KEY environment variable not set`

**解决**:
```bash
export OPENROUTER_API_KEY="your-key-here"
# 或者在 docker-compose.yml 中设置
```

## 最佳实践

1. **始终使用 Docker 运行**: 在测试和开发时使用 Docker 环境
2. **定期清理**: 清理未使用的容器和镜像
   ```bash
   docker container prune
   docker image prune
   ```
3. **监控资源**: 使用 `docker stats` 监控容器资源使用
4. **备份输出**: 定期备份 `./output` 目录中的重要结果
5. **版本控制**: 不要将 `./output` 目录提交到 Git

## 与本地运行的区别

| 特性 | 本地运行 | Docker 运行 |
|------|---------|------------|
| 文件系统访问 | 完整访问 | 受限访问 |
| 安全性 | 低（可能破坏文件） | 高（完全隔离） |
| 性能 | 快 | 稍慢（容器开销） |
| 环境一致性 | 依赖本地环境 | 完全一致 |
| 清理 | 手动清理 | 自动清理 |

## 总结

Docker 运行环境提供了：
- ✅ 完全隔离的执行环境
- ✅ 防止误操作破坏宿主机文件
- ✅ 一致的运行环境
- ✅ 易于清理和重置
- ✅ 资源限制和监控

推荐在开发和测试时始终使用 Docker 环境运行 Agent。
