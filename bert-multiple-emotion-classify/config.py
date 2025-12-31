import os
from type import label_dict

class Config:
    # 项目根目录 -> 工作目录
    base_dirname = os.getcwd()
    # 训练参数设置
    epoch_n = 6
    batch_size = 32
    max_length = 128
    use_fp16 = True
    gradient_checkpointing = True
    learning_rate = 5e-5  # 学习率
    accumulation_steps = 4  # 梯度积累 32 * 4 = 128
    # 模型与数据集路径
    model_path = os.path.join(base_dirname, "pretrained_model/bert-base-chinese")
    dataset_path = os.path.join(base_dirname, "dataset/processed_data.json")
    tokenized_dataset_path = os.path.join(base_dirname, "dataset/tokenized_data.json")
    # 分类数量
    class_num = len(label_dict)

