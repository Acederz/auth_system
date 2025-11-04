"""
异步任务管理器
用于跟踪文档生成任务的进度和状态
"""
import threading
import uuid
from datetime import datetime
from typing import Dict, Optional


class TaskManager:
    """单例任务管理器"""
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._tasks = {}
                    cls._instance._tasks_lock = threading.Lock()
        return cls._instance
    
    def create_task(self, task_type: str, total: int = 1) -> str:
        """
        创建新任务
        
        Args:
            task_type: 任务类型（word, pdf, word_batch, pdf_batch）
            total: 总数量
            
        Returns:
            task_id: 任务ID
        """
        task_id = str(uuid.uuid4())
        
        with self._tasks_lock:
            self._tasks[task_id] = {
                'task_id': task_id,
                'task_type': task_type,
                'status': 'pending',  # pending, running, completed, failed
                'progress': 0,
                'total': total,
                'current': 0,
                'message': '任务已创建',
                'result': None,
                'error': None,
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }
        
        return task_id
    
    def update_task(self, task_id: str, **kwargs):
        """
        更新任务信息
        
        Args:
            task_id: 任务ID
            **kwargs: 要更新的字段
        """
        with self._tasks_lock:
            if task_id in self._tasks:
                self._tasks[task_id].update(kwargs)
                self._tasks[task_id]['updated_at'] = datetime.now().isoformat()
                
                # 自动计算进度百分比
                if 'current' in kwargs or 'total' in kwargs:
                    current = self._tasks[task_id]['current']
                    total = self._tasks[task_id]['total']
                    if total > 0:
                        self._tasks[task_id]['progress'] = int((current / total) * 100)
    
    def get_task(self, task_id: str) -> Optional[Dict]:
        """
        获取任务信息
        
        Args:
            task_id: 任务ID
            
        Returns:
            任务信息字典，如果任务不存在返回 None
        """
        with self._tasks_lock:
            return self._tasks.get(task_id, None)
    
    def set_task_running(self, task_id: str, message: str = '正在处理...'):
        """设置任务为运行中"""
        self.update_task(task_id, status='running', message=message)
    
    def set_task_progress(self, task_id: str, current: int, message: str = None):
        """更新任务进度"""
        update_data = {'current': current}
        if message:
            update_data['message'] = message
        self.update_task(task_id, **update_data)
    
    def set_task_completed(self, task_id: str, result=None, message: str = '任务完成'):
        """设置任务为完成"""
        self.update_task(
            task_id,
            status='completed',
            progress=100,
            current=self._tasks[task_id]['total'],
            message=message,
            result=result
        )
    
    def set_task_failed(self, task_id: str, error: str):
        """设置任务为失败"""
        self.update_task(
            task_id,
            status='failed',
            message=f'任务失败: {error}',
            error=error
        )
    
    def cleanup_old_tasks(self, hours: int = 24):
        """
        清理旧任务
        
        Args:
            hours: 清理多少小时前的任务
        """
        from datetime import timedelta
        
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        with self._tasks_lock:
            task_ids_to_remove = []
            
            for task_id, task_info in self._tasks.items():
                updated_at = datetime.fromisoformat(task_info['updated_at'])
                if updated_at < cutoff_time:
                    task_ids_to_remove.append(task_id)
            
            for task_id in task_ids_to_remove:
                del self._tasks[task_id]
        
        return len(task_ids_to_remove)


# 全局任务管理器实例
task_manager = TaskManager()

