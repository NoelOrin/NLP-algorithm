# Step 1: 导入必要的模块
import torch
from transformers import BertTokenizer, BertModel
import torch.nn as nn

from config import Config
from model.BertClassifier import BertClassifier

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Step 3: 加载分词器和模型
tokenizer = BertTokenizer.from_pretrained(Config.model_path)
bert_model = BertModel.from_pretrained(Config.model_path)

# Step 5: 初始化模型并设置为评估模式
model = BertClassifier(model_path=Config.model_path, class_num=Config.class_num)
# 加载权重 如果是 GPU 训练的模型，map_location 可选
model.load_state_dict(torch.load("output_trained_models/chinese_news_classify_2.pth", map_location=device))
model.eval()  # 推理时使用 eval 模式

# Step 6: 定义待分类的文本
texts = [
    "我非常喜欢这个产品，它太棒了！",     # 正面
    "服务很差，完全不推荐这家店。",        # 负面
]

# Step 7: 使用 tokenizer 对文本进行编码
tokens = tokenizer(
    texts,
    add_special_tokens=True,
    padding=True,
    truncation=True,
    max_length=128,
    return_tensors='pt'
)

input_ids = tokens['input_ids']
attention_mask = tokens['attention_mask']

# Step 8: 进行推理
with torch.no_grad():
    logits = model(input_ids, attention_mask)

# Step 9: 获取预测结果
probs = torch.softmax(logits, dim=1)  # 转换为概率
predictions = torch.argmax(logits, dim=1)  # 获取预测类别

# Step 10: 打印结果
for i, text in enumerate(texts):
    label = "正面" if predictions[i].item() == 1 else "负面"
    print(f"文本: {text} | 预测: {label} | 置信度: {probs[i][predictions[i]].item():.4f}")