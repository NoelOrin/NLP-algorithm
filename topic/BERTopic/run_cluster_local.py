#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BERTopic聚类脚本 - 使用本地嵌入模型版本
"""

import os
import sys
import logging
from typing import Optional
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 导入聚类器
from bertopic_clustering import BERTopicClustering, run_clustering_pipeline


def get_local_model_path(model_name: str) -> Optional[str]:
    """获取本地模型路径"""
    # 常见的本地模型缓存路径
    cache_paths = [
        # HuggingFace缓存路径
        Path.home() / ".cache" / "huggingface" / "hub",
        # SentenceTransformers默认缓存路径
        Path.home() / ".cache" / "torch" / "sentence_transformers",
        # 项目本地模型目录
        project_root / "models" / "sentence_transformers",
    ]
    
    # 模型名称到目录名的映射
    model_mapping = {
        "all-MiniLM-L6-v2": "models--sentence-transformers--all-MiniLM-L6-v2",
        "paraphrase-multilingual-MiniLM-L12-v2": "models--sentence-transformers--paraphrase-multilingual-MiniLM-L12-v2",
    }
    
    model_dir_name = model_mapping.get(model_name)
    if not model_dir_name:
        return None
    
    for cache_path in cache_paths:
        model_path = cache_path / model_dir_name
        if model_path.exists():
            logger.info(f"找到本地模型: {model_path}")
            return str(model_path)
    
    return None


def demo_with_local_model():
    """使用本地模型进行演示"""
    logger.info("=== 使用本地嵌入模型进行演示 ===")
    
    # 尝试获取本地模型路径
    model_name = "all-MiniLM-L6-v2"
    local_model_path = get_local_model_path(model_name)
    
    if not local_model_path:
        logger.warning(f"未找到 {model_name} 的本地模型，将使用在线模型")
        local_model_path = None
    
    # 创建聚类器（使用本地模型）
    clusterer = BERTopicClustering(
        embedding_model=model_name,
        local_model_path=local_model_path,
        min_topic_size=3,
        nr_topics=5,
        verbose=True
    )
    
    # 创建示例数据
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
        "注意力机制让模型能够关注重要信息",
        "今天天气真好适合出去散步",
        "明天可能会下雨记得带伞",
        "周末计划去公园野餐",
        "最近在学习新的编程语言",
        "数据分析和可视化很重要",
        "人工智能技术正在快速发展",
        "深度学习在医疗影像分析中应用广泛",
        "自然语言处理帮助机器理解人类语言",
        "计算机视觉技术让机器能够看懂世界",
        "推荐系统根据用户兴趣提供个性化内容"
    ] * 5  # 重复创建更多数据
    
    # 设置数据
    clusterer.docs = example_texts
    clusterer.original_docs = example_texts
    
    # 训练模型
    if clusterer.train_model():
        # 查看主题信息
        topic_info = clusterer.get_topic_info()
        if topic_info is not None:
            print("\n=== 主题信息 ===")
            print(topic_info)
        
        # 查看主题分布
        distribution = clusterer.analyze_topic_distribution()
        if distribution:
            print("\n=== 主题分布 ===")
            print(f"总文档数: {distribution['total_documents']}")
            print(f"有效主题数: {distribution['total_topics']}")
            print(f"噪声文档比例: {distribution['noise_ratio']:.2%}")
            print(f"平均主题大小: {distribution['avg_topic_size']:.1f}")
        
        # 查看每个主题的关键词
        valid_topics = [topic for topic in set(clusterer.topics) if topic != -1]
        for topic_id in valid_topics:
            topic_words = clusterer.get_topic_words(topic_id)
            if topic_words:
                print(f"\n=== 主题 {topic_id} 的关键词 ===")
                for word, score in topic_words[:8]:
                    print(f"  {word}: {score:.4f}")
        
        # 保存结果
        clusterer.save_results("local_model_results")
        
        logger.info("演示完成，结果已保存到 local_model_results 目录")
    else:
        logger.error("模型训练失败")


def run_with_real_data_local():
    """使用真实数据运行聚类（本地模型版本）"""
    logger.info("=== 使用真实数据运行聚类（本地模型） ===")
    
    # 尝试获取本地模型路径
    model_name = "all-MiniLM-L6-v2"
    local_model_path = get_local_model_path(model_name)
    
    if not local_model_path:
        logger.warning(f"未找到 {model_name} 的本地模型，将使用在线模型")
        local_model_path = None
    
    # 数据库连接信息
    from orm.client import get_db
    
    try:
        db = get_db()
        cursor = db.cursor()
        
        # 查询微博数据
        sql = "SELECT text FROM weibo_blog LIMIT 100"
        cursor.execute(sql)
        tmp = cursor.fetchall()
        
        if not tmp:
            logger.error("未查询到数据")
            return
        
        # 提取文本
        texts = [text[0] for text in tmp]
        logger.info(f"成功加载 {len(texts)} 条微博数据")
        
        # 创建聚类器（使用本地模型）
        clusterer = BERTopicClustering(
            embedding_model=model_name,
            local_model_path=local_model_path,
            min_topic_size=5,
            nr_topics=10,
            verbose=True
        )
        
        # 设置数据
        clusterer.docs = texts
        clusterer.original_docs = texts
        
        # 训练模型
        if clusterer.train_model():
            # 查看主题信息
            topic_info = clusterer.get_topic_info()
            if topic_info is not None:
                print("\n=== 主题信息 ===")
                print(topic_info)
            
            # 查看主题分布
            distribution = clusterer.analyze_topic_distribution()
            if distribution:
                print("\n=== 主题分布 ===")
                print(f"总文档数: {distribution['total_documents']}")
                print(f"有效主题数: {distribution['total_topics']}")
                print(f"噪声文档比例: {distribution['noise_ratio']:.2%}")
                print(f"平均主题大小: {distribution['avg_topic_size']:.1f}")
            
            # 保存结果
            clusterer.save_results("real_data_local_results")
            
            logger.info("真实数据聚类完成，结果已保存到 real_data_local_results 目录")
        else:
            logger.error("模型训练失败")
            
    except Exception as e:
        logger.error(f"数据库操作失败: {e}")


if __name__ == "__main__":
    print("BERTopic聚类脚本 - 本地嵌入模型版本")
    print("=" * 50)
    
    # 演示使用本地模型
    demo_with_local_model()
    
    print("\n" + "=" * 50)
    
    # 尝试使用真实数据
    try:
        run_with_real_data_local()
    except Exception as e:
        logger.warning(f"真实数据运行失败: {e}")
        print("真实数据运行失败，但示例数据演示已完成")