# 定时调度器 - 每日自动运行策略
import schedule
import time
import datetime
import pytz
from typing import Callable, Dict
import json


class DailyScheduler:
    """每日定时调度器"""
    
    def __init__(self, timezone: str = 'Asia/Shanghai'):
        """
        初始化调度器
        
        Args:
            timezone: 时区
        """
        self.timezone = pytz.timezone(timezone)
        self.jobs = {}
        self.execution_log = "scheduler_execution.json"
    
    def schedule_daily_job(self, job_name: str, time_str: str, 
                          job_func: Callable, *args, **kwargs):
        """
        安排每日定时任务
        
        Args:
            job_name: 任务名称
            time_str: 执行时间，格式 "HH:MM" (24小时制)
            job_func: 要执行的函数
            *args, **kwargs: 传递给函数的参数
        """
        def wrapper():
            try:
                print(f"[{datetime.datetime.now()}] 开始执行任务: {job_name}")
                result = job_func(*args, **kwargs)
                self._log_execution(job_name, "成功", result)
                print(f"[{datetime.datetime.now()}] 任务完成: {job_name}")
                return result
            except Exception as e:
                error_msg = str(e)
                print(f"[{datetime.datetime.now()}] 任务失败: {job_name} - {error_msg}")
                self._log_execution(job_name, "失败", error_msg)
                raise
        
        job = schedule.every().day.at(time_str).do(wrapper)
        self.jobs[job_name] = job
        print(f"✓ 已安排任务: {job_name} 在每天 {time_str} 执行")
    
    def _log_execution(self, job_name: str, status: str, details: str = ""):
        """记录任务执行"""
        log_entry = {
            'timestamp': datetime.datetime.now().isoformat(),
            'job_name': job_name,
            'status': status,
            'details': str(details)[:200]  # 限制长度
        }
        
        logs = []
        try:
            with open(self.execution_log, 'r', encoding='utf-8') as f:
                logs = json.load(f)
        except:
            logs = []
        
        logs.append(log_entry)
        
        # 只保留最近1000条日志
        logs = logs[-1000:]
        
        with open(self.execution_log, 'w', encoding='utf-8') as f:
            json.dump(logs, f, ensure_ascii=False, indent=2)
    
    def start(self):
        """
        启动调度器（阻塞式）
        这会一直运行直到被中断
        """
        print("=" * 60)
        print("📅 定时调度器已启动")
        print("=" * 60)
        
        while True:
            schedule.run_pending()
            time.sleep(60)  # 每60秒检查一次是否有任务需要执行
    
    def start_background(self):
        """
        启动调度器（后台进程）
        需要配合线程或多进程使用
        """
        import threading
        
        scheduler_thread = threading.Thread(target=self._background_run, daemon=True)
        scheduler_thread.start()
        print("📅 后台调度器已启动")
    
    def _background_run(self):
        """后台运行"""
        while True:
            schedule.run_pending()
            time.sleep(60)


# 便捷函数 - 用于在你的程序中快速集成

def create_scheduler():
    """创建调度器实例"""
    return DailyScheduler(timezone='Asia/Shanghai')


def schedule_monitor_task(scheduler: DailyScheduler, monitor_func: Callable):
    """
    安排monitor程序的每日执行
    
    Args:
        scheduler: DailyScheduler实例
        monitor_func: 你的monitor.py中的main函数或关键函数
    """
    scheduler.schedule_daily_job(
        job_name="每日14:30 Monitor任务",
        time_str="14:30",
        job_func=monitor_func
    )


if __name__ == "__main__":
    # 示例用法
    scheduler = create_scheduler()
    
    # 示例：定义你的monitor函数
    def my_monitor_task():
        print("执行monitor任务...")
        # 这里会调用你的实际monitor逻辑
        return {"status": "success"}
    
    # 安排任务
    schedule_monitor_task(scheduler, my_monitor_task)
    
    # 启动调度器
    scheduler.start()
