# V5 开发规划 - SWE-bench 评估集成版

## 项目目标

V5 版本的核心目标是将 my-coding-agent 与 SWE-bench 评估框架集成，使 agent 能够在真实世界的 GitHub issue 修复任务上进行标准化评估，并通过自动化评估流程持续改进性能。

## 核心功能

### 1. SWE-bench 适配器模块
- **数据加载器**：从 HuggingFace 加载 SWE-bench 数据集（Lite/Full/Verified）
- **任务转换器**：将 SWE-bench 实例转换为 agent 可理解的任务格式
- **补丁生成器**：将 agent 的执行结果转换为标准 git diff 格式
- **预测文件生成**：自动生成符合 SWE-bench 要求的 JSONL 预测文件

### 2. 评估集成
- **推理接口**：实现 `swebench.inference` 兼容的推理接口
- **批量处理**：支持批量处理多个实例，自动断点续传
- **结果收集**：收集并汇总评估结果，生成性能报告

### 3. 工具扩展
- **Git 工具**：添加 git 相关操作（apply patch, checkout, diff 等）
- **测试运行工具**：支持运行测试套件验证修复效果
- **代码库导航**：增强代码库探索能力，支持大型项目

## 架构设计

```
V5 Architecture
├── swebench/                    # SWE-bench 集成模块（新增）
│   ├── adapter.py              # 数据适配器
│   ├── inference.py            # 推理接口
│   ├── evaluator.py            # 评估包装器
│   └── patch_generator.py      # 补丁生成器
├── core/                       # 核心业务逻辑（继承 v4）
├── tools/                      # 工具系统（扩展）
│   └── git_tools.py           # Git 操作工具（新增）
├── evaluation/                 # 评估相关（新增）
│   ├── runner.py              # 评估运行器
│   └── reporter.py           # 结果报告生成
└── app.py                      # 应用入口（扩展）
```

## 数据流设计

### 推理流程
```
SWE-bench Instance
  ↓
Adapter (转换为 Agent Task)
  ↓
Agent Core (执行任务)
  ↓
Patch Generator (提取补丁)
  ↓
JSONL Prediction File
  ↓
SWE-bench Harness (评估)
  ↓
Evaluation Report
```

## SWE-bench 评估机制详解

### 评估流程概览

SWE-bench 使用 Docker 容器化环境进行标准化评估，确保结果的可重现性。整个评估流程如下：

#### 1. 环境准备阶段

**Docker 镜像构建（三层架构）**
- **Base Image**：基础操作系统镜像（Ubuntu 22.04）
- **Environment Image**：安装项目依赖和运行环境（Python/Node.js 等版本、依赖包）
- **Instance Image**：克隆代码库到指定 commit（`base_commit`），应用测试补丁（`test_patch`）

**TestSpec 生成**
- 从 SWE-bench 实例中提取测试规范
- 包含：`FAIL_TO_PASS`（需要从失败变为通过的测试）和 `PASS_TO_PASS`（需要保持通过的测试）
- 生成评估脚本（`eval_script`），用于运行测试套件

#### 2. 补丁应用阶段

**补丁应用流程**
1. 将模型生成的补丁（`model_patch`）复制到容器中
2. 尝试多种方式应用补丁：
   - `git apply --verbose`
   - `git apply --verbose --reject`（允许部分应用）
   - `patch --batch --fuzz=5 -p1 -i`（模糊匹配）
3. 如果所有方式都失败，标记为 `APPLY_PATCH_FAIL`，评估终止

**验证补丁应用**
- 记录应用前后的 `git diff`，确保补丁正确应用
- 检查是否有权限或文件模式问题

#### 3. 测试执行阶段

**评估脚本执行**
- 运行 `eval_script`，通常包含：
  1. 重置测试文件到 `base_commit` 状态（避免测试补丁影响）
  2. 应用测试补丁（`test_patch`）
  3. 运行测试套件（如 `pytest`、`npm test` 等）
  4. 捕获测试输出

**测试输出解析**
- 使用特定于仓库的日志解析器（`log_parsers`）
- 解析测试结果，生成测试状态映射（`status_map`）
- 识别每个测试用例的状态：`PASSED`、`FAILED`、`ERROR`、`SKIPPED`、`XFAIL`

#### 4. 结果评估阶段

**评估指标计算**

**Fail-to-Pass (F2P) - 解决率**
- 衡量原本失败的测试是否通过
- 公式：`F2P = 通过的 F2P 测试数 / 总 F2P 测试数`
- 这是**核心指标**，表示问题是否被解决

**Pass-to-Pass (P2P) - 维护率**
- 衡量原本通过的测试是否仍然通过
- 公式：`P2P = 通过的 P2P 测试数 / 总 P2P 测试数`
- 确保修复没有破坏现有功能

**解决状态判断（Resolved Status）**

```python
if F2P == 1.0 and P2P == 1.0:
    status = "RESOLVED_FULL"  # 完全解决
elif F2P > 0 and F2P < 1.0 and P2P == 1.0:
    status = "RESOLVED_PARTIAL"  # 部分解决
else:
    status = "RESOLVED_NO"  # 未解决
```

