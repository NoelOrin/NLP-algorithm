import csv
import json
import re
import emoji
import jieba
from transformers import BertTokenizer

from config import Config
from type.label import label_dict


def preprocess_csv_to_json(input_csv, output_json):
    """
    读取CSV文件，清洗数据，并导出为包含 id、text、label 的JSON文件。

    参数:
        input_csv (str): CSV文件路径（tab分隔，含表头）
        output_json (str): 输出JSON文件路径
    """

    # 定义清理文本的函数
    def clean_text(text):
        text = emoji.replace_emoji(text, replace='')  # 删除所有 emoji
        # 去除多余空格
        text = re.sub(r'\s+', ' ', text).strip()
        # 去除 [表情] 类似格式的标签，如 [震惊]、[蛋糕]、[害羞]
        parts = text.split('[')
        cleaned_parts = [part.split(']', 1)[-1] for part in parts]
        cleaned_text = ''.join(cleaned_parts)
        return cleaned_text

    json_data = []

    with open(input_csv, mode='r', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile, delimiter='\t')  # 使用 tab 分隔读取
        header = next(reader)  # 跳过表头

        for row in reader:
            if len(row) < 3:  # 确保至少有 id, text, label 三个字段
                continue

            entry_id = row[0].strip()  # 第一列为 ID
            raw_text = ' '.join(row[1:-1])  # 合并中间为文本内容
            label = row[-1].strip()  # 最后一列为标签

            cleaned_text = clean_text(raw_text)  # 清洗文本

            json_data.append({
                "id": entry_id,
                "text": cleaned_text,
                "label": label_dict.get(label)
            })

    # 写入 JSON 文件
    with open(output_json, 'w', encoding='utf-8') as jsonfile:
        json.dump(json_data, jsonfile, ensure_ascii=False, indent=2)

    print(f"✅ 数据已成功导出到 {output_json}")
    return output_json

def tokenizeDataset(input_json, output_json):
    with open(input_json, 'r', encoding='utf-8') as f:
        data = json.load(f)

    tokenized_data = []
    tokenizer = BertTokenizer.from_pretrained(Config.model_path, config=Config)
    for item in data:
        original_text = item.get("text", "")
        tokenized_text = tokenizer()
        tokenized_item = {
            "id": item["id"],
            "text": tokenized_text,
            "label": item["label"]
        }
        tokenized_data.append(tokenized_item)

    with open(output_json, 'w', encoding='utf-8') as f:
        json.dump(tokenized_data, f, ensure_ascii=False, indent=2)
        print(f"✅ 预处理完成，已保存至 {output_json}")
    return output_json

# jieba分词处理 废弃
def pretreat_json_text(input_json, output_json):
    # 自定义停用词列表或加载外部文件
    STOPWORDS = {'的', '了', '是', '在', '和', '我', '有', '不', '人', '都', '一', '个', '你', '这', '很', '与', '上',
                 '们',
                 '到', '也', '他', '她'}

    def tokenize_and_remove_stopwords(text, stopwords=None):
        if stopwords is None:
            stopwords = STOPWORDS
        tokens = list(jieba.cut(text))
        filtered_tokens = [token for token in tokens if token not in stopwords]
        return ' '.join(filtered_tokens)

    def preprocess_text(text):
        processed_text = tokenize_and_remove_stopwords(text)
        return processed_text

    with open(input_json, 'r', encoding='utf-8') as f:
        data = json.load(f)

    processed_data = []

    for item in data:
        original_text = item.get("text", "")
        processed_text = preprocess_text(original_text)
        processed_item = {
            "id": item["id"],
            "text": processed_text,
            "label": item["label"]
        }
        processed_data.append(processed_item)

    with open(output_json, 'w', encoding='utf-8') as f:
        json.dump(processed_data, f, ensure_ascii=False, indent=2)
        print(f"✅ 预处理完成，已保存至 {output_json}")

if __name__ == '__main__':
    # 生成清洗后json数据集
    output_json_path = preprocess_csv_to_json(
        input_csv='../dataset/OCEMOTION.csv',
        output_json='../dataset/processed_data.json'
    )
    # 生成jieba分词后的词元数据集
    # pretreat_json_text(input_json=output_json_path,
    #                    output_json='../dataset/pretreatment_data.json')
