import requests

from type import TextItem, TextList


def post_infer_predict(text: TextItem="这是一条测试文本"):
    url = 'http://0.0.0.0:8848/predict'
    payload = {
        "text": text
    }

    try:
        res = requests.post(url, json=payload)
        res.raise_for_status()  # 抛出 HTTPError（如果不是 200）

        result = res.json()  # FastAPI 默认返回 JSON
        print("预测结果：", result)
    except requests.exceptions.RequestException as e:
        print("请求出错：", e)

def post_infer_bulk_predict(texts: TextList=["这是一条测试文本"]):
    url = 'http://0.0.0.0:8848/bulk_predict'
    payload = {
        "texts": texts
    }

    try:
        res = requests.post(url, json=payload)
        res.raise_for_status()  # 抛出 HTTPError（如果不是 200）

        result = res.json()  # FastAPI 默认返回 JSON
        print("预测结果：", result)
    except requests.exceptions.RequestException as e:
        print("请求出错：", e)



if __name__ == '__main__':
    post_infer_predict()
    post_infer_bulk_predict()