**最终判断**
- `resolved = True` 仅当 `status == "RESOLVED_FULL"`
- 即：所有 F2P 测试通过 + 所有 P2P 测试通过

#### 5. 报告生成阶段

**评估报告内容**
```json
{
  "instance_id": "sympy__sympy-20590",
  "patch_exists": true,
  "patch_successfully_applied": true,
  "resolved": true/false,
  "tests_status": {
    "FAIL_TO_PASS": {
      "success": ["test_case_1", ...],
      "failure": ["test_case_2", ...]
    },
    "PASS_TO_PASS": {
      "success": ["test_case_3", ...],
      "failure": ["test_case_4", ...]
    }
  }
}
```

### 关键设计特点

1. **容器化隔离**：每个评估在独立的 Docker 容器中运行，避免环境污染
2. **可重现性**：通过固定 commit 和依赖版本，确保结果一致
3. **多策略补丁应用**：使用多种 git/patch 命令，提高补丁应用成功率
4. **测试分类**：区分 F2P 和 P2P，同时评估修复效果和回归风险
5. **详细日志**：记录每个步骤的输出，便于调试和分析

### 评估失败场景

1. **补丁应用失败**：补丁格式错误或无法应用 → `APPLY_PATCH_FAIL`
2. **环境初始化失败**：依赖安装失败 → `INSTALL_FAIL`
3. **测试执行错误**：测试框架崩溃 → `TESTS_ERROR`
4. **测试超时**：超过时间限制 → `TESTS_TIMEOUT`
5. **部分测试失败**：F2P 或 P2P 测试未全部通过 → `resolved = False`

### 对我们的影响

1. **补丁格式要求严格**：必须生成有效的 git diff 格式
2. **需要处理多文件修改**：补丁可能涉及多个文件
3. **测试覆盖考虑**：修复需要确保不破坏现有测试
4. **错误处理**：需要优雅处理补丁应用失败等情况

### 任务转换示例
```python
# SWE-bench 实例
{
  "instance_id": "sympy__sympy-20590",
  "problem_statement": "Issue description...",
  "repo": "sympy/sympy",
  "base_commit": "abc123..."
}

# 转换为 Agent 任务
"""
Repository: sympy/sympy
Issue: [problem_statement]
Base commit: abc123

Please analyze the issue and generate a patch to fix it.
You have access to the codebase at the base commit.
"""
```

## 实施计划

### Phase 1: 基础适配（Week 1）- TDD 任务清单

#### 任务 1.1: SWE-bench 数据加载器

**说明**：SWE-bench 代码仓库本身不包含完整数据集，只包含辅助资源（如 environment.yml）。完整数据集托管在 HuggingFace 上（`SWE-bench/SWE-bench_Lite` 等）。数据加载器需要支持从 HuggingFace 下载，同时也支持本地 JSON/JSONL 文件用于测试。

**测试阶段（Red）**
- [x] 编写测试：测试从 HuggingFace 加载 SWE-bench Lite 数据集（主要数据源）
- [x] 编写测试：测试从本地 JSON/JSONL 文件加载（用于测试和自定义数据）
- [x] 编写测试：测试加载单个实例的字段完整性验证
- [x] 编写测试：测试处理无效数据集名称的错误处理
- [x] 编写测试：测试实例 ID 过滤功能
- [x] 编写测试：测试处理网络错误和 HuggingFace 连接失败的情况

**实现阶段（Green）**
- [x] 创建 `swebench/loader.py` 模块
- [x] 实现 `load_dataset()` 函数，支持 HuggingFace 和本地文件
- [x] 实现 `validate_instance()` 函数，验证必需字段
- [x] 实现 `filter_instances()` 函数，支持按 instance_id 过滤
- [x] 添加错误处理和日志记录

**重构阶段（Refactor）**
- [x] 提取配置常量（数据集名称、字段名等）
- [x] 优化错误消息的可读性
- [x] 添加类型提示和文档字符串

#### 任务 1.2: 任务转换器（Instance → Agent Task）

**测试阶段（Red）**
- [x] 编写测试：测试将 SWE-bench 实例转换为 agent 任务字符串
- [x] 编写测试：验证任务包含所有关键信息（repo, issue, base_commit）
- [x] 编写测试：测试处理缺失字段的默认值
- [x] 编写测试：测试任务格式的一致性和可读性
- [x] 编写测试：测试特殊字符和换行符的处理

**实现阶段（Green）**
- [x] 创建 `swebench/adapter.py` 模块
- [x] 实现 `convert_to_task()` 函数，生成任务描述
- [x] 实现任务模板系统，支持自定义格式
- [x] 添加字段提取和格式化逻辑
- [x] 实现任务验证功能

**重构阶段（Refactor）**
- [x] 提取任务模板为可配置项（DEFAULT_TASK_TEMPLATE）
- [x] 优化任务描述的清晰度和结构
- [ ] 添加任务长度和复杂度统计（可选，后续优化）

