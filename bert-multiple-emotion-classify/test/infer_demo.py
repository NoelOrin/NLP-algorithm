import torch
from transformers import BertTokenizer
from model.BertClassifier import BertClassifier
from config import Config

# 设置设备
device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

# 加载模型
model = BertClassifier(Config.model_path, Config.class_num)
model.load_state_dict(torch.load('./output_trained_models/zh_cn_epoch-4_batch_size-24.pth', map_location=device))
model.to(device)
model.eval()

# 加载 tokenizer
tokenizer = BertTokenizer.from_pretrained(Config.model_path)

# 预测函数
def predict(texts):
    """
    :param texts: List[str]，要预测的句子列表
    :return: List[int]，每个句子的预测类别索引
    """
    inputs = tokenizer(texts,
                       padding=True,
                       truncation=True,
                       max_length=Config.max_len if hasattr(Config, 'max_len') else 128,
                       return_tensors="pt")

    input_ids = inputs["input_ids"].to(device)
    attention_mask = inputs["attention_mask"].to(device)

    with torch.no_grad():
        outputs = model(input_ids, attention_mask)
        predictions = torch.argmax(outputs, dim=1)
        return predictions.cpu().tolist()

# 示例文本
test_texts = [
    "这个产品非常好用，我很喜欢！",
    "服务态度太差了，差评！",
    "价格还可以，性价比高",
    "我不推荐这个商家"
]

# 进行预测
predicted_labels = predict(test_texts)

# 打印结果
for text, label in zip(test_texts, predicted_labels):
    print(f"文本: {text}\n预测类别: {label}\n")
