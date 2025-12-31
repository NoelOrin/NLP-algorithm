import json
import os
import torch
from torch.utils.data import Dataset

from config import Config


# 继承pytorch数据集类
class TextClassifyDataset(Dataset):
    def __init__(self, path):
        self.examples = []
        with open(path, 'r', encoding='utf-8') as file:
            data_list = json.load(file)  # 一次性加载整个 JSON 数组
            for data in data_list:
                try:
                    text = data['text']
                    label = int(data['label'])
                    self.examples.append((text, int(label)))
                except KeyError as e:
                    print(f"缺少必要字段 {e}，跳过该条数据：{data}")
                    continue

    def __len__(self):
        return len(self.examples)

    def __getitem__(self, index):
        return self.examples[index]


# collate_fn 函数：对每个 batch 进行分词和填充
def collate_fn(batch, tokenizer):
    texts = [item[0] for item in batch]
    labels = [item[1] for item in batch]

    # 使用 tokenizer 对整个 batch 的文本进行编码
    encoded_inputs = tokenizer(
        texts,
        add_special_tokens=True,
        padding=True,
        truncation=True,
        max_length=Config.max_length,
        return_tensors="pt"
    )

    input_ids = encoded_inputs['input_ids']
    attention_mask = encoded_inputs['attention_mask']
    labels = torch.tensor(labels, dtype=torch.long)
    print(labels)
    return input_ids, attention_mask, labels