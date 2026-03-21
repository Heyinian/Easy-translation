"""
快捷键和事件监听模块
"""
import threading
import time
from typing import Callable, Dict, List, Tuple

from pynput import keyboard
from pynput.keyboard import Key, Listener


SPECIAL_KEYS = {
    'alt': {Key.alt, Key.alt_l, Key.alt_r},
    'shift': {Key.shift, Key.shift_l, Key.shift_r},
    'ctrl': {Key.ctrl, Key.ctrl_l, Key.ctrl_r},
    'space': {Key.space},
    'enter': {Key.enter},
    'tab': {Key.tab},
    'esc': {Key.esc},
    'backspace': {Key.backspace},
}

for index in range(1, 13):
    SPECIAL_KEYS[f'f{index}'] = {getattr(Key, f'f{index}')}

class HotkeyManager:
    """全局快捷键管理器"""
    
    def __init__(self):
        self.hotkey_callbacks: Dict[str, Tuple[Callable, List[str]]] = {}
        self.listener = None
        self.running = False
        self.pressed_keys = set()
        self.active_hotkeys = set()
        
    def register_hotkey(self, hotkey_name: str, callback: Callable, hotkey_value: str):
        """
        注册一个热键回调函数
        
        Args:
            hotkey_name: 热键名称（如'screenshot', 'clipboard'）
            callback: 回调函数
        """
        parsed_hotkey = self._parse_hotkey(hotkey_value)
        self.hotkey_callbacks[hotkey_name] = (callback, parsed_hotkey)
        print(f"已注册热键: {hotkey_name} -> {hotkey_value}")
    
    def start(self):
        """启动全局热键监听"""
        if not self.running:
            self.running = True
            self.listener = Listener(
                on_press=self._on_key_press,
                on_release=self._on_key_release
            )
            self.listener.start()
            print("热键监听已启动")
    
    def stop(self):
        """停止热键监听"""
        if self.running:
            self.running = False
            if self.listener:
                self.listener.stop()
            print("热键监听已停止")
    
    def _on_key_press(self, key):
        """按键按下回调"""
        try:
            self.pressed_keys.add(key)

            for hotkey_name, (_, hotkey_keys) in self.hotkey_callbacks.items():
                if hotkey_name in self.active_hotkeys:
                    continue
                if self._check_hotkey(hotkey_keys):
                    self.active_hotkeys.add(hotkey_name)
                    self._trigger_callback(hotkey_name)
                
        except AttributeError:
            pass
    
    def _on_key_release(self, key):
        """按键释放回调"""
        try:
            self.pressed_keys.discard(key)
            self.active_hotkeys.clear()
        except AttributeError:
            pass

    def _parse_hotkey(self, hotkey_value: str) -> List[str]:
        return [part.strip().lower() for part in hotkey_value.split('+') if part.strip()]
    
    def _check_hotkey(self, key_combination: list) -> bool:
        """检查是否按下了指定的按键组合"""
        required_keys = {key_str.lower() for key_str in key_combination}
        pressed = set()
        for key in self.pressed_keys:
            for key_name, key_variants in SPECIAL_KEYS.items():
                if key in key_variants:
                    pressed.add(key_name)

            try:
                if key.char:
                    pressed.add(key.char.lower())
            except AttributeError:
                pass
        
        return required_keys.issubset(pressed)
    
    def _trigger_callback(self, hotkey_name: str):
        """触发注册的回调函数"""
        if hotkey_name in self.hotkey_callbacks:
            callback = self.hotkey_callbacks[hotkey_name][0]
            # 在后台线程执行，避免阻塞
            threading.Thread(target=callback, daemon=True).start()


class TripleClickDetector:
    """三击空格检测器"""
    
    def __init__(self, callback: Callable, time_window: float = 0.5):
        """
        Args:
            callback: 三击时的回调函数
            time_window: 时间窗口（秒），用于判断是否为连续三击
        """
        self.callback = callback
        self.time_window = time_window
        self.click_times = []
        self.listener = None
        self.running = False
        
    def start(self):
        """启动检测器"""
        if not self.running:
            self.running = True
            self.listener = Listener(on_press=self._on_key_press)
            self.listener.start()
            print("三击空格检测已启动")
    
    def stop(self):
        """停止检测器"""
        if self.running:
            self.running = False
            if self.listener:
                self.listener.stop()
    
    def _on_key_press(self, key):
        """检测空格键按下"""
        try:
            if key == Key.space:
                current_time = time.time()
                
                # 移除超出时间窗口的点击
                self.click_times = [
                    t for t in self.click_times 
                    if current_time - t < self.time_window
                ]
                
                self.click_times.append(current_time)
                
                # 如果累计三次点击，触发回调
                if len(self.click_times) >= 3:
                    self.click_times = []  # 重置
                    threading.Thread(target=self.callback, daemon=True).start()
                    
        except AttributeError:
            pass


if __name__ == '__main__':
    # 测试快捷键
    def on_screenshot():
        print("触发截图热键")
    
    def on_clipboard():
        print("触发复制热键")
    
    def on_triple_click():
        print("三击空格检测!")
    
    manager = HotkeyManager()
    manager.register_hotkey('screenshot', on_screenshot, 'alt+shift+s')
    manager.register_hotkey('clipboard', on_clipboard, 'alt+shift+c')
    manager.start()
    
    detector = TripleClickDetector(on_triple_click)
    detector.start()
    
    try:
        while True:
            time.sleep(0.1)
    except KeyboardInterrupt:
        manager.stop()
        detector.stop()
        print("\n监听已停止")
