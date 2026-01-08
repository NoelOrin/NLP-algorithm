"""
中文文本预处理器
用于BERTopic系统的文本预处理，包括文本清洗、分词、停用词过滤等功能
"""

import re
import jieba
import jieba.posseg as pseg
from typing import List, Optional


class ChineseTextPreprocessor:
    """中文文本预处理器"""
    
    def __init__(self, stopwords_file: Optional[str] = None, user_dict_file: Optional[str] = None):
        """
        初始化预处理器
        
        Args:
            stopwords_file: 停用词文件路径
            user_dict_file: 用户词典文件路径
        """
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
    
    def load_stopwords(self, filepath: str) -> None:
        """加载停用词文件"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                words = {line.strip() for line in f if line.strip()}
                self.stopwords.update(words)
        except FileNotFoundError:
            print(f"警告: 停用词文件 {filepath} 不存在，使用默认停用词")
    
    def clean_text(self, text: str) -> str:
        """
        清洗文本
        
        Args:
            text: 原始文本
            
        Returns:
            清洗后的文本
        """
        if not text or not text.strip():
            return ""
        
        # 去除HTML标签
        text = re.sub(r'<[^>]+>', '', text)
        
        # 去除URL
        text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
        
        # 去除@用户提及
        text = re.sub(r'@[\w\u4e00-\u9fa5]+', '', text)
        
        # 去除话题标签但保留内容
        # text = re.sub(r'#[^#]+#', lambda x: x.group()[1:-1], text)
        
        # 去除表情符号
        text = re.sub(r'\[[^\]]+\]', '', text)  # 微博表情格式 [xxx]
        
        # 去除特殊字符和标点符号（保留中文标点）
        text = re.sub(r'[^\w\s\u4e00-\u9fa5，。！？；：""''《》（）【】]', '', text)
        
        # 去除多余空格
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def segment_text(self, text: str, remove_stopwords: bool = True, use_pos: bool = False) -> str:
        """
        分词处理
        
        Args:
            text: 清洗后的文本
            remove_stopwords: 是否移除停用词
            use_pos: 是否使用词性标注
            
        Returns:
            分词后的文本（空格分隔）
        """
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
    
    def preprocess_pipeline(self, texts: List[str], remove_stopwords: bool = True, 
                          use_pos: bool = False) -> List[str]:
        """
        完整的预处理流水线
        
        Args:
            texts: 原始文本列表
            remove_stopwords: 是否移除停用词
            use_pos: 是否使用词性标注
            
        Returns:
            预处理后的文本列表
        """
        processed_texts = []
        
        for text in texts:
            # 文本清洗
            cleaned = self.clean_text(text)
            
            # 跳过空文本
            if not cleaned:
                continue
            
            # 分词处理
            segmented = self.segment_text(cleaned, remove_stopwords, use_pos)
            
            # 跳过分词后为空的结果
            if segmented.strip():
                processed_texts.append(segmented)
        
        return processed_texts


def preprocess_pipeline(texts: List[str], **kwargs) -> List[str]:
    """
    便捷的预处理函数
    
    Args:
        texts: 原始文本列表
        **kwargs: 传递给ChineseTextPreprocessor的参数
        
    Returns:
        预处理后的文本列表
    """
    preprocessor = ChineseTextPreprocessor(**kwargs)
    return preprocessor.preprocess_pipeline(texts)


if __name__ == "__main__":
    # 测试代码
    preprocessor = ChineseTextPreprocessor()
    
    test_texts = [
        "今天天气真好！#天气# @用户  http://example.com 适合出去散步",
        "机器学习是人工智能的重要分支",
        "",  # 空文本
        "   ",  # 只有空格的文本
        "Python是数据科学的首选语言!!!"
    ]
    
    print("=== 测试数据预处理器 ===")
    for i, text in enumerate(test_texts):
        cleaned = preprocessor.clean_text(text)
        segmented = preprocessor.segment_text(cleaned)
        print(f"原文 {i+1}: {text}")
        print(f"清洗后: {cleaned}")
        print(f"分词后: {segmented}")
        print("-" * 50)