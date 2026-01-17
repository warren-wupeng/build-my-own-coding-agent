# SWE-bench 评估架构详解

本文档详细说明 SWE-bench 评估过程中，哪些代码在宿主机运行，哪些在容器内运行。

## 整体架构概览

```
┌─────────────────────────────────────────────────────────────┐
│                      宿主机 (Host)                            │
│                                                               │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  1. 推理阶段 (Inference) - 生成 Patch                │   │
│  │     - run_inference()                                │   │
│  │     - AgentCore 执行                                  │   │
│  │     - 调用 LLM API                                   │   │
│  │     - 生成 predictions.jsonl                         │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                               │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  2. 评估阶段 (Evaluation) - 测试 Patch               │   │
│  │     - run_evaluation.py (主程序)                     │   │
│  │     - 读取 predictions.jsonl                         │   │
│  │     - 构建 Docker 镜像                               │   │
│  │     - 管理容器生命周期                                │   │
│  │     - 复制文件到容器                                  │   │
│  │     - 执行容器内命令                                  │   │
│  │     - 读取容器输出                                    │   │
│  │     - 生成评估报告                                    │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ Docker API
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    Docker 容器 (Container)                    │
│                                                               │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  容器构建阶段 (Image Build)                          │   │
│  │  - Base Image: 基础操作系统环境                      │   │
│  │  - Env Image: 安装依赖 (conda, pip 等)              │   │
│  │  - Instance Image: 克隆代码库                        │   │
│  │    * git clone <repo>                                │   │
│  │    * git reset --hard <base_commit>                  │   │
│  │    * 安装项目依赖                                     │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                               │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  容器运行阶段 (Container Runtime)                    │   │
│  │  - 应用 patch: git apply patch.diff                  │   │
│  │  - 运行测试: pytest/tox/...                          │   │
│  │  - 输出测试结果                                       │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

## 详细代码执行位置

### 宿主机运行的代码

#### 1. 推理阶段（Inference Phase）

**位置**: 宿主机环境

**代码**:
- `swebench/inference/run_api.py` - 推理主程序
- `run_inference()` - 你的推理函数
- `AgentCore` - Agent 核心逻辑
- LLM API 调用（OpenAI, Anthropic 等）

**功能**:
- 加载 SWE-bench 数据集
- 将实例转换为任务描述
- Agent 执行任务（可能需要访问代码库）
- 生成 git diff 格式的 patch
- 写入 `predictions.jsonl` 文件

**注意**: 
- Agent 如果需要访问代码库，需要自己克隆到宿主机
- 或者通过其他方式访问代码（如 API、文件系统等）

#### 2. 评估阶段（Evaluation Phase）

**位置**: 宿主机环境

**代码**:
- `swebench/harness/run_evaluation.py` - 评估主程序
- `swebench/harness/docker_build.py` - Docker 镜像构建
- `swebench/harness/docker_utils.py` - Docker 操作工具
- `swebench/harness/grading.py` - 评估报告生成

**主要函数**:
```python
# run_evaluation.py
def main():
    # 1. 读取 predictions.jsonl
    predictions = get_predictions_from_file(predictions_path)
    
    # 2. 加载数据集
    dataset = load_swebench_dataset(dataset_name)
    
    # 3. 构建 Docker 镜像（如果需要）
    build_env_images(...)
    
    # 4. 对每个实例运行评估
    for pred in predictions:
        run_instance(test_spec, pred, ...)

def run_instance(test_spec, pred, ...):
    # 1. 构建/启动容器
    container = build_container(...)
    container.start()
    
    # 2. 复制 patch 文件到容器
    patch_file.write_text(pred["model_patch"])
    copy_to_container(container, patch_file, DOCKER_PATCH)
    
    # 3. 在容器内应用 patch
    container.exec_run("git apply " + DOCKER_PATCH)
    
    # 4. 复制 eval 脚本到容器
    copy_to_container(container, eval_file, "/eval.sh")
    
    # 5. 在容器内运行测试
    test_output = exec_run_with_timeout(container, "/bin/bash /eval.sh")
    
    # 6. 读取测试输出并生成报告
    report = get_eval_report(test_spec, pred, test_output)
```

### 容器内运行的代码

#### 1. 镜像构建阶段（Image Build）

**位置**: Docker 镜像构建时

**代码**: `test_spec.repo_script_list` 和 `test_spec.env_script_list`

**执行内容**:
```bash
# repo_script_list (在构建 Instance Image 时执行)
git clone https://github.com/{repo} /{env_name}
cd /{env_name}
git reset --hard {base_commit}
git remote remove origin
# 清理 git 历史，确保看不到未来提交
# 安装项目依赖
conda activate {env_name}
{pip install / python setup.py install / ...}