#### 任务 1.3: 补丁提取器（Agent Output → Git Diff）

**测试阶段（Red）**
- [x] 编写测试：测试从 agent 消息历史中提取文件修改
- [x] 编写测试：测试生成单文件 git diff 格式
- [x] 编写测试：测试生成多文件 git diff 格式
- [x] 编写测试：测试处理空修改和无修改的情况
- [x] 编写测试：测试 diff 格式的正确性（符合 git 标准）
- [x] 编写测试：测试处理二进制文件和特殊字符

**实现阶段（Green）**
- [x] 创建 `swebench/patch_generator.py` 模块
- [x] 实现消息历史分析器，追踪 write_file/edit_file 调用
- [x] 实现文件内容对比功能（使用 difflib）
- [x] 实现 git diff 格式生成器
- [x] 实现多文件补丁合并逻辑
- [x] 添加补丁验证功能（通过测试验证）

**重构阶段（Refactor）**
- [x] 优化 diff 算法的性能和准确性（使用 difflib.unified_diff）
- [x] 提取 diff 格式生成为独立函数（generate_git_diff）
- [ ] 添加补丁统计信息（文件数、行数等）（可选，后续优化）

#### 任务 1.4: 基础推理接口

**测试阶段（Red）**
- [x] 编写测试：测试推理接口的基本调用流程
- [x] 编写测试：测试处理单个实例的完整流程（加载→转换→执行→提取）
- [x] 编写测试：测试生成符合 SWE-bench 格式的预测文件
- [x] 编写测试：测试错误处理和异常情况
- [x] 编写测试：测试与 agent_core 的集成

**实现阶段（Green）**
- [x] 创建 `swebench/inference.py` 模块
- [x] 实现 `run_inference()` 函数，处理单个实例
- [x] 实现预测结果格式化（JSONL 格式）
- [x] 集成数据加载器、任务转换器、补丁生成器
- [x] 实现与 agent_core 的接口适配
- [x] 添加进度跟踪和日志记录

**重构阶段（Refactor）**
- [ ] 提取配置参数（模型、超参数等）
- [ ] 优化错误处理和用户反馈
- [ ] 添加性能指标收集

#### Phase 1 集成测试

**端到端测试**
- [x] 测试完整流程：从数据集加载到生成预测文件
- [x] 测试在真实 SWE-bench Lite 实例上的运行
- [ ] 验证生成的预测文件格式符合 SWE-bench 要求
- [ ] 性能测试：处理时间和资源消耗

**文档和清理**
- [ ] 更新模块文档字符串
- [ ] 创建使用示例和快速开始指南
- [ ] 代码审查和清理未使用的导入
- [ ] 确保所有测试通过

### Phase 2: 评估集成（Week 2）
- [ ] 集成 SWE-bench harness
- [ ] 实现批量推理流程
- [ ] 添加断点续传功能
- [ ] 实现结果收集和报告

### Phase 3: 工具扩展（Week 3）
- [ ] 添加 Git 操作工具
- [ ] 添加测试运行工具
- [ ] 优化代码库导航能力
- [ ] 增强文件搜索和代码理解

### Phase 4: 优化与测试（Week 4）
- [ ] 性能优化（并发处理、缓存）
- [ ] 错误处理和重试机制
- [ ] 在 SWE-bench Lite 上测试
- [ ] 生成性能基准报告

## 技术要点

### 1. 补丁生成策略
- 监控 agent 的文件修改操作（write_file, edit_file）
- 记录修改前后的文件内容差异
- 使用 diff 算法生成标准 git diff 格式
- 处理多文件修改场景

### 2. 上下文管理
- 利用 v4 的对话压缩能力处理长上下文
- 针对大型代码库实现智能检索（RAG）
- 优化 token 使用，控制 API 成本

### 3. 错误处理
- 补丁格式验证
- 应用失败重试机制
- 详细的错误日志记录
- 优雅降级策略

### 4. 性能优化
- 并行处理多个实例
- Docker 镜像缓存利用
- 增量评估（只评估新预测）
- 结果缓存机制

## 评估指标

- **Resolution Rate**：成功解决的实例比例
- **Patch Quality**：补丁格式正确率
- **Execution Efficiency**：平均执行时间和 token 消耗
- **Error Analysis**：失败原因分类统计

## 预期成果

1. **标准化评估**：在 SWE-bench Lite 上建立性能基准
2. **持续改进**：通过评估反馈优化 agent 策略
3. **可扩展性**：支持扩展到完整 SWE-bench 数据集
4. **文档完善**：提供完整的使用和评估指南

## 下一步行动

1. 开始 Phase 1 开发，实现基础适配器
2. 在 SWE-bench Lite 上运行初步测试
3. 根据测试结果迭代优化
4. 逐步扩展到完整功能集

---

**版本**: V5 - SWE-bench Integration  
**状态**: 规划阶段  
**目标完成时间**: 4 周
