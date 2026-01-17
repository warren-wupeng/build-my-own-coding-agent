# Docker 构建故障排除

## 内存不足错误

### 错误现象

```
ERROR: process "/bin/sh -c apt-get update && apt-get install..." did not complete successfully: cannot allocate memory
ResourceExhausted: cannot allocate memory
```

### 原因分析

1. **Docker 内存限制过低**: Docker Desktop 默认内存可能只有 2-4GB
2. **build-essential 体积大**: 包含 gcc/g++ 等编译工具，需要 ~400MB 空间
3. **系统内存不足**: 宿主机可用内存不足

### 解决方案

#### 方案 1: 增加 Docker 内存限制（推荐）

1. 打开 Docker Desktop
2. 进入 Settings → Resources → Advanced
3. 增加 Memory 到至少 **8GB**（推荐 12GB+）
4. 点击 "Apply & Restart"

#### 方案 2: 清理 Docker 资源

```bash
# 清理未使用的镜像、容器、缓存
docker system prune -a --volumes

# 查看 Docker 资源使用
docker system df
```

#### 方案 3: 优化 Dockerfile（已优化）

已优化 Dockerfile，将依赖安装分为两步：
- 第一步：安装基础工具（git, curl 等）
- 第二步：安装编译工具（gcc, g++ 等）

这样可以减少单次构建的内存压力。

#### 方案 4: 使用多阶段构建（高级）

如果内存仍然不足，可以使用多阶段构建：

```dockerfile
# Stage 1: Build dependencies
FROM python:3.11-slim as builder
RUN apt-get update && apt-get install -y build-essential
# ... install Python packages ...

# Stage 2: Runtime
FROM python:3.11-slim
COPY --from=builder /usr/local /usr/local
# ... copy application code ...
```

### 检查 Docker 资源

```bash
# 查看 Docker 内存限制
docker info | grep -i memory

# 查看 Docker 资源使用
docker system df

# 查看运行中的容器资源使用
docker stats --no-stream
```

### 预防措施

1. **定期清理**: 定期运行 `docker system prune` 清理未使用的资源
2. **合理配置**: 根据系统内存合理配置 Docker Desktop 内存限制
3. **监控使用**: 使用 `docker stats` 监控容器资源使用

## 权限错误

### 错误现象

```
error: Failed to query Python interpreter at `/tmp/.local/share/uv/python/.../bin/python3.14`
  Caused by: Permission denied (os error 13)
```

### 原因分析

1. **tmpfs 使用了 `noexec` 标志**: `/tmp` 挂载时使用了 `noexec`，阻止执行其中的文件
2. **uv 需要执行 Python 解释器**: `uv` 下载的 Python 解释器存储在 `/tmp/.local/share/uv/python/` 下，需要执行权限

### 解决方案

已修复：移除了 `--tmpfs /tmp` 中的 `noexec` 标志，保留 `nosuid` 以保持安全性。

**为什么移除 `noexec` 是安全的：**
- 容器使用非 root 用户运行（`--user agent`）
- 工作空间是只读的，无法修改代码
- 只有 `/output` 和 `/tmp` 可写
- 容器是临时的（`--rm`），运行结束后自动删除
- 保留了 `nosuid` 标志，防止 setuid 攻击

## 其他常见问题

### 问题 2: 网络超时

**错误**: `dial tcp: i/o timeout`

**解决**:
- 检查网络连接
- 使用国内镜像源（需要修改 Dockerfile）
- 增加超时时间

### 问题 3: 权限错误

**错误**: `Permission denied`

**解决**:
- 确保使用 `--user agent` 参数
- 检查挂载目录权限
- 确保输出目录有写权限

### 问题 4: 镜像构建缓慢

**解决**:
- 使用 `.dockerignore` 减少构建上下文
- 利用 Docker 缓存层
- 使用多阶段构建
