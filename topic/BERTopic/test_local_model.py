#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试本地嵌入模型
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


def test_local_model_direct():
    """直接测试本地模型路径"""
    logger.info("=== 直接测试本地模型路径 ===")
    
    # 直接指定本地模型路径
    local_model_path = r"C:\Users\1\.cache\huggingface\hub\models--sentence-transformers--all-MiniLM-L6-v2\snapshots\86741b4e3f5cb7765a600d3a3d55a0f6a6cb443d"
    
    # 检查路径是否存在
    if os.path.exists(local_model_path):
        logger.info(f"本地模型路径存在: {local_model_path}")
        
        # 创建聚类器（使用本地模型）
        clusterer = BERTopicClustering(
            embedding_model="all-MiniLM-L6-v2",
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
        ] * 3  # 少量数据用于快速测试
        
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
    else:
        logger.error(f"❌ 本地模型路径不存在: {local_model_path}")
        
        # 尝试查找正确的快照目录
        base_path = Path(r"C:\Users\1\.cache\huggingface\hub\models--sentence-transformers--all-MiniLM-L6-v2")
        if base_path.exists():
            logger.info("查找可用的快照目录...")
            snapshots_dir = base_path / "snapshots"
            if snapshots_dir.exists():
                for item in snapshots_dir.iterdir():
                    if item.is_dir():
                        logger.info(f"找到快照目录: {item}")
                        
                        # 检查是否有必要的模型文件
                        model_files = ["config.json", "pytorch_model.bin", "tokenizer.json"]
                        has_files = all((item / f).exists() for f in model_files)
                        
                        if has_files:
                            logger.info(f"✅ 完整的模型文件存在于: {item}")
                            return test_with_snapshot(str(item))
            
            # 如果没有snapshots目录，尝试直接使用blobs
            blobs_dir = base_path / "blobs"
            if blobs_dir.exists():
                logger.info(f"找到blobs目录: {blobs_dir}")
        
        return False


def test_with_snapshot(snapshot_path: str):
    """使用快照路径测试"""
    logger.info(f"使用快照路径测试: {snapshot_path}")
    
    # 创建聚类器（使用本地模型）
    clusterer = BERTopicClustering(
        embedding_model="all-MiniLM-L6-v2",
        local_model_path=snapshot_path,
        min_topic_size=2,
        nr_topics=3,
        verbose=True
    )
    
    # 创建示例数据
    example_texts = [
        "今天天气真好",
        "机器学习很重要",
        "深度学习很强大",
    ]
    
    # 设置数据
    clusterer.docs = example_texts
    clusterer.original_docs = example_texts
    
    # 训练模型
    if clusterer.train_model():
        logger.info("✅ 使用快照路径训练成功！")
        return True
    else:
        logger.error("❌ 使用快照路径训练失败")
        return False


def test_online_model():
    """测试在线模型作为对比"""
    logger.info("=== 测试在线模型作为对比 ===")
    
    # 创建聚类器（使用在线模型）
    clusterer = BERTopicClustering(
        embedding_model="all-MiniLM-L6-v2",
        local_model_path=None,  # 不使用本地模型
        min_topic_size=2,
        nr_topics=3,
        verbose=True
    )
    
    # 创建示例数据
    example_texts = [
        "今天天气真好",
        "机器学习很重要",
        "深度学习很强大",
    ]
    
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


if __name__ == "__main__":
    print("BERTopic本地嵌入模型测试")
    print("=" * 50)
    
    # 测试本地模型
    local_success = test_local_model_direct()
    
    print("\n" + "=" * 50)
    
    # 测试在线模型作为对比
    online_success = test_online_model()
    
    print("\n" + "=" * 50)
    print("测试结果总结:")
    print(f"本地模型测试: {'✅ 成功' if local_success else '❌ 失败'}")
    print(f"在线模型测试: {'✅ 成功' if online_success else '❌ 失败'}")