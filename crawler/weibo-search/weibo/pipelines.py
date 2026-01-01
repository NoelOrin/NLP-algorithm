# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

import copy
import csv
import os

import scrapy
from scrapy.exceptions import DropItem
from scrapy.pipelines.files import FilesPipeline
from scrapy.pipelines.images import ImagesPipeline
from scrapy.utils.project import get_project_settings

settings = get_project_settings()


class CsvPipeline(object):
    def process_item(self, item, spider):
        base_dir = '结果文件' + os.sep + item['keyword']
        if not os.path.isdir(base_dir):
            os.makedirs(base_dir)
        file_path = base_dir + os.sep + item['keyword'] + '.csv'
        if not os.path.isfile(file_path):
            is_first_write = 1
        else:
            is_first_write = 0

        if item:
            with open(file_path, 'a', encoding='utf-8-sig', newline='') as f:
                writer = csv.writer(f)
                if is_first_write:
                    header = [
                        'id', 'bid', 'user_id', '用户昵称', '微博正文', '头条文章url',
                        '发布位置', '艾特用户', '话题', '转发数', '评论数', '点赞数', '发布时间',
                        '发布工具', '微博图片url', '微博视频url', 'retweet_id', 'ip', 'user_authentication',
                        '会员类型', '会员等级'
                    ]
                    writer.writerow(header)

                writer.writerow([
                    item['weibo'].get('id', ''),
                    item['weibo'].get('bid', ''),
                    item['weibo'].get('user_id', ''),
                    item['weibo'].get('screen_name', ''),
                    item['weibo'].get('text', ''),
                    item['weibo'].get('article_url', ''),
                    item['weibo'].get('location', ''),
                    item['weibo'].get('at_users', ''),
                    item['weibo'].get('topics', ''),
                    item['weibo'].get('reposts_count', ''),
                    item['weibo'].get('comments_count', ''),
                    item['weibo'].get('attitudes_count', ''),
                    item['weibo'].get('created_at', ''),
                    item['weibo'].get('source', ''),
                    ','.join(item['weibo'].get('pics', [])),
                    item['weibo'].get('video_url', ''),
                    item['weibo'].get('retweet_id', ''),
                    item['weibo'].get('ip', ''),
                    item['weibo'].get('user_authentication', ''),
                    item['weibo'].get('vip_type', ''),
                    item['weibo'].get('vip_level', 0)
                ])
        return item

class SQLitePipeline(object):
    def open_spider(self, spider):
        try:
            import sqlite3
            # 在结果文件目录下创建SQLite数据库
            base_dir = '结果文件'
            if not os.path.isdir(base_dir):
                os.makedirs(base_dir)
            db_name = settings.get('SQLITE_DATABASE', 'weibo.db')
            self.conn = sqlite3.connect(os.path.join(base_dir, db_name))
            self.cursor = self.conn.cursor()
            # 创建表
            sql = """
            CREATE TABLE IF NOT EXISTS weibo (
                id varchar(20) NOT NULL PRIMARY KEY,
                bid varchar(12) NOT NULL,
                user_id varchar(20),
                screen_name varchar(30),
                text varchar(2000),
                article_url varchar(100),
                topics varchar(200),
                at_users varchar(1000),
                pics varchar(3000),
                video_url varchar(1000),
                location varchar(100),
                created_at DATETIME,
                source varchar(30),
                attitudes_count INTEGER,
                comments_count INTEGER,
                reposts_count INTEGER,
                retweet_id varchar(20),
                ip varchar(100),
                user_authentication varchar(100),
                vip_type varchar(50),
                vip_level INTEGER
            )"""
            self.cursor.execute(sql)
            self.conn.commit()
        except Exception as e:
            print(f"SQLite数据库创建失败: {e}")
            spider.sqlite_error = True


    def process_item(self, item, spider):
        data = dict(item['weibo'])
        data['pics'] = ','.join(data['pics'])
        keys = ', '.join(data.keys())
        placeholders = ', '.join(['?'] * len(data))
        sql = f"""INSERT OR REPLACE INTO weibo ({keys}) 
                 VALUES ({placeholders})"""
        try:
            self.cursor.execute(sql, tuple(data.values()))
            self.conn.commit()
        except Exception as e:
            print(f"SQLite保存出错: {e}")
            spider.sqlite_error = True
            self.conn.rollback()

    def close_spider(self, spider):
        self.conn.close()

