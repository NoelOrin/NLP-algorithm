"""
BERTopic主题聚类示例用法

这个文件展示了如何使用BERTopic进行中文文本的主题聚类分析
"""

import warnings
import logging
import pandas as pd
import os
import sys

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(__file__))

# 抑制警告
warnings.filterwarnings("ignore")

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

from bertopic_clustering import BERTopicClustering
from data_preprocessor import ChineseTextPreprocessor, preprocess_pipeline
from visualization import BERTopicVisualizer


def basic_example():
    """基础示例：快速开始BERTopic聚类"""
    logger.info("=== 基础示例开始 ===")
    
    # 1. 创建聚类器
    clusterer = BERTopicClustering(
        embedding_model="paraphrase-multilingual-MiniLM-L12-v2",
        language="chinese",
        min_topic_size=5,
        nr_topics="auto"
    )
    
    # 2. 加载数据
    data_file = "../data/合并数据.csv"
    if os.path.exists(data_file):
        success = clusterer.load_data(data_file, text_column='微博正文', sample_size=500)
        if not success:
            logger.error("数据加载失败")
            return
    else:
        logger.warning(f"数据文件不存在: {data_file}")
        # 使用示例数据
        example_texts = [
            "今天天气真好，适合出去散步",
            "机器学习是人工智能的重要分支",
            "深度学习在图像识别方面表现出色",
            "自然语言处理技术发展迅速",
            "Python是数据科学的首选语言",
            "神经网络模型需要大量数据进行训练",
            "Transformer架构改变了NLP领域",
            "BERT模型在多项任务上取得突破",
            "预训练语言模型成为研究热点",
            "注意力机制让模型能够关注重要信息"
        ] * 50  # 重复创建更多数据
        
        clusterer.docs = example_texts
        clusterer.original_docs = example_texts
        logger.info("使用示例数据进行演示")
    
    # 3. 训练模型
    if clusterer.train_model():
        # 4. 查看主题信息
        topic_info = clusterer.get_topic_info()
        if topic_info is not None:
            print("\n=== 主题信息 ===")
            print(topic_info.head())
        
        # 5. 查看具体主题的关键词
        if len(topic_info) > 1:
            topic_id = topic_info[topic_info['Topic'] != -1].iloc[0]['Topic']
            topic_words = clusterer.get_topic_words(topic_id)
            if topic_words:
                print(f"\n=== 主题 {topic_id} 的关键词 ===")
                for word, score in topic_words[:10]:
                    print(f"{word}: {score:.4f}")
        
        # 6. 保存结果
        clusterer.save_results("basic_example_results")
        
        logger.info("基础示例完成")


def advanced_example():
    """高级示例：完整的预处理和可视化流程"""
    logger.info("\n=== 高级示例开始 ===")
    
    # 1. 数据预处理
    data_file = "../data/合并数据.csv"
    if os.path.exists(data_file):
        logger.info("开始数据预处理...")
        
        preprocessor = ChineseTextPreprocessor()
        
        # 加载原始数据
        df = pd.read_csv(data_file, encoding='utf-8')
        
        # 预处理数据
        processed_df = preprocessor.preprocess_dataframe(
            df, 
            text_column='微博正文', 
            sample_size=1000
        )
        
        # 分析文本长度
        stats = preprocessor.analyze_text_length(processed_df['processed_text'].tolist())
        logger.info(f"文本长度统计: {stats}")
        
        # 保存预处理数据
        preprocessor.save_preprocessed_data(processed_df, "preprocessed_weibo_data")
        
        # 使用预处理后的数据
        docs = processed_df['processed_text'].tolist()
        original_docs = processed_df['微博正文'].tolist()
    else:
        logger.warning("数据文件不存在，使用示例数据")
        # 创建示例数据
        docs = [
            "机器学习 人工智能 重要 分支",
            "深度学习 图像 识别 表现 出色", 
            "自然语言 处理 技术 发展 迅速",
            "Python 数据 科学 首选 语言",
            "神经网络 模型 需要 大量 数据 训练",
            "Transformer 架构 改变 NLP 领域",
            "BERT 模型 多项 任务 取得 突破",
            "预训练 语言 模型 成为 研究 热点",
            "注意力 机制 模型 能够 关注 重要 信息"
        ] * 100
        original_docs = docs
    
    # 2. 创建聚类器（使用更精细的参数）
    clusterer = BERTopicClustering(
        embedding_model="paraphrase-multilingual-MiniLM-L12-v2",
        language="chinese",
        min_topic_size=3,
        nr_topics=10  # 限制主题数量
    )
    
    clusterer.docs = docs
    clusterer.original_docs = original_docs
    
    # 3. 训练模型
    if clusterer.train_model():
        # 4. 创建可视化器
        visualizer = BERTopicVisualizer(
            clusterer.model, 
            clusterer.docs, 
            clusterer.topics, 
            clusterer.probabilities
        )
        
        # 5. 生成综合报告
        visualizer.generate_comprehensive_report("advanced_example_report")
        
        # 6. 交互式可视化
        visualizer.create_interactive_dashboard(save_path="advanced_dashboard.html")
        
        logger.info("高级示例完成")


