import json
import os
import torch
from torch.utils.data import Dataset

# 继承pytorch数据集类
class CSVClassifyDataset(Dataset):
    def __init__(self, path):
        self.examples = []
        file = open(path, 'r', encoding='utf-8')
        for line in file:
            line = line.strip()
            if not line:  # 跳过空行
                continue
            parts = line.split('\t')
            if len(parts) == 3:
                _, text, label = parts
            elif len(parts) == 2:
                text, label = parts
            else:
                continue  # 跳过格式错误行
            self.texts.append(text)
            self.labels.append(label)

        file.close()

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
        max_length=512,
        return_tensors="pt"
    )

    input_ids = encoded_inputs['input_ids']
    attention_mask = encoded_inputs['attention_mask']
    labels = torch.tensor(labels, dtype=torch.long)

    return input_ids, attention_mask, labels