# -*- coding: utf-8 -*-

BOT_NAME = 'weibo_crawler'
SPIDER_MODULES = ['weibo.spiders']
NEWSPIDER_MODULE = 'weibo.spiders'
COOKIES_ENABLED = False
TELNETCONSOLE_ENABLED = False
LOG_LEVEL = 'ERROR'
# 访问完一个页面再访问下一个时需要等待的时间，默认为5秒
DOWNLOAD_DELAY = 5
DEFAULT_REQUEST_HEADERS = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-US;q=0.7',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36 Edg/128.0.0.0',
    'Cookie': '_T_WM=0601f8b79ee7de682115d889b070c4d3; SCF=ArMQAAJmyIG49ARh17nK3PgjUV15xWAqieE_jmgpqmK6EBv6JEuOrloQt868CZ5yThTA3pxgFX7f0An6IYfJa2I.; SUB=_2A25EXwvEDeRhGe9O6VcZ8C7FyD-IHXVnFQEMrDV6PUJbktANLXXMkW1NdKWo_UJ8t0S55YmPJM9PJIsqT4g9-XGO; SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9Wh8HILbCB1TnVb5veiMiHfR5JpX5KMhUgL.Fo.7eo-Reh54e0e2dJLoIp7LxKML1KBLBKnLxKqL1hnLBoM4ehzf1h571Ke0;'
}
ITEM_PIPELINES = {
    'weibo.pipelines.DuplicatesPipeline': 300,
    'weibo.pipelines.PostgresqlPipeline': 301
}
# 要搜索的关键词列表，可写多个, 值可以是由关键词或话题组成的列表，也可以是包含关键词的txt文件路径，
# 如'keyword_list.txt'，txt文件中每个关键词占一行
KEYWORD_LIST = ['舆论','社会','社会问题', '政治','新闻','事件']  # 或者 KEYWORD_LIST = 'keyword_list.txt'
# 要搜索的微博类型，0代表搜索全部微博，1代表搜索全部原创微博，2代表热门微博，3代表关注人微博，4代表认证用户微博，5代表媒体微博，6代表观点微博
WEIBO_TYPE = 5
# 筛选结果微博中必需包含的内容，0代表不筛选，获取全部微博，1代表搜索包含图片的微博，2代表包含视频的微博，3代表包含音乐的微博，4代表包含短链接的微博
CONTAIN_TYPE = 0
# 筛选微博的发布地区，精确到省或直辖市，值不应包含“省”或“市”等字，如想筛选北京市的微博请用“北京”而不是“北京市”，想要筛选安徽省的微博请用“安徽”而不是“安徽省”，可以写多个地区，
# 具体支持的地名见region.py文件，注意只支持省或直辖市的名字，省下面的市名及直辖市下面的区县名不支持，不筛选请用“全部”
REGION = ['全部']
# 搜索的起始日期，为yyyy-mm-dd形式，搜索结果包含该日期
START_DATE = '2025-12-10'
# 搜索的终止日期，为yyyy-mm-dd形式，搜索结果包含该日期
END_DATE = '2026-01-06'
# 进一步细分搜索的阈值，若结果页数大于等于该值，则认为结果没有完全展示，细分搜索条件重新搜索以获取更多微博。数值越大速度越快，也越有可能漏掉微博；数值越小速度越慢，获取的微博就越多。
# 建议数值大小设置在40到50之间。
FURTHER_THRESHOLD = 50
# 爬取结果的数量限制，爬取到该数量的微博后自动停止，设置为0代表不限制
LIMIT_RESULT = 10000
# 图片文件存储路径
IMAGES_STORE = './'
# 视频文件存储路径
FILES_STORE = './'

# 配置PostgreSQL数据库
POSTGRESQL_HOST = 'localhost'
POSTGRESQL_PORT = 5432
POSTGRESQL_USER = 'NoelOrin'
POSTGRESQL_PASSWORD = 'Aa18520863834 '
POSTGRESQL_DATABASE = 'nlp_db'