def batch_processing_example():
    """批处理示例：处理多个数据文件"""
    logger.info("\n=== 批处理示例开始 ===")
    
    # 定义要处理的数据文件
    data_files = [
        "../data/事件.csv",
        "../data/新闻.csv", 
        "../data/舆论.csv"
    ]
    
    results = []
    
    for data_file in data_files:
        if os.path.exists(data_file):
            logger.info(f"处理文件: {data_file}")
            
            # 为每个文件创建单独的聚类器
            clusterer = BERTopicClustering(
                embedding_model="paraphrase-multilingual-MiniLM-L12-v2",
                language="chinese",
                min_topic_size=5
            )
            
            # 加载数据
            if clusterer.load_data(data_file, text_column='微博正文', sample_size=300):
                # 训练模型
                if clusterer.train_model():
                    # 获取主题信息
                    topic_info = clusterer.get_topic_info()
                    if topic_info is not None:
                        # 记录结果
                        file_name = os.path.basename(data_file)
                        results.append({
                            'file': file_name,
                            'total_docs': len(clusterer.docs),
                            'num_topics': len(topic_info[topic_info['Topic'] != -1]),
                            'noise_docs': topic_info[topic_info['Topic'] == -1]['Count'].iloc[0] if -1 in topic_info['Topic'].values else 0
                        })
                        
                        # 保存每个文件的结果
                        clusterer.save_results(f"batch_result_{file_name.replace('.csv', '')}")
        else:
            logger.warning(f"文件不存在: {data_file}")
    
    # 汇总结果
    if results:
        summary_df = pd.DataFrame(results)
        print("\n=== 批处理结果汇总 ===")
        print(summary_df)
        summary_df.to_csv("batch_processing_summary.csv", index=False, encoding='utf-8-sig')
    
    logger.info("批处理示例完成")


def parameter_tuning_example():
    """参数调优示例：比较不同参数的效果"""
    logger.info("\n=== 参数调优示例开始 ===")
    
    # 定义不同的参数组合
    param_combinations = [
        {'min_topic_size': 5, 'nr_topics': 'auto', 'name': '默认参数'},
        {'min_topic_size': 3, 'nr_topics': 'auto', 'name': '小主题'},
        {'min_topic_size': 10, 'nr_topics': 'auto', 'name': '大主题'},
        {'min_topic_size': 5, 'nr_topics': 5, 'name': '固定5主题'},
        {'min_topic_size': 5, 'nr_topics': 10, 'name': '固定10主题'}
    ]
    
    comparison_results = []
    
    # 使用示例数据
    example_texts = [
        "机器学习 人工智能 重要 分支",
        "深度学习 图像 识别 表现 出色", 
        "自然语言 处理 技术 发展 迅速",
        "Python 数据 科学 首选 语言",
        "神经网络 模型 需要 大量 数据 训练",
        "Transformer 架构 改变 NLP 领域",
        "BERT 模型 多项 任务 取得 突破",
        "预训练 语言 模型 成为 研究 热点",
        "注意力 机制 模型 能够 关注 重要 信息"
    ] * 50
    
    for params in param_combinations:
        logger.info(f"测试参数组合: {params['name']}")
        
        try:
            clusterer = BERTopicClustering(
                embedding_model="paraphrase-multilingual-MiniLM-L12-v2",
                language="chinese",
                min_topic_size=params['min_topic_size'],
                nr_topics=params['nr_topics']
            )
            
            clusterer.docs = example_texts
            clusterer.original_docs = example_texts
            
            if clusterer.train_model():
                topic_info = clusterer.get_topic_info()
                if topic_info is not None:
                    valid_topics = topic_info[topic_info['Topic'] != -1]
                    
                    comparison_results.append({
                        '参数组合': params['name'],
                        '最小主题大小': params['min_topic_size'],
                        '主题数量策略': params['nr_topics'],
                        '发现主题数': len(valid_topics),
                        '总文档数': len(example_texts),
                        '噪声文档数': topic_info[topic_info['Topic'] == -1]['Count'].iloc[0] if -1 in topic_info['Topic'].values else 0,
                        '平均主题大小': valid_topics['Count'].mean() if len(valid_topics) > 0 else 0
                    })
        except Exception as e:
            logger.error(f"参数组合 {params['name']} 测试失败: {str(e)}")
    
    # 输出比较结果
    if comparison_results:
        comparison_df = pd.DataFrame(comparison_results)
        print("\n=== 参数调优比较结果 ===")
        print(comparison_df)
        comparison_df.to_csv("parameter_tuning_comparison.csv", index=False, encoding='utf-8-sig')
    
    logger.info("参数调优示例完成")


def main():
    """主函数：运行所有示例"""
    logger.info("BERTopic主题聚类示例开始")
    
    # 运行基础示例
    basic_example()
    
    # 运行高级示例
    advanced_example()
    
    # 运行批处理示例（如果数据文件存在）
    if any(os.path.exists(f"../data/{file}") for file in ["事件.csv", "新闻.csv", "舆论.csv"]):
        batch_processing_example()
    
    # 运行参数调优示例
    parameter_tuning_example()
    
    logger.info("所有示例运行完成")
    
    # 使用说明
    print("\n" + "="*50)
    print("BERTopic主题聚类系统使用说明")
    print("="*50)
    print("\n主要功能模块:")
    print("1. bertopic_clustering.py - 核心聚类功能")
    print("2. data_preprocessor.py - 数据预处理")
    print("3. visualization.py - 可视化功能")
    print("4. example_usage.py - 示例用法")
    
    print("\n快速开始:")
    print("from bertopic_clustering import BERTopicClustering")
    print("clusterer = BERTopicClustering()")
    print("clusterer.load_data('your_data.csv', text_column='text')")
    print("clusterer.train_model()")
    print("clusterer.visualize_topics()")
    
    print("\n生成的文件:")
    print("- *_with_topics.csv - 包含主题分配的完整数据")
    print("- *_topic_info.csv - 主题统计信息")
    print("- *_model - 保存的模型文件")
    print("- 各种可视化图表和报告")


if __name__ == "__main__":
    main()