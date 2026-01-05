#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单本地模型测试
"""

import os
import sys
import logging
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 导入聚类器
from bertopic_clustering import BERTopicClustering


def test_simple_local_model():
    """简单测试本地模型"""
    logger.info("=== 简单测试本地模型 ===")
    
    # 直接使用本地模型路径
    local_model_path = r"C:\Users\1\.cache\huggingface\hub\models--sentence-transformers--all-MiniLM-L6-v2\snapshots\c9745ed1d9f207416be6d2e6f8de32d1f16199bf"
    
    logger.info(f"尝试使用本地模型路径: {local_model_path}")
    
    # 检查路径是否存在
    if not os.path.exists(local_model_path):
        logger.error("本地模型路径不存在")
        return False
    
    # 检查模型文件
    required_files = ["config.json", "pytorch_model.bin", "tokenizer.json", "vocab.txt"]
    missing_files = []
    
    for file in required_files:
        file_path = os.path.join(local_model_path, file)
        if os.path.exists(file_path):
            logger.info(f"✅ 找到模型文件: {file}")
        else:
            logger.warning(f"❌ 缺少模型文件: {file}")
            missing_files.append(file)
    
    if missing_files:
        logger.warning(f"缺少 {len(missing_files)} 个模型文件，可能无法正常加载")
    
    try:
        # 创建聚类器（使用本地模型）
        clusterer = BERTopicClustering(
            embedding_model="all-MiniLM-L6-v2",
            local_model_path=local_model_path,
            min_topic_size=2,
            nr_topics=3,
            verbose=True
        )
        
        if clusterer.model is None:
            logger.error("模型初始化失败")
            return False
        
        logger.info("✅ 本地模型初始化成功！")
        
        # 创建示例数据（需要足够的数据量）
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
        ] * 2  # 20条数据
        
        # 设置数据
        clusterer.docs = example_texts
        clusterer.original_docs = example_texts
        
        # 训练模型
        if clusterer.train_model():
            logger.info("✅ 使用本地模型训练成功！")
            
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
            
            return True
        else:
            logger.error("❌ 使用本地模型训练失败")
            return False
            
    except Exception as e:
        logger.error(f"❌ 发生错误: {e}")
        return False


def test_online_model_comparison():
    """测试在线模型作为对比"""
    logger.info("=== 测试在线模型作为对比 ===")
    
    try:
        # 创建聚类器（使用在线模型）
        clusterer = BERTopicClustering(
            embedding_model="all-MiniLM-L6-v2",
            local_model_path=None,  # 不使用本地模型
            min_topic_size=2,
            nr_topics=3,
            verbose=True
        )
        
        if clusterer.model is None:
            logger.error("在线模型初始化失败")
            return False
        
        logger.info("✅ 在线模型初始化成功！")
        
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
        ] * 2  # 20条数据
        
        # 设置数据
        clusterer.docs = example_texts
        clusterer.original_docs = example_texts
        
        # 训练模型
        if clusterer.train_model():
            logger.info("✅ 在线模型训练成功！")
            return True
        else:
            logger.error("❌ 在线模型训练失败")
            return False
            
    except Exception as e:
        logger.error(f"❌ 发生错误: {e}")
        return False


if __name__ == "__main__":
    print("BERTopic本地嵌入模型简单测试")
    print("=" * 50)
    
    # 测试本地模型
    local_success = test_simple_local_model()
    
    print("\n" + "=" * 50)
    
    # 测试在线模型作为对比
    online_success = test_online_model_comparison()
    
    print("\n" + "=" * 50)
    print("测试结果总结:")
    print(f"本地模型测试: {'✅ 成功' if local_success else '❌ 失败'}")
    print(f"在线模型测试: {'✅ 成功' if online_success else '❌ 失败'}")
    
    if local_success:
        print("\n🎉 本地嵌入模型已成功配置并可以使用！")
    else:
        print("\n⚠️ 本地模型配置需要进一步调整")