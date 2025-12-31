label_dict = {
    'sadness': 0,
    'happiness': 1,
    'anger': 2,
    'fear': 3,
    'surprise': 4,
    'disgust': 5,
    'like': 6
}
# 反转 key val
def reversed_dict(dict):
    return {value: key for key, value in dict.items()}
