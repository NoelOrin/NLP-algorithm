# BERTopic 主题聚类系统

基于BERTopic的中文文本主题聚类系统，专门为中文微博、新闻等文本数据设计。

## 功能特性

- ✅ **中文文本预处理**：自动清洗、分词、去停用词
- ✅ **BERT嵌入表示**：使用多语言BERT模型获取高质量文本嵌入
- ✅ **主题聚类**：基于HDBSCAN的密度聚类算法
- ✅ **主题建模**：使用c-TF-IDF提取主题关键词
- ✅ **丰富可视化**：主题分布图、词云、相似度热力图等
- ✅ **交互式仪表板**：Plotly交互式可视化
- ✅ **批量处理**：支持多文件批量处理
- ✅ **参数调优**：提供多种参数组合比较

## 系统架构

```
BERTopic/
├── bertopic_clustering.py    # 核心聚类功能
├── data_preprocessor.py      # 数据预处理
├── visualization.py          # 可视化功能
├── example_usage.py          # 示例用法
├── test_basic.py            # 基本功能测试
└── README.md                # 说明文档
```

## 安装依赖

```bash
# 使用pip安装
pip install bertopic sentence-transformers umap-learn hdbscan wordcloud plotly

# 或使用uv（推荐）
uv add bertopic sentence-transformers umap-learn hdbscan wordcloud plotly
```

## 快速开始

### 1. 基础用法

```python
from bertopic_clustering import BERTopicClustering

# 创建聚类器
clusterer = BERTopicClustering(
    embedding_model="paraphrase-multilingual-MiniLM-L12-v2",
    language="chinese",
    min_topic_size=5
)

# 加载数据
clusterer.load_data("data.csv", text_column='微博正文', sample_size=1000)

# 训练模型
clusterer.train_model()

# 查看主题信息
topic_info = clusterer.get_topic_info()
print(topic_info)

# 可视化
clusterer.visualize_topics(save_path="results")

# 保存结果
clusterer.save_results("bertopic_results")
```

### 2. 完整流程

```python
import pandas as pd
from bertopic_clustering import BERTopicClustering
from data_preprocessor import ChineseTextPreprocessor
from visualization import BERTopicVisualizer

# 1. 数据预处理
preprocessor = ChineseTextPreprocessor()
df = pd.read_csv("data.csv")
processed_df = preprocessor.preprocess_dataframe(df, '微博正文')

# 2. 主题聚类
clusterer = BERTopicClustering()
clusterer.docs = processed_df['processed_text'].tolist()
clusterer.train_model()

# 3. 可视化分析
visualizer = BERTopicVisualizer(
    clusterer.model, 
    clusterer.docs, 
    clusterer.topics
)
visualizer.generate_comprehensive_report("full_analysis")
```

### 3. 批处理示例

```python
from example_usage import batch_processing_example

# 处理多个数据文件
batch_processing_example()
```

## 数据格式要求

### 输入数据格式

支持CSV和Excel格式，需要包含文本列：

```csv
id,微博正文,发布时间,用户昵称
1,"今天天气真好，适合出去散步",2025-01-01,用户A
2,"机器学习是人工智能的重要分支",2025-01-01,用户B
```

### 输出数据格式

1. **主题分配文件** (`*_with_topics.csv`)
   - 包含原始数据+主题分配+概率

2. **主题信息文件** (`*_topic_info.csv`)
   - 每个主题的统计信息

3. **可视化图表**
   - 主题分布图、词云、热力图等

## 参数说明

### BERTopicClustering 参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `embedding_model` | str | "paraphrase-multilingual-MiniLM-L12-v2" | 嵌入模型 |
| `language` | str | "chinese" | 语言设置 |
| `min_topic_size` | int | 10 | 最小主题大小 |
| `nr_topics` | int/str | "auto" | 主题数量 |

### 数据预处理参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `custom_dict_path` | str | None | 自定义词典路径 |
| `stop_words_path` | str | None | 停用词表路径 |
| `min_word_length` | int | 1 | 最小词长 |

## 可视化功能

### 1. 主题分布图
显示每个主题包含的文档数量分布。

### 2. 主题词云
为每个主题生成关键词词云。

### 3. 主题相似度热力图
显示主题之间的相似度关系。

### 4. 文档嵌入降维图
使用UMAP/t-SNE将高维嵌入降维到2D可视化。

### 5. 交互式仪表板
Plotly生成的交互式分析面板。

## 示例数据

系统包含示例用法，可以直接运行：

```bash
cd topic/BERTopic
python example_usage.py
```

## 测试系统

运行基本功能测试：

```bash
python test_basic.py
```

## 常见问题

### Q: 如何解决内存不足问题？
A: 使用`sample_size`参数限制处理的数据量。

### Q: 主题数量太多/太少怎么办？
A: 调整`min_topic_size`和`nr_topics`参数。

### Q: 如何处理特定领域的文本？
A: 使用`custom_dict_path`加载领域词典。

### Q: 如何提高聚类质量？
A: 尝试不同的`embedding_model`和预处理参数。

## 性能优化建议

1. **数据量控制**：对于大规模数据，使用采样或分批处理
2. **模型选择**：根据任务选择合适的嵌入模型
3. **参数调优**：通过实验找到最佳的主题大小参数
4. **硬件加速**：使用GPU加速BERT模型推理

## 输出文件说明

运行完成后会生成以下文件：

- `*_with_topics.csv` - 包含主题分配的完整数据
- `*_topic_info.csv` - 主题统计信息
- `*_model` - 保存的模型文件（文件夹）
- `*_distribution.png` - 主题分布图
- `*_wordclouds.png` - 主题词云网格
- `*_similarity.png` - 相似度热力图
- `*_embeddings.png` - 嵌入降维图
- `*_dashboard.html` - 交互式仪表板

## 扩展功能

系统支持以下扩展功能：

- **自定义预处理**：修改`ChineseTextPreprocessor`类
- **主题演化分析**：需要时间戳数据
- **多语言支持**：修改`language`参数
- **自定义可视化**：扩展`BERTopicVisualizer`类

## 技术细节

### 算法流程

1. **文本预处理**：清洗、分词、去停用词
2. **BERT嵌入**：使用Sentence-BERT获取文本向量
3. **降维处理**：UMAP降低维度
4. **密度聚类**：HDBSCAN识别主题
5. **主题建模**：c-TF-IDF提取关键词

### 模型选择

- **嵌入模型**：paraphrase-multilingual-MiniLM-L12-v2（推荐中文）
- **聚类算法**：HDBSCAN（密度聚类）
- **降维算法**：UMAP（保持局部结构）

## 贡献指南

欢迎提交Issue和Pull Request来改进系统。

## 许可证

本项目基于MIT许可证开源。

## 联系方式

如有问题请提交Issue或联系开发者。