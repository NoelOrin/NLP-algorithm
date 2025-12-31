import time

from torch.utils.data import DataLoader
from transformers import BertTokenizer
import os
from tqdm import tqdm
from config import Config
from dataset_formator import TextClassifyDataset, collate_fn, CSVClassifyDataset
from model.BertClassifier import BertClassifier
import torch
import torch.nn as nn
import torch.optim as optim
from transformers import get_linear_schedule_with_warmup
from torch.utils.data import random_split

from temp import BertAdam

from torch.cuda.amp import autocast, GradScaler





model_path = Config.model_path
dataset_path = Config.dataset_path
class_num = Config.class_num

if __name__ == '__main__':
    # 设置训练轮数
    epoch_n = Config.epoch_n
    # 定义设备：检查是否有 GPU 可用
    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    print(f"device = {device}")
    scaler = GradScaler()

    dataset = TextClassifyDataset(dataset_path)

    tokenizer = BertTokenizer.from_pretrained(model_path,
                                              # config=Config
                                              )

    dataLoader = DataLoader(dataset=dataset,
                            batch_size=Config.batch_size,
                            shuffle=True,
                            collate_fn=lambda x: collate_fn(x, tokenizer)
                            )

    # # 假设你希望用 90% 数据训练，10% 验证
    # train_size = int(0.9 * len(dataset))
    # val_size = len(dataset) - train_size
    #
    # train_dataset, val_dataset = random_split(dataset, [train_size, val_size])
    #
    # # 创建两个 DataLoader
    # train_loader = DataLoader(train_dataset, batch_size=Config.batch_size, shuffle=True,
    #                           collate_fn=lambda x: collate_fn(x, tokenizer))
    # val_loader = DataLoader(val_dataset, batch_size=Config.batch_size, shuffle=False,
    #                         collate_fn=lambda x: collate_fn(x, tokenizer))

    # 实例化模型并移动到设备上
    model = BertClassifier(model_path, class_num).to(device)

    # 定义优化器（使用 AdamW）
    # optimizer = optim.AdamW(model.parameters(), lr=Config.learning_rate)

    param_optimizer = list(model.named_parameters())
    no_decay = ['bias', 'LayerNorm.bias', 'LayerNorm.weight']
    optimizer_grouped_parameters = [
        {'params': [p for n, p in param_optimizer if not any(nd in n for nd in no_decay)], 'weight_decay': 0.01},
        {'params': [p for n, p in param_optimizer if any(nd in n for nd in no_decay)], 'weight_decay': 0.0}]


    optimizer = BertAdam(optimizer_grouped_parameters,
                         lr=Config.learning_rate,
                         warmup=0.05,
                         t_total=len(dataLoader) * Config.epoch_n)

    # optimizer = AdamW(optimizer_grouped_parameters, lr=Config.learning_rate)

    # 学习率
    total_steps = len(dataLoader) * epoch_n
    scheduler = get_linear_schedule_with_warmup(
        optimizer,
        num_warmup_steps=int(total_steps * 0.1),  # 假设我们希望前10%的步骤作为预热阶段
        num_training_steps=total_steps
    )

    # 定义损失函数（交叉熵损失）
    criterion = nn.CrossEntropyLoss()

    # 设置为训练模式
    model.train()
    # 创建保存模型的目录
    os.makedirs('output_trained_models', exist_ok=True)

    # 迭代训练
    for epoch in range(1, epoch_n + 1):
        progress_bar = tqdm(dataLoader, desc=f"Epoch {epoch}/{epoch_n}", leave=False)  # 进度条
        for batch_idx, data in enumerate(progress_bar):
            input_ids = data[0].to(device)
            attention_mask = data[1].to(device)
            label = data[2].to(device)

            # output = model(input_ids, attention_mask)  # 前向传播
            # loss = criterion(output, label)  # 计算损失
            #
            # loss.backward()  # 计算梯度
            # optimizer.step()  # 更新模型参数

            with autocast():
                output = model(input_ids, attention_mask)
                loss = criterion(output, label)

            loss = loss / Config.accumulation_steps  # 梯度累积

            scaler.scale(loss).backward()
            scaler.unscale_(optimizer)  # 先反缩放梯度
            torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
            scaler.step(optimizer)
            scaler.update()
            optimizer.zero_grad()
            # 更新学习率调度器
            scheduler.step()

            predict = torch.argmax(output, dim=1)
            correct = (predict == label).sum().item()
            acc = correct / output.size(0)

            # 更新进度条描述
            progress_bar.set_postfix({
                'Loss': f'{loss.item():.4f}',
                'Acc': f' {correct} / {output.size(0)} = {acc:.3f}'
            })

            del input_ids, attention_mask, label, output, loss, predict
            torch.cuda.empty_cache()
            torch.cuda.ipc_collect()  # 额外清理 IPC 内存泄漏（可选）

        # 每一轮迭代，都保存一次模型
        model_name = f'./output_trained_models/zh_cn_epoch-{epoch}_batch_size-{Config.batch_size}-{time.time()}.pth'
        print("saved model: %s" % model_name)
        torch.save(model.state_dict(), model_name)
