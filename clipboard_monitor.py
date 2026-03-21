"""
剪贴板监听模块 - 监听剪贴板变化
"""
import threading
import time
import pyperclip
from typing import Callable, Optional


class ClipboardMonitor:
    """剪贴板监听器"""
    
    def __init__(self, callback: Callable, polling_interval: float = 0.5):
        """
        Args:
            callback: 当剪贴板内容变化时的回调函数
            polling_interval: 轮询间隔（秒）
        """
        self.callback = callback
        self.polling_interval = polling_interval
        self.running = False
        self.last_clipboard = ""
        self.monitor_thread = None
        
    def start(self):
        """启动剪贴板监听"""
        if not self.running:
            self.running = True
            self.last_clipboard = self._get_clipboard_text()
            self.monitor_thread = threading.Thread(
                target=self._monitor_loop,
                daemon=True
            )
            self.monitor_thread.start()
            print("剪贴板监听已启动")
    
    def stop(self):
        """停止剪贴板监听"""
        self.running = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=2)
        print("剪贴板监听已停止")
    
    def _monitor_loop(self):
        """监听循环"""
        while self.running:
            try:
                current_clipboard = self._get_clipboard_text()
                
                # 如果内容变化了
                if current_clipboard != self.last_clipboard:
                    self.last_clipboard = current_clipboard
                    
                    # 执行回调
                    if current_clipboard.strip():  # 只在非空时触发
                        self.callback(current_clipboard)
                
                time.sleep(self.polling_interval)
                
            except Exception as e:
                print(f"剪贴板监听出错: {e}")
                time.sleep(self.polling_interval)
    
    def _get_clipboard_text(self) -> str:
        """获取剪贴板中的文本"""
        try:
            return pyperclip.paste()
        except Exception as e:
            print(f"获取剪贴板失败: {e}")
            return ""
    
    def get_current_clipboard(self) -> str:
        """获取当前剪贴板内容"""
        return self._get_clipboard_text()
    
    def set_clipboard(self, text: str):
        """设置剪贴板内容"""
        try:
            pyperclip.copy(text)
        except Exception as e:
            print(f"设置剪贴板失败: {e}")


if __name__ == '__main__':
    def on_clipboard_change(text):
        print(f"剪贴板内容变化: {text[:50]}")
    
    monitor = ClipboardMonitor(on_clipboard_change)
    monitor.start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        monitor.stop()
        print("\n监听已停止")
