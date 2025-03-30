# 大模型评测框架

一个简单、易用的大模型评测框架，用于评估各种大语言模型的性能。

## 功能特点

- 支持多种模型类型（HuggingFace、OpenAI等）
- 可扩展的数据集和评估指标
- 灵活的配置方式
- 支持本地模型和在线模型
- 离线评测模式
- 用户友好的API接口
- 命令行工具支持

## 安装

```bash
# 克隆仓库
git clone https://github.com/yourusername/model_evaluate_demo.git
cd model_evaluate_demo

# 安装依赖
pip install -r requirements.txt
```

## 快速开始

### 命令行使用

```bash
# 列出所有可用的数据集
python ../run_model_evaluate.py --list-datasets

# 列出所有可用的评估指标
python ../run_model_evaluate.py --list-metrics

# 列出所有可用的模型类型
python ../run_model_evaluate.py --list-model-types

# 评测本地模型
python ../run_model_evaluate.py --model-path /path/to/your/model --dataset math --max-samples 5
```

### API使用

```python
from model_evaluate_demo.api import evaluate_model

# 评测本地模型
results = evaluate_model(
    model_path="/path/to/your/model",
    model_type="huggingface",
    dataset_name="math",
    metrics=["accuracy"],
    max_samples=100,
    output_dir="./outputs",
    batch_size=4,
    prompt_template="Solve this math problem:\n{question}\n\nThe answer is:",
    generation_kwargs={
        "temperature": 0.0,
        "max_new_tokens": 256,
        "do_sample": False
    },
    device="cuda",
    offline=True,
    debug=True
)

print(results)
```

## 参数说明

### 命令行参数

```
--model-path: 模型文件夹路径（必需）
--model-type: 模型类型，默认为"huggingface"
--dataset: 数据集名称，默认为"math"
--metrics: 评估指标列表，默认为["accuracy"]
--max-samples: 最大评估样本数，默认评估全部样本
--output-dir: 结果输出目录，默认为"./outputs"
--batch-size: 推理时的批处理大小，默认为1
--prompt-template: 提示模板，默认使用数据集默认模板
--device: 使用设备，默认为"cuda"
--offline: 启用离线模式（不下载文件）
--debug: 启用调试模式
--no-trust-remote-code: 不信任模型代码
--load-in-8bit: 使用8位量化
--load-in-4bit: 使用4位量化
--temperature: 生成温度，默认为0.0
--max-new-tokens: 最大生成token数，默认为256
--do-sample: 启用采样生成
```

### API参数

```python
evaluate_model(
    model_path: str,                  # 模型文件夹路径
    model_type: str = "huggingface",  # 模型类型
    dataset_name: str = "math",       # 数据集名称
    metrics: list = ["accuracy"],     # 评估指标列表
    max_samples: int = None,          # 最大评估样本数
    output_dir: str = "./outputs",    # 结果输出目录
    batch_size: int = 1,              # 推理时的批处理大小
    prompt_template: str = None,      # 提示模板
    generation_kwargs: dict = None,   # 生成参数
    device: str = "cuda",             # 使用设备
    offline: bool = True,             # 是否使用离线模式
    debug: bool = False,              # 是否开启调试模式
    trust_remote_code: bool = True,   # 是否信任模型代码
    load_in_8bit: bool = False,       # 是否使用8位量化
    load_in_4bit: bool = False        # 是否使用4位量化
)
```

## 支持的数据集

- math: 数学问题数据集
- ...（可根据需求扩展）

## 支持的评估指标

- accuracy: 准确率
- ...（可根据需求扩展）

## 支持的模型类型

- huggingface: HuggingFace模型
- openai: OpenAI API模型
- ...（可根据需求扩展）

## 自定义扩展

### 添加新的数据集

1. 在`datasets`目录中创建新的数据集类
2. 继承`BaseDataset`类并实现必要的方法
3. 使用`@DATASETS.register`装饰器注册数据集

### 添加新的评估指标

1. 在`metrics`目录中创建新的评估指标类
2. 继承`BaseMetric`类并实现必要的方法
3. 使用`@METRICS.register`装饰器注册评估指标

### 添加新的模型类型

1. 在`models`目录中创建新的模型类
2. 继承`BaseModel`类并实现必要的方法
3. 使用`@MODELS.register`装饰器注册模型类型

## 示例

### 评测本地HuggingFace模型

```python
from model_evaluate_demo.api import evaluate_model

results = evaluate_model(
    model_path="/path/to/your/model",
    model_type="huggingface",
    dataset_name="math",
    metrics=["accuracy"],
    max_samples=100,
    offline=True
)
```

### 评测OpenAI模型

```python
from model_evaluate_demo.api import evaluate_model

results = evaluate_model(
    model_path="gpt-3.5-turbo",
    model_type="openai",
    dataset_name="math",
    metrics=["accuracy"],
    max_samples=10,
    generation_kwargs={
        "temperature": 0.1,
        "max_new_tokens": 256
    }
)
```

## 注意事项

1. 在使用本地模型时，确保模型文件夹包含完整的模型文件
2. 在使用HuggingFace模型时，可能需要设置HuggingFace镜像站点：`os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"`
3. 在使用离线模式时，确保已预先下载所需的模型和数据集

## 贡献指南

欢迎贡献代码、报告问题或提出建议！

## 许可证

MIT 许可证# model_evaluate_demo
