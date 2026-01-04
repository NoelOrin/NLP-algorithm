from urllib import request
from service.api.weibo.weibo_blog_comment import WeiboBlogCommentType


def extract_topic(content: WeiboBlogCommentType) -> list[str]:
    """提取文本中的主题"""
    req = request.Request(
        url="http://localhost:8000/topic/classification",
        method="POST",
        data=content.encode("utf-8"),
        headers={
            "Content-Type": "application/json"
        }
    )

    with request.urlopen(req) as resp:
        data = resp.read().decode("utf-8")

    return data


if __name__ == '__main__':
    print(extract_topic({
        "id": "123",
        "bid": "456",
        "content": "这是一条关于Python的微博",
        "comments": []
    }))