class MyImagesPipeline(ImagesPipeline):
    def get_media_requests(self, item, info):
        if len(item['weibo']['pics']) == 1:
            yield scrapy.Request(item['weibo']['pics'][0],
                                 meta={
                                     'item': item,
                                     'sign': ''
                                 })
        else:
            sign = 0
            for image_url in item['weibo']['pics']:
                yield scrapy.Request(image_url,
                                     meta={
                                         'item': item,
                                         'sign': '-' + str(sign)
                                     })
                sign += 1

    def file_path(self, request, response=None, info=None):
        image_url = request.url
        item = request.meta['item']
        sign = request.meta['sign']
        base_dir = '结果文件' + os.sep + item['keyword'] + os.sep + 'images'
        if not os.path.isdir(base_dir):
            os.makedirs(base_dir)
        image_suffix = image_url[image_url.rfind('.'):]
        file_path = base_dir + os.sep + item['weibo'][
            'id'] + sign + image_suffix
        return file_path


class MyVideoPipeline(FilesPipeline):
    def get_media_requests(self, item, info):
        if item['weibo']['video_url']:
            yield scrapy.Request(item['weibo']['video_url'],
                                 meta={'item': item})

    def file_path(self, request, response=None, info=None):
        item = request.meta['item']
        base_dir = '结果文件' + os.sep + item['keyword'] + os.sep + 'videos'
        if not os.path.isdir(base_dir):
            os.makedirs(base_dir)
        file_path = base_dir + os.sep + item['weibo']['id'] + '.mp4'
        return file_path


class MongoPipeline(object):
    def open_spider(self, spider):
        try:
            from pymongo import MongoClient
            self.client = MongoClient(settings.get('MONGO_URI'))
            self.db = self.client['weibo']
            self.collection = self.db['weibo']
        except ModuleNotFoundError:
            spider.pymongo_error = True

    def process_item(self, item, spider):
        try:
            import pymongo

            new_item = copy.deepcopy(item)
            if not self.collection.find_one({'id': new_item['weibo']['id']}):
                self.collection.insert_one(dict(new_item['weibo']))
            else:
                self.collection.update_one({'id': new_item['weibo']['id']},
                                           {'$set': dict(new_item['weibo'])})
        except pymongo.errors.ServerSelectionTimeoutError:
            spider.mongo_error = True

    def close_spider(self, spider):
        try:
            self.client.close()
        except AttributeError:
            pass
