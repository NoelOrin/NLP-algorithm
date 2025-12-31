# Step 1: 导入必要的模块
import torch
from transformers import BertTokenizer, BertModel

# Step 2: 设置模型路径（请确保该路径下有 vocab.txt 和其他模型文件）
model_path = "../pretrained_model/bert-base-chinese"  # 注意：路径不要带引号以外的符号，如中文引号或乱码

# Step 3: 加载分词器和模型
tokenizer = BertTokenizer.from_pretrained(model_path)
model = BertModel.from_pretrained(model_path)

# Step 4: 打印分词器支持的最大输入长度
print(f"Maximum tokenizer input length: {tokenizer.model_max_length}")

# Step 5: 定义待处理的文本
texts = [
    "你好，世界！",
    "我喜欢编程。我是一个学生。",
]

# Step 6: 使用 tokenizer 对文本进行编码
tokens = tokenizer(
    texts,                       # 输入文本列表
    add_special_tokens=True,   # 添加 [CLS], [SEP] 等特殊标记
    padding=True,              # 填充至最大长度
    truncation=True,           # 自动截断超出最大长度的部分
    max_length=128,            # 设置最大序列长度
    return_tensors='pt'        # 返回 PyTorch 张量
)

# Step 7: 提取 input_ids 和 attention_mask
input_ids = tokens['input_ids']
attention_mask = tokens['attention_mask']

# Step 8: 打印张量形状和内容
print("Shape of input_ids:", input_ids.shape)
print(input_ids)

print("\nShape of attention_mask:", attention_mask.shape)
print(attention_mask)

# 得到模型的特征提取结果
model = BertModel.from_pretrained(model_path)
# 将input ids.和attention mask传入model,得到BERT模型的特征提取结果
features = model(input_ids=input_ids, attention_mask=attention_mask)
# Step 10: 提取 pooler_output（[CLS] token 经过池化后的向量）
pooler_output = features.pooler_output

# Step 11: 打印结果
print("Shape of pooler_output:", pooler_output.shape)
print(pooler_output)