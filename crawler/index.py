import subprocess
import threading
import os
import sys

def run_scrapy_crawl():
    """在子线程中执行Scrapy爬虫命令"""
    try:
        # 获取当前脚本所在目录
        current_dir = os.path.dirname(os.path.abspath(__file__))
        weibo_search_dir = os.path.join(current_dir, 'weibo-search')
        
        # 检查目录是否存在
        if not os.path.exists(weibo_search_dir):
            print(f"错误: 目录 {weibo_search_dir} 不存在")
            return
            
        # 切换到weibo-search目录执行命令
        original_dir = os.getcwd()
        os.chdir(weibo_search_dir)
        
        # 确保crawls目录存在
        os.makedirs('crawls/search', exist_ok=True)
        
        # 执行Scrapy爬虫命令
        process = subprocess.Popen(
            ['scrapy', 'crawl', 'search', '-s', 'JOBDIR=crawls/search'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=weibo_search_dir  # 确保在正确的目录中执行
        )
        
        # 等待进程完成并获取输出
        stdout, stderr = process.communicate()
        
        if process.returncode == 0:
            print("爬虫执行成功:")
            print(stdout)
        else:
            print("爬虫执行失败:")
            print("错误信息:", stderr)
            
    except FileNotFoundError:
        print("错误: 未找到scrapy命令，请确保已安装scrapy并添加到PATH中")
    except Exception as e:
        print(f"执行爬虫时发生错误: {e}")
    finally:
        # 恢复原始目录
        os.chdir(original_dir)

if __name__ == '__main__':
    run_scrapy_crawl()
    # # 创建并启动线程来执行Scrapy爬虫
    # thread = threading.Thread(target=run_scrapy_crawl)
    # # 创建并启动线程来执行Scrapy爬虫
    # thread = threading.Thread(target=)
    # thread.daemon = True  # 设置为守护线程
    # thread.start()
    
    # # 等待线程完成（可选，根据需要决定是否等待）
    # thread.join()
    # print("爬虫线程执行完成")