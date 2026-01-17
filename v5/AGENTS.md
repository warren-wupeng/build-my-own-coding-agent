# 开发规范和约定

本文档记录了 my-coding-agent v5 项目的开发规范和约定，供 AI 助手在开发过程中遵循。

## 测试编写规范

### 使用函数风格而非类风格

**规则**：所有测试必须使用函数风格编写，不要使用类来组织测试。

#### ✅ 正确示例（函数风格）

```python
import pytest

def test_load_from_json_file():
    """Test loading from local JSON file"""
    # 测试代码
    dataset = load_dataset("test.json")
    assert len(dataset) == 1

def test_validate_instance():
    """Test instance validation"""
    instance = {"instance_id": "test__repo-1", ...}
    assert validate_instance(instance) == True
```

#### ❌ 错误示例（类风格）

```python
import pytest

class TestLoadDataset:
    def test_load_from_json_file(self):
        # 测试代码
        pass
    
    def test_validate_instance(self):
        # 测试代码
        pass
```

### 原因

1. **简洁性**：函数风格更简洁，无需类包装
2. **灵活性**：函数可以独立运行和组织
3. **Pytest 最佳实践**：函数风格是 pytest 推荐的方式
4. **易于维护**：减少不必要的抽象层级

### 测试组织

- 使用描述性的函数名：`test_<功能>_<场景>`
- 使用模块级别的文档字符串说明测试目的
- 相关测试可以放在同一个文件中，通过函数名分组

### 集成测试标记

对于需要网络访问或其他外部资源的测试，使用 `@pytest.mark.integration` 标记：

```python
@pytest.mark.integration
def test_load_swebench_lite_from_huggingface():
    """Test loading SWE-bench Lite dataset from HuggingFace"""
    dataset = load_dataset("SWE-bench/SWE-bench_Lite", split="test")
    assert dataset is not None
```

## TDD 工作流程

### 三阶段开发流程

1. **测试阶段（Red）**：先编写测试，定义期望行为
2. **实现阶段（Green）**：实现最小功能，使测试通过
3. **重构阶段（Refactor）**：优化代码结构、可读性和可维护性

### 测试编写原则

- 每个功能点都要有对应的测试
- 测试应该覆盖正常情况和边界情况
- 测试应该独立，不依赖其他测试的执行顺序
- 使用描述性的测试名称，清晰表达测试意图

## 代码风格

### Python 代码规范

- 遵循 PEP 8 代码风格
- 使用类型提示（Type Hints）
- 添加文档字符串（Docstrings）
- 使用有意义的变量和函数名

### 模块组织

- 每个模块应该有清晰的职责
- 使用 `__init__.py` 定义模块公共接口
- 相关功能组织在同一个包中

## 依赖管理

### 使用 uv 管理依赖

- 所有依赖通过 `uv add` 添加到 `pyproject.toml`
- 开发依赖使用 `uv add --dev`
- 运行 `uv sync` 同步环境
- `uv.lock` 文件应该提交到版本控制

### 依赖分类

- **核心依赖**：项目运行必需的依赖
- **开发依赖**：测试、代码质量工具等
- **可选依赖**：特定功能需要的依赖（如 Docker 用于评估）

## 文件命名规范

### 测试文件

- 测试文件以 `test_` 开头
- 测试函数以 `test_` 开头
- 集成测试文件使用 `test_<module>_integration.py` 命名

### 模块文件

- 使用小写字母和下划线
- 模块名应该清晰表达功能

## Git 提交规范

### 提交信息格式

```
<type>: <subject>

<body>
```

类型（type）：
- `feat`: 新功能
- `fix`: 修复 bug
- `test`: 添加或修改测试
- `refactor`: 重构代码
- `docs`: 文档更新
- `chore`: 构建/工具相关

## 文档规范

### README 更新

- 新功能添加后更新 README
- 包含使用示例
- 说明依赖和安装步骤

### 代码注释

- 复杂逻辑添加注释说明
- 使用文档字符串说明函数/类用途
- 参数和返回值要有类型提示

## 错误处理

### 异常处理原则

- 使用具体的异常类型
- 提供有意义的错误消息
- 记录错误日志便于调试
- 优雅降级，避免程序崩溃

## 性能考虑

### 优化原则

- 先保证功能正确，再考虑性能
- 使用适当的算法和数据结构
- 避免过早优化
- 对关键路径进行性能测试

## 安全考虑

### API 密钥管理

- 使用环境变量存储敏感信息
- 不要将密钥提交到版本控制
- 在 `.gitignore` 中排除配置文件

## 持续改进

### 代码审查

- 定期审查代码质量
- 重构重复代码
- 提取公共功能
- 保持代码简洁

---

**最后更新**：2025-01-14  
**版本**：v5
