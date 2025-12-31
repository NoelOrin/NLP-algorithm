from fastapi import FastAPI
import torch
from transformers import BertTokenizer
from model.BertClassifier import BertClassifier
from config import Config
from type import label_dict, reversed_dict, TextItem, TextList

app = FastAPI()

# 设备选择
device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

# 加载模型
model = BertClassifier(Config.model_path, Config.class_num)
model.load_state_dict(torch.load('./output_trained_models/zh_cn_epoch-6_batch_size-32.pth', map_location=device))
model.to(device)
model.eval()

# 加载分词器
tokenizer = BertTokenizer.from_pretrained(Config.model_path)

num2label_dict = reversed_dict(label_dict)

print('have loaded')

# 推理函数
def predict(texts):
    inputs = tokenizer(
        texts,
        padding=True,
        truncation=True,
        max_length=getattr(Config, 'max_len', 128),
        return_tensors="pt"
    )

    input_ids = inputs["input_ids"].to(device)
    attention_mask = inputs["attention_mask"].to(device)

    with torch.no_grad():
        outputs = model(input_ids, attention_mask)
        predictions = torch.argmax(outputs, dim=1)
        return predictions.cpu().tolist()


# 单条预测接口
@app.post("/predict")
def predict_single(item: TextItem):
    label = predict([item.text])[0]
    label = num2label_dict[label]
    return {"text": item.text, "label": label}


# 批量预测接口
@app.post("/bulk_predict")
def predict_batch(items: TextList):
    labels = predict(items.texts)
    labels = [num2label_dict[label] for label in labels]
    return [{"text": text, "label": label} for text, label in zip(items.texts, labels)]
