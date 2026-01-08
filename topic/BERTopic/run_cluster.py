import logging
from models.weibo_blog import WeiboBlog
from orm.client import ORM
from sqlalchemy.sql import func

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 直接导入
from bertopic_clustering import BERTopicClustering, run_clustering_pipeline


def demo_with_sample_data():
    """使用示例数据进行演示"""
    logger.info("=== 使用示例数据进行演示 ===")
    with ORM() as db:
        # tmp = db.query(WeiboBlog.text).filter(WeiboBlog.text != "").limit(100).all()
        tmp = db.query(WeiboBlog.text).order_by(func.random()).limit(50).all()
        example_texts = [text[0] for text in tmp]
        print(example_texts)

    # 创建聚类器 - 移除nr_topics参数，让模型自动确定主题数量
    clusterer = BERTopicClustering(
        min_topic_size=3,
        # nr_topics=5,  # 暂时移除这个参数，避免主题数量冲突
        verbose=True,
        # embedding_model="all-MiniLM-L12-v2"
        # embedding_model="BAAI/bge-small-zh-v1.5"
        embedding_model="moka-ai/m3e-base"
        # embedding_model="BAAI/bge-base-zh-v1.5"
    )

    # all - MiniLM - L6 - v2
    # all - MiniLM - L12 - v2
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
        clusterer.save_results("demo_results")

        logger.info("演示完成，结果已保存到 demo_results 目录")
    else:
        logger.error("模型训练失败")


if __name__ == "__main__":
    print("BERTopic聚类运行脚本")
    demo_with_sample_data()