# env_script_list (在构建 Env Image 时执行)
# 安装 conda 环境
# 安装系统依赖
# 配置测试环境
```

#### 2. 容器运行阶段（Container Runtime）

**位置**: 容器启动后

**代码**: `test_spec.eval_script`

**执行内容**:
```bash
#!/bin/bash
set -uxo pipefail

# 1. 激活环境
source /opt/miniconda3/bin/activate
conda activate {env_name}
cd /{env_name}

# 2. 应用 patch（由宿主机通过 exec_run 执行）
git apply /patch.diff

# 3. 重置测试文件到 base_commit
git checkout {base_commit} {test_files}

# 4. 应用测试补丁
git apply <<EOF
{test_patch}
EOF

# 5. 运行测试
: 'START_TEST_OUTPUT'
{pytest / tox / python -m unittest / ...}
: 'END_TEST_OUTPUT'

# 6. 恢复测试文件
git checkout {base_commit} {test_files}
```

## 数据流

### 推理阶段数据流

```
SWE-bench Dataset (HuggingFace)
    ↓
load_dataset() [宿主机]
    ↓
Instance (dict) [宿主机]
    ↓
convert_to_task() [宿主机]
    ↓
AgentCore.execute_task() [宿主机]
    ↓
LLM API Call [网络]
    ↓
Agent 工具调用 (read_file, write_file, ...) [宿主机]
    ↓
extract_patch_from_messages() [宿主机]
    ↓
predictions.jsonl [宿主机文件系统]
```

### 评估阶段数据流

```
predictions.jsonl [宿主机]
    ↓
get_predictions_from_file() [宿主机]
    ↓
pred = {"instance_id": "...", "model_patch": "..."} [宿主机]
    ↓
build_container() [宿主机 → Docker API]
    ↓
Container with codebase [容器内]
    ↓
copy_to_container(patch_file) [宿主机 → Docker API → 容器]
    ↓
container.exec_run("git apply patch.diff") [容器内执行]
    ↓
container.exec_run("/bin/bash /eval.sh") [容器内执行]
    ↓
Test Output [容器内 → Docker API → 宿主机]
    ↓
get_eval_report() [宿主机]
    ↓
report.json [宿主机文件系统]
```

## 关键点总结

### 1. 推理阶段（生成 Patch）

- **位置**: 完全在宿主机运行
- **Agent 代码**: 在宿主机执行
- **LLM API**: 从宿主机调用
- **代码库访问**: Agent 需要自己处理（克隆到宿主机或通过其他方式）
- **输出**: `predictions.jsonl` 文件（宿主机文件系统）

### 2. 评估阶段（测试 Patch）

- **控制逻辑**: 在宿主机运行（`run_evaluation.py`）
- **Docker 操作**: 通过 Docker API 从宿主机执行
- **代码库**: 在容器内（构建镜像时已克隆）
- **Patch 应用**: 在容器内执行（`git apply`）
- **测试执行**: 在容器内执行（`eval.sh`）
- **结果收集**: 从容器读取到宿主机

### 3. 容器内的内容

- ✅ 代码库（已克隆并切换到 base_commit）
- ✅ 项目依赖（已安装）
- ✅ 测试环境（已配置）
- ✅ Patch 文件（从宿主机复制）
- ✅ Eval 脚本（从宿主机复制）
- ❌ Agent 代码（不在容器内）
- ❌ LLM API 调用（不在容器内）

## 对你的代码的影响

### 当前测试代码的问题

你的 `test_real_swebench_lite_instance_with_real_agent()` 测试：

```python
prediction = run_inference(instance, agent, ...)
```

这段代码在**宿主机**运行，但：
- 代码库不在宿主机（astropy 仓库未克隆）
- Agent 无法访问需要修复的代码文件
- 因此无法生成实际的 patch

### 解决方案

#### 方案 1: 在宿主机克隆代码库（推荐用于测试）

```python
# 在测试中，手动克隆代码库到临时目录
import subprocess
import tempfile

work_dir = tempfile.mkdtemp()
subprocess.run([
    "git", "clone", 
    f"https://github.com/{instance['repo']}", 
    work_dir
])
subprocess.run(["git", "reset", "--hard", instance["base_commit"]], cwd=work_dir)

# 让 Agent 在克隆的代码库目录中工作
# 修改 Agent 的工作目录或通过工具访问代码
```

#### 方案 2: 使用 SWE-bench 的容器环境（推荐用于生产）

修改评估流程，让 Agent 在容器内运行：
- 在容器内安装 Agent 代码
- 在容器内执行推理
- 直接在容器内生成和应用 patch

这需要自定义 SWE-bench 的评估流程。

## 总结

- **推理阶段**: 完全在宿主机，Agent 需要自己处理代码库访问
- **评估阶段**: 控制逻辑在宿主机，实际测试在容器内
- **代码库**: 在容器内（构建时克隆），推理阶段需要自己克隆到宿主机
