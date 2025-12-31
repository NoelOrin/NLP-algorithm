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

        # 确定scrapy命令的完整路径
        scrapy_cmd = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.venv', 'Scripts',
                                  'scrapy.exe')

        # 如果在Scripts目录中没有找到，尝试Scripts目录下的脚本
        scrapy_cmd = [sys.executable, '-m', 'scrapy']
        print("使用Python模块方式执行scrapy...")

        # 执行Scrapy爬虫命令
        cmd = [scrapy_cmd] if isinstance(scrapy_cmd, str) else scrapy_cmd
        cmd.extend(['crawl', 'search', '-s', 'JOBDIR=crawls/search', '-L', 'DEBUG'])

        # 使用流式输出方式运行爬虫
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,  # 行缓冲
            cwd=weibo_search_dir
        )

        # 实时读取并输出
        for line in iter(process.stdout.readline, ''):
            print(line.rstrip())

        for line in iter(process.stderr.readline, ''):
            print(line.rstrip(), file=sys.stderr)

        # 等待进程完成
        return_code = process.wait()

        if return_code == 0:
            print("爬虫执行成功")
        else:
            print("爬虫执行失败，返回码:", return_code)

    except FileNotFoundError:
        print("错误: 未找到scrapy命令，请确保已安装scrapy并添加到PATH中")
    except Exception as e:
        print(f"执行爬虫时发生错误: {e}")
    finally:
        # 恢复原始目录
        os.chdir(original_dir)


if __name__ == '__main__':
    run_scrapy_crawl()
