import os
import sys
import json
import logging
import numpy as np
from typing import List, Optional, Dict, Tuple, Any
from pathlib import Path

# 检查依赖可用性
try:
    from bertopic import BERTopic
    from sentence_transformers import SentenceTransformer
    from umap import UMAP
    from hdbscan import HDBSCAN
    from sklearn.feature_extraction.text import CountVectorizer
    from bertopic.representation import KeyBERTInspired, MaximalMarginalRelevance
    import jieba
    import jieba.posseg as pseg
    import re
    BERTOPIC_AVAILABLE = True
except ImportError as e:
    BERTOPIC_AVAILABLE = False
    print(f"警告: 缺少依赖包 {e}")

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ChineseTextPreprocessor:
    """中文文本预处理器"""
    
    def __init__(self, stopwords_file: Optional[str] = None, user_dict_file: Optional[str] = None):
        """初始化预处理器"""
        # 默认停用词列表
        self.stopwords = {
            '的', '了', '是', '在', '和', '我', '有', '不', '人', '都', '一', '个', '你', '这', '很', '与', '上',
            '们', '到', '也', '他', '她', '它', '那', '就', '但', '着', '个', '之', '将', '或', '并', '而', '等',
            '其', '已', '无', '没', '非', '经', '为', '对', '把', '被', '让', '使', '以', '于', '由', '向', '及',
            '以及', '以及', '可以', '能够', '应该', '必须', '需要', '想要', '希望', '觉得', '认为', '知道', '看到'
        }
        
        # 加载外部停用词文件
        if stopwords_file:
            self.load_stopwords(stopwords_file)
        
        # 加载用户词典
        if user_dict_file:
            jieba.load_userdict(user_dict_file)
        
        # 配置jieba分词
        jieba.initialize()
    
    def load_stopwords(self, file_path: str):
        """加载停用词文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                words = f.read().splitlines()
                self.stopwords.update(set(words))
            logger.info(f"从 {file_path} 加载了 {len(words)} 个停用词")
        except Exception as e:
            logger.error(f"加载停用词文件失败: {e}")
    
    def clean_text(self, text: str) -> str:
        """清洗文本"""
        if not text or not text.strip():
            return ""
        
        # 去除HTML标签
        text = re.sub(r'<[^>]+>', '', text)
        
        # 去除URL
        text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
        
        # 去除@用户提及
        text = re.sub(r'@[\\w\\u4e00-\\u9fa5]+', '', text)
        
        # 去除话题标签但保留内容
        text = re.sub(r'#[^#]+#', lambda x: x.group()[1:-1], text)
        
        # 去除表情符号
        text = re.sub(r'\\[[^\\]]+\\]', '', text)  # 微博表情格式 [xxx]
        
        # 去除特殊字符和标点符号（保留中文标点）
        text = re.sub(r'[^\\w\\s\\u4e00-\\u9fa5，。！？；：""''《》（）【】]', '', text)
        
        # 去除多余空格
        text = re.sub(r'\\s+', ' ', text).strip()
        
        return text
    
    def segment_text(self, text: str, remove_stopwords: bool = True, use_pos: bool = False) -> str:
        """分词处理"""
        if not text:
            return ""
        
        if use_pos:
            # 使用词性标注分词
            words = pseg.cut(text)
            # 过滤：只保留名词、动词、形容词
            filtered_words = []
            for word, pos in words:
                if pos.startswith(('n', 'v', 'a')) and len(word) > 1:
                    if not remove_stopwords or word not in self.stopwords:
                        filtered_words.append(word)
            result = ' '.join(filtered_words)
        else:
            # 普通分词
            words = jieba.cut(text)
            if remove_stopwords:
                words = [word for word in words if word not in self.stopwords and len(word) > 1]
            result = ' '.join(words)
        
        return result
    
    def preprocess_texts(self, texts: List[str], clean: bool = True, segment: bool = True, 
                        remove_stopwords: bool = True, use_pos: bool = False) -> List[str]:
        """批量预处理文本"""
        processed_texts = []
        
        for i, text in enumerate(texts):
            try:
                processed_text = text
                
                if clean:
                    processed_text = self.clean_text(processed_text)
                
                if segment:
                    processed_text = self.segment_text(processed_text, remove_stopwords, use_pos)
                
                processed_texts.append(processed_text)
                
            except Exception as e:
                logger.warning(f"处理第 {i+1} 个文本时出错: {e}")
                processed_texts.append("")
        
        return processed_texts


class BERTopicClustering:
    """BERTopic主题聚类器"""
    
    def __init__(self, 
                 embedding_model: str = "paraphrase-multilingual-MiniLM-L12-v2",
                 language: str = "chinese",
                 min_topic_size: int = 10,
                 nr_topics: Optional[int] = None,
                 verbose: bool = False):
        """初始化聚类器"""
        self.embedding_model_name = embedding_model
        self.language = language
        self.min_topic_size = min_topic_size
        self.nr_topics = nr_topics
        self.verbose = verbose
        
        # 数据相关属性
        self.docs = []
        self.original_docs = []
        self.df = None
        
        # 模型相关属性
        self.model = None
        self.topics = None
        self.probabilities = None
        
        # 预处理器
        self.preprocessor = ChineseTextPreprocessor()
        
        # 初始化模型
        self._initialize_model()
    
    def _initialize_model(self):
        """初始化BERTopic模型"""
        if not BERTOPIC_AVAILABLE:
            logger.error("BERTopic不可用，请先安装相关依赖")
            return
        
        try:
            # 配置嵌入模型
            embedding_model = SentenceTransformer(self.embedding_model_name)
            
            # 配置UMAP降维
            umap_model = UMAP(
                n_neighbors=15,
                n_components=5,
                min_dist=0.0,
                metric='cosine',
                random_state=42
            )
            
            # 配置HDBSCAN聚类
            hdbscan_model = HDBSCAN(
                min_cluster_size=self.min_topic_size,
                metric='euclidean',
                cluster_selection_method='eom',
                prediction_data=True
            )
            
            # 配置向量化器（针对中文优化）
            vectorizer_model = CountVectorizer(
                stop_words=None,  # 中文停用词在预处理阶段处理
                ngram_range=(1, 1),  # 先使用单字词
                min_df=1,  # 降低最小文档频率
                max_df=1.0  # 允许所有词汇
            )
            
            # 配置主题表示
            representation_model = {
                "KeyBERT": KeyBERTInspired(),
                "MMR": MaximalMarginalRelevance(diversity=0.3)
            }
            
            # 创建BERTopic模型
            self.model = BERTopic(
                embedding_model=embedding_model,
                umap_model=umap_model,
                hdbscan_model=hdbscan_model,
                vectorizer_model=vectorizer_model,
                representation_model=representation_model,
                language=self.language,
                min_topic_size=self.min_topic_size,
                nr_topics=self.nr_topics,
                verbose=self.verbose
            )
            
            logger.info("BERTopic模型初始化完成")
            
        except Exception as e:
            logger.error(f"模型初始化失败: {str(e)}")
            self.model = None
    
    def load_data(self, file_path: str, text_column: str = 'text', sample_size: Optional[int] = None):
        """从文件加载数据"""
        try:
            import pandas as pd
            
            if file_path.endswith('.csv'):
                self.df = pd.read_csv(file_path)
            elif file_path.endswith('.xlsx'):
                self.df = pd.read_excel(file_path)
            else:
                logger.error("不支持的文件格式")
                return False
            
            # 检查文本列是否存在
            if text_column not in self.df.columns:
                logger.error(f"文本列 '{text_column}' 不存在")
                return False
            
            # 处理缺失值
            self.df = self.df.dropna(subset=[text_column])
            
            # 抽样
            if sample_size and len(self.df) > sample_size:
                self.df = self.df.sample(sample_size, random_state=42)
            
            # 提取文本
            self.original_docs = self.df[text_column].tolist()
            
            # 预处理文本
            self.docs = self.preprocessor.preprocess_texts(
                self.original_docs, 
                clean=True, 
                segment=True, 
                remove_stopwords=True
            )
            
            logger.info(f"成功加载 {len(self.docs)} 个文档")
            return True
            
        except Exception as e:
            logger.error(f"数据加载失败: {str(e)}")
            return False
    
    def train_model(self) -> bool:
        """训练聚类模型"""
        if not self.model:
            logger.error("模型未初始化")
            return False
        
        if not self.docs:
            logger.error("没有可用的文档数据")
            return False
        
        try:
            # 过滤空文档
            valid_docs = [doc for doc in self.docs if doc and len(doc.strip()) > 0]
            valid_indices = [i for i, doc in enumerate(self.docs) if doc and len(doc.strip()) > 0]
            
            if len(valid_docs) < self.min_topic_size:
                logger.error(f"有效文档数量({len(valid_docs)})小于最小主题大小({self.min_topic_size})")
                return False
            
            # 训练模型
            self.topics, self.probabilities = self.model.fit_transform(valid_docs)
            
            # 映射回原始索引
            full_topics = [-1] * len(self.docs)
            full_probabilities = [None] * len(self.docs)
            
            for idx, valid_idx in enumerate(valid_indices):
                full_topics[valid_idx] = self.topics[idx]
                if self.probabilities is not None:
                    full_probabilities[valid_idx] = self.probabilities[idx]
            
            self.topics = full_topics
            self.probabilities = full_probabilities
            
            logger.info(f"模型训练完成，发现 {len(set(self.topics)) - 1} 个主题")
            return True
            
        except Exception as e:
            logger.error(f"模型训练失败: {str(e)}")
            return False
    
    def get_topic_info(self):
        """获取主题信息"""
        if not self.model:
            return None
        
        try:
            return self.model.get_topic_info()
        except Exception as e:
            logger.error(f"获取主题信息失败: {str(e)}")
            return None
    
    def get_topic_words(self, topic_id: int, n_words: int = 10):
        """获取指定主题的关键词"""
        if not self.model:
            return None
        
        try:
            return self.model.get_topic(topic_id)[:n_words]
        except Exception as e:
            logger.error(f"获取主题 {topic_id} 的关键词失败: {str(e)}")
            return None
    
    def analyze_topic_distribution(self) -> Dict[str, Any]:
        """分析主题分布"""
        if self.topics is None:
            return {}
        
        try:
            # 统计主题分布
            topic_counts = {}
            for topic in self.topics:
                topic_counts[topic] = topic_counts.get(topic, 0) + 1
            
            # 计算有效主题（排除噪声）
            valid_topics = {k: v for k, v in topic_counts.items() if k != -1}
            noise_count = topic_counts.get(-1, 0)
            
            return {
                'total_documents': len(self.topics),
                'total_topics': len(valid_topics),
                'noise_documents': noise_count,
                'noise_ratio': noise_count / len(self.topics) if len(self.topics) > 0 else 0,
                'topic_sizes': valid_topics,
                'avg_topic_size': np.mean(list(valid_topics.values())) if valid_topics else 0,
                'max_topic_size': max(valid_topics.values()) if valid_topics else 0,
                'min_topic_size': min(valid_topics.values()) if valid_topics else 0
            }
            
        except Exception as e:
            logger.error(f"分析主题分布失败: {str(e)}")
            return {}
    
    def save_results(self, output_dir: str):
        """保存聚类结果"""
        if not self.model:
            logger.error("模型未训练，无法保存结果")
            return
        
        try:
            # 创建输出目录
            os.makedirs(output_dir, exist_ok=True)
            
            # 保存主题信息
            topic_info = self.get_topic_info()
            if topic_info is not None:
                topic_info.to_csv(os.path.join(output_dir, "topic_info.csv"), index=False, encoding='utf-8-sig')
            
            # 保存主题分布分析
            distribution = self.analyze_topic_distribution()
            # 转换numpy类型为Python原生类型
            if 'topic_sizes' in distribution:
                distribution['topic_sizes'] = {int(k): int(v) for k, v in distribution['topic_sizes'].items()}
            with open(os.path.join(output_dir, "topic_distribution.json"), 'w', encoding='utf-8') as f:
                json.dump(distribution, f, ensure_ascii=False, indent=2)
            
            # 保存文档分类结果
            if self.df is not None and len(self.docs) == len(self.df):
                result_df = self.df.copy()
                result_df['processed_text'] = self.docs
                result_df['topic'] = self.topics
                
                if self.probabilities is not None:
                    result_df['topic_probability'] = self.probabilities
                
                result_df.to_csv(os.path.join(output_dir, "document_topics.csv"), 
                                index=False, encoding='utf-8-sig')
            
            # 保存每个主题的关键词
            valid_topics = [topic for topic in set(self.topics) if topic != -1]
            topic_words_dict = {}
            for topic_id in valid_topics:
                words = self.get_topic_words(topic_id, 15)
                if words:
                    topic_words_dict[topic_id] = words
            
            with open(os.path.join(output_dir, "topic_keywords.json"), 'w', encoding='utf-8') as f:
                json.dump(topic_words_dict, f, ensure_ascii=False, indent=2)
            
            logger.info(f"结果已保存到 {output_dir} 目录")
            
        except Exception as e:
            logger.error(f"保存结果失败: {str(e)}")


def run_clustering_pipeline(file_path: str, text_column: str = 'text', 
                           sample_size: Optional[int] = None,
                           min_topic_size: int = 10, 
                           nr_topics: Optional[int] = None,
                           output_dir: str = "clustering_results"):
    """运行完整的聚类流程"""
    
    # 创建聚类器
    clusterer = BERTopicClustering(
        min_topic_size=min_topic_size,
        nr_topics=nr_topics,
        verbose=True
    )
    
    # 加载数据
    if not clusterer.load_data(file_path, text_column, sample_size):
        logger.error("数据加载失败")
        return False
    
    # 训练模型
    if not clusterer.train_model():
        logger.error("模型训练失败")
        return False
    
    # 分析结果
    topic_info = clusterer.get_topic_info()
    if topic_info is not None:
        print("\n=== 主题信息 ===")
        print(topic_info)
    
    distribution = clusterer.analyze_topic_distribution()
    if distribution:
        print("\n=== 主题分布 ===")
        print(f"总文档数: {distribution['total_documents']}")
        print(f"有效主题数: {distribution['total_topics']}")
        print(f"噪声文档比例: {distribution['noise_ratio']:.2%}")
        print(f"平均主题大小: {distribution['avg_topic_size']:.1f}")
    
    # 保存结果
    clusterer.save_results(output_dir)
    
    return True


if __name__ == "__main__":
    # 示例用法
    clusterer = BERTopicClustering()
    print("BERTopic聚类器已初始化")