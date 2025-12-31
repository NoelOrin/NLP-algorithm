import torch
from torch import nn
from transformers import BertModel, BertConfig


# 小黑黑讲AI：构建一个基于 BERT 的文本分类模型
class BertClassifier(nn.Module):
    """
    BERT 分类模型，封装预训练的 BERT 模型 + 线性分类层
    用于细粒度情感分类任务（如舆情分析）
    """

    def __init__(self, model_path, class_num):
        """
        :param model_path: 预训练 BERT 模型路径（本地或 HuggingFace ID）
        :param class_num: 分类的类别数量
        """
        super(BertClassifier, self).__init__()

        # 加载预训练的 BERT 模型作为特征提取器
        self.bert = BertModel.from_pretrained(model_path)

        # 获取 BERT 的隐藏层维度（base 版本为 768）
        hidden_size = self.bert.config.hidden_size or 768

        # 添加一个线性分类层：768 -> class_num
        self.classifier = nn.Linear(hidden_size, class_num)

    def forward(self, input_ids, attention_mask):
        """
        前向传播函数
        :param input_ids: token 的索引序列 (batch_size, seq_length)
        :param attention_mask: 区分真实 token 和 padding 的 mask (batch_size, seq_length)
        :return: logits (batch_size, class_num)
        """

        # 将输入传入 BERT 模型，得到输出
        features = self.bert(
            input_ids=input_ids,
            attention_mask=attention_mask
        )
        # 提取 [CLS] token 经过池化后的向量（句子级别的表示）
        pooled_output = features.pooler_output
        # 将特征向量送入分类层进行分类 (线性层
        logits = self.classifier(pooled_output)

        return logits
