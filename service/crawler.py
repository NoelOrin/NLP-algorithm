import subprocess
import threading
import time
import os
import signal
import psutil
from datetime import datetime
from typing import Optional, Dict, Any


class ScrapyCrawlerSingleton:
    """Scrapy爬虫单例类"""
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        """实现单例模式"""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """初始化单例"""
        if not self._initialized:
            self.active_crawlers = {}
            self.crawler_status = {}
            self._initialized = True
    
    def start_crawler(self, crawler_id: str, spider_name: str = "search", 
                     job_dir: str = "crawls/search", log_level: str = "DEBUG",
                     project_path: str = "crawler/weibo-search") -> Dict[str, Any]:
        """
        启动Scrapy爬虫
        
        Args:
            crawler_id: 爬虫唯一标识
            spider_name: 爬虫名称，默认为search
            job_dir: 工作目录，默认为crawls/search
            log_level: 日志级别，默认为DEBUG
            project_path: Scrapy项目路径，默认为crawler/weibo-search
            
        Returns:
            包含爬虫状态信息的字典
        """
        if crawler_id in self.active_crawlers:
            return {
                "success": False,
                "message": f"爬虫 {crawler_id} 已在运行中",
                "crawler_id": crawler_id
            }
        
        # 构建完整的项目路径
        full_project_path = os.path.abspath(project_path)
        
        # 检查项目路径是否存在
        if not os.path.exists(full_project_path):
            return {
                "success": False,
                "message": f"Scrapy项目路径不存在: {full_project_path}",
                "crawler_id": crawler_id
            }
        
        # 构建Scrapy命令
        scrapy_command = [
            "scrapy", "crawl", spider_name,
            "-s", f"JOBDIR={job_dir}",
            "-L", log_level
        ]
        
        try:
            # 启动Scrapy进程
            process = subprocess.Popen(
                scrapy_command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=full_project_path,
                shell=True  # 在Windows上需要shell=True
            )
            
            # 记录爬虫信息
            self.active_crawlers[crawler_id] = {
                "process": process,
                "start_time": datetime.now(),
                "spider_name": spider_name,
                "job_dir": job_dir,
                "log_level": log_level,
                "project_path": full_project_path,
                "pid": process.pid
            }
            
            # 启动监控线程
            monitor_thread = threading.Thread(
                target=self._monitor_crawler,
                args=(crawler_id, process)
            )
            monitor_thread.daemon = True
            monitor_thread.start()
            
            return {
                "success": True,
                "message": f"爬虫 {crawler_id} 启动成功",
                "crawler_id": crawler_id,
                "pid": process.pid,
                "start_time": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"启动爬虫失败: {str(e)}",
                "crawler_id": crawler_id
            }
    
    def stop_crawler(self, crawler_id: str) -> Dict[str, Any]:
        """
        停止指定的爬虫
        
        Args:
            crawler_id: 爬虫唯一标识
            
        Returns:
            包含停止状态信息的字典
        """
        if crawler_id not in self.active_crawlers:
            return {
                "success": False,
                "message": f"爬虫 {crawler_id} 未运行"
            }
        
        crawler_info = self.active_crawlers[crawler_id]
        process = crawler_info["process"]
        
        try:
            # 终止进程及其子进程
            parent = psutil.Process(process.pid)
            children = parent.children(recursive=True)
            
            # 先终止子进程
            for child in children:
                child.terminate()
            
            # 等待子进程终止
            gone, still_alive = psutil.wait_procs(children, timeout=5)
            
            # 如果还有存活的子进程，强制终止
            for child in still_alive:
                child.kill()
            
            # 终止父进程
            parent.terminate()
            parent.wait(timeout=5)
            
            # 清理记录
            del self.active_crawlers[crawler_id]
            
            return {
                "success": True,
                "message": f"爬虫 {crawler_id} 已停止",
                "crawler_id": crawler_id
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"停止爬虫失败: {str(e)}",
                "crawler_id": crawler_id
            }
    
    def _monitor_crawler(self, crawler_id: str, process):
        """监控爬虫进程状态"""
        try:
            # 等待进程结束
            stdout, stderr = process.communicate()
            
            # 记录爬虫结束状态
            self.crawler_status[crawler_id] = {
                "exit_code": process.returncode,
                "stdout": stdout,
                "stderr": stderr,
                "end_time": datetime.now(),
                "success": process.returncode == 0
            }
            
            # 清理活跃爬虫记录
            if crawler_id in self.active_crawlers:
                del self.active_crawlers[crawler_id]
                
        except Exception as e:
            # 记录异常状态
            self.crawler_status[crawler_id] = {
                "exit_code": -1,
                "error": str(e),
                "end_time": datetime.now(),
                "success": False
            }
            
            if crawler_id in self.active_crawlers:
                del self.active_crawlers[crawler_id]
    
    def get_status(self, crawler_id: str) -> Dict[str, Any]:
        """
        获取爬虫状态
        
        Args:
            crawler_id: 爬虫唯一标识
            
        Returns:
            包含爬虫状态信息的字典
        """
        if crawler_id in self.active_crawlers:
            crawler_info = self.active_crawlers[crawler_id]
            process = crawler_info["process"]
            
            # 检查进程是否仍在运行
            if process.poll() is None:
                return {
                    "status": "running",
                    "crawler_id": crawler_id,
                    "start_time": crawler_info["start_time"].isoformat(),
                    "running_time": str(datetime.now() - crawler_info["start_time"]),
                    "pid": process.pid,
                    "spider_name": crawler_info["spider_name"]
                }
            else:
                # 进程已结束，但还未被监控线程处理
                return {
                    "status": "completed",
                    "crawler_id": crawler_id,
                    "exit_code": process.returncode
                }
        
        elif crawler_id in self.crawler_status:
            status_info = self.crawler_status[crawler_id]
            return {
                "status": "completed" if status_info["success"] else "failed",
                "crawler_id": crawler_id,
                "exit_code": status_info.get("exit_code", -1),
                "end_time": status_info["end_time"].isoformat(),
                "success": status_info["success"]
            }
        
        else:
            return {
                "status": "not_found",
                "crawler_id": crawler_id,
                "message": "爬虫不存在"
            }
    
    def list_crawlers(self) -> Dict[str, Any]:
        """
        列出所有爬虫状态
        
        Returns:
            包含所有爬虫状态信息的字典
        """
        active_crawlers = {}
        for crawler_id, info in self.active_crawlers.items():
            process = info["process"]
            if process.poll() is None:
                active_crawlers[crawler_id] = {
                    "status": "running",
                    "start_time": info["start_time"].isoformat(),
                    "pid": process.pid,
                    "spider_name": info["spider_name"]
                }
        
        completed_crawlers = {}
        for crawler_id, info in self.crawler_status.items():
            completed_crawlers[crawler_id] = {
                "status": "completed" if info["success"] else "failed",
                "end_time": info["end_time"].isoformat(),
                "exit_code": info.get("exit_code", -1)
            }
        
        return {
            "active": active_crawlers,
            "completed": completed_crawlers,
            "total_active": len(active_crawlers),
            "total_completed": len(completed_crawlers)
        }
    
    def get_logs(self, crawler_id: str, lines: int = 100) -> Dict[str, Any]:
        """
        获取爬虫日志
        
        Args:
            crawler_id: 爬虫唯一标识
            lines: 返回的日志行数
            
        Returns:
            包含日志信息的字典
        """
        if crawler_id in self.crawler_status:
            status_info = self.crawler_status[crawler_id]
            stdout = status_info.get("stdout", "")
            stderr = status_info.get("stderr", "")
            
            # 获取最后几行日志
            stdout_lines = stdout.strip().split('\n')[-lines:]
            stderr_lines = stderr.strip().split('\n')[-lines:]
            
            return {
                "crawler_id": crawler_id,
                "stdout": '\n'.join(stdout_lines),
                "stderr": '\n'.join(stderr_lines),
                "has_stdout": bool(stdout.strip()),
                "has_stderr": bool(stderr.strip())
            }
        
        else:
            return {
                "crawler_id": crawler_id,
                "message": "未找到该爬虫的日志信息"
            }


# 使用示例
def main():
    """单例类使用示例"""
    # 获取单例实例
    crawler_manager = ScrapyCrawlerSingleton()
    
    # 启动爬虫
    result = crawler_manager.start_crawler(
        crawler_id="test_crawler_1",
        spider_name="search",
        job_dir="crawls/search",
        log_level="DEBUG"
    )
    
    print("启动结果:", result)
    
    # 等待几秒钟
    time.sleep(3)
    
    # 获取状态
    status = crawler_manager.get_status("test_crawler_1")
    print("爬虫状态:", status)
    
    # 列出所有爬虫
    all_crawlers = crawler_manager.list_crawlers()
    print("所有爬虫:", all_crawlers)
    
    # 停止爬虫
    stop_result = crawler_manager.stop_crawler("test_crawler_1")
    print("停止结果:", stop_result)


if __name__ == "__main__":
    main()