class PostgresqlPipeline(object):
    """PostgreSQL数据库管道"""

    def __init__(self):
        """初始化PostgreSQL连接配置"""
        # PostgreSQL连接配置
        self.pg_config = {
            'host': settings.get('POSTGRESQL_HOST', 'localhost'),
            'port': settings.get('POSTGRESQL_PORT', 5432),
            'user': settings.get('POSTGRESQL_USER', 'NoelOrin'),
            'password': settings.get('POSTGRESQL_PASSWORD', 'Aa18520863834'),
            'database': settings.get('POSTGRESQL_DATABASE', 'nlp_db'),
            'client_encoding': 'utf8'
        }
        self.conn = None
        self.cursor = None

        # 统计配置
        self.total_processed = 0  # 总处理数量
        self.error_count = 0  # 错误计数

    def create_database(self):
        """创建PostgreSQL数据库"""
        import psycopg2
        # 连接到默认数据库创建目标数据库
        temp_config = self.pg_config.copy()
        temp_config['database'] = 'nlp_db'  # 连接到默认数据库

        try:
            conn = psycopg2.connect(**temp_config)
            conn.autocommit = True
            cursor = conn.cursor()

            # 检查数据库是否存在
            cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s",
                         (self.pg_config['database'],))
            exists = cursor.fetchone()

            if not exists:
                # 创建数据库
                cursor.execute(f"CREATE DATABASE {self.pg_config['database']} ENCODING 'UTF8'")
                print(f"创建数据库: {self.pg_config['database']}")

            cursor.close()
            conn.close()
        except Exception as e:
            print(f"创建数据库失败: {e}")

    def create_table(self):
        """创建PostgreSQL表"""
        sql = """
        CREATE TABLE IF NOT EXISTS weibo_blogs (
            id VARCHAR(20) PRIMARY KEY,
            bid VARCHAR(12) NOT NULL UNIQUE,
            user_id VARCHAR(20),
            screen_name VARCHAR(30),
            text TEXT,
            article_url VARCHAR(100),
            topics VARCHAR(200),
            at_users TEXT,
            pics TEXT,
            video_url TEXT,
            location VARCHAR(100),
            created_at TIMESTAMP,
            source VARCHAR(30),
            attitudes_count INTEGER,
            comments_count INTEGER,
            reposts_count INTEGER,
            retweet_id VARCHAR(20),
            ip VARCHAR(100),
            user_authentication VARCHAR(100),
            vip_type VARCHAR(50),
            vip_level INTEGER,
            created_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )"""

        try:
            self.cursor.execute(sql)
            self.conn.commit()
            print("PostgreSQL表已创建或已存在")
        except Exception as e:
            print(f"创建表失败: {e}")
            self.conn.rollback()

    def open_spider(self, spider):
        """爬虫开始时连接数据库"""
        try:
            import psycopg2

            # 创建数据库
            self.create_database()

            # 连接到目标数据库
            self.conn = psycopg2.connect(**self.pg_config)
            self.cursor = self.conn.cursor()

            # 创建表
            self.create_table()

            print("PostgreSQL连接成功")

        except ImportError:
            print("psycopg2模块未安装")
            spider.postgresql_error = True
        except Exception as e:
            print(f"PostgreSQL连接失败: {e}")
            spider.postgresql_error = True
            
    def process_item(self, item, spider):
        """处理微博数据项 - 逐条写入"""
        if hasattr(spider, 'postgresql_error') and spider.postgresql_error:
            return item
            
        try:
            data = dict(item['weibo'])
            data['pics'] = ','.join(data['pics'])
            
            # 处理空值
            for key in data:
                if data[key] is None:
                    data[key] = ''
            
            # 构建SQL语句
            keys = ', '.join(data.keys())
            values = ', '.join(['%s'] * len(data))
            
            sql = """INSERT INTO weibo_blogs({keys}) VALUES ({values}) ON 
                      CONFLICT (id) DO UPDATE SET""".format(keys=keys, values=values)
            
            update = ','.join([" {key} = EXCLUDED.{key}".format(key=key) for key in data if key != 'id'])
            sql += update
            
            # 执行SQL
            self.cursor.execute(sql, tuple(data.values()))
            self.conn.commit()
            
            # 更新统计信息
            self.total_processed += 1
            if self.total_processed % 100 == 0:
                print(f"已处理 {self.total_processed} 条数据")
            
        except Exception as e:
            print(f"处理数据项失败: {e}")
            try:
                self.conn.rollback()
            except:
                pass
            
        return item

    def close_spider(self, spider):
        """爬虫结束时关闭数据库连接"""
        # 输出最终统计信息
        print(f"\nPostgreSQL管道处理完成，共处理 {self.total_processed} 条数据")
        
        if self.conn:
            try:
                self.cursor.close()
                self.conn.close()
                print("PostgreSQL连接已关闭")
            except Exception as e:
                print(f"关闭PostgreSQL连接失败: {e}")


class DuplicatesPipeline(object):
    def __init__(self):
        self.ids_seen = set()

    def process_item(self, item, spider):
        if item['weibo']['id'] in self.ids_seen:
            raise DropItem("过滤重复微博: %s" % item)
        else:
            self.ids_seen.add(item['weibo']['id'])
            return item
