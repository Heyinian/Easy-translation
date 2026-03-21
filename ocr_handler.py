"""
OCR模块 - 处理截图和文字识别
"""
import importlib.util
import os
import pkgutil
from datetime import datetime
from typing import Optional

from PIL import ImageGrab, ImageDraw

import config
from config import SCREENSHOT_DIR

if not hasattr(pkgutil, 'find_loader'):
    def _find_loader(name):
        return importlib.util.find_spec(name)

    pkgutil.find_loader = _find_loader

import pytesseract


def configure_tesseract() -> bool:
    """根据当前配置更新 Tesseract 可执行文件路径。"""
    tesseract_path = config.TESSERACT_PATH
    if os.path.exists(tesseract_path):
        pytesseract.pytesseract.pytesseract_cmd = tesseract_path
        return True
    return False


configure_tesseract()


class ScreenshotHandler:
    """截图处理类"""
    
    @staticmethod
    def take_screenshot() -> Optional[str]:
        """
        获取全屏截图并保存
        返回截图文件路径
        """
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            screenshot_path = SCREENSHOT_DIR / f"screenshot_{timestamp}.png"
            
            # 获取全屏并保存
            screenshot = ImageGrab.grab()
            screenshot.save(screenshot_path)
            
            print(f"截图已保存: {screenshot_path}")
            return str(screenshot_path)
            
        except Exception as e:
            print(f"截图失败: {e}")
            return None
    
    @staticmethod
    def take_region_screenshot(x1: int, y1: int, x2: int, y2: int) -> Optional[str]:
        """
        获取指定区域的截图
        """
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            screenshot_path = SCREENSHOT_DIR / f"region_{timestamp}.png"
            
            # 获取指定区域
            region = ImageGrab.grab(bbox=(x1, y1, x2, y2))
            region.save(screenshot_path)
            
            return str(screenshot_path)
            
        except Exception as e:
            print(f"区域截图失败: {e}")
            return None


class OCRHandler:
    """OCR处理类 - 识别图像中的文字"""
    
    @staticmethod
    def recognize_text_from_image(image_path: str, language: str = 'chi_sim+eng') -> Optional[str]:
        """
        从图像识别文本
        
        Args:
            image_path: 图像文件路径
            language: Tesseract语言包（'chi_sim'简体中文，'eng'英文）
            
        Returns:
            识别出的文本，失败返回None
        """
        try:
            if not os.path.exists(image_path):
                print(f"图像文件不存在: {image_path}")
                return None

            configure_tesseract()
            
            # 使用Tesseract识别
            text = pytesseract.image_to_string(image_path, lang=language)
            
            if text.strip():
                return text.strip()
            else:
                print("未识别到文字")
                return None
                
        except pytesseract.TesseractNotFoundError:
            print("未找到Tesseract。请从以下地址安装：")
            print("https://github.com/UB-Mannheim/tesseract/wiki")
            return None
            
        except Exception as e:
            print(f"OCR识别失败: {e}")
            return None
    
    @staticmethod
    def recognize_from_clipboard() -> Optional[str]:
        """
        从剪贴板中的图像识别文本（如果是图像的话）
        """
        try:
            from PIL import ImageGrab
            configure_tesseract()
            
            # 尝试从剪贴板获取图像
            image = ImageGrab.grabclipboard()
            
            if image is None:
                print("剪贴板中没有图像")
                return None
            
            # 临时保存图像
            temp_path = SCREENSHOT_DIR / "temp_clipboard.png"
            image.save(temp_path)
            
            # 识别文本
            text = pytesseract.image_to_string(str(temp_path))
            
            # 清理临时文件
            temp_path.unlink()
            
            return text.strip() if text.strip() else None
            
        except Exception as e:
            print(f"从剪贴板识别失败: {e}")
            return None


class InteractiveScreenshot:
    """交互式截图选择类"""
    
    def __init__(self):
        self.start_point = None
        self.end_point = None
        self.screenshot = None
        
    def show_selection_tool(self) -> Optional[str]:
        """
        显示截图选择工具
        用户可以拖拽选择要截图的区域
        （实现需要使用PyQt）
        """
        # 这个功能在main_window.py中实现
        pass


if __name__ == '__main__':
    # 测试截图
    path = ScreenshotHandler.take_screenshot()
    if path:
        print(f"截图路径: {path}")
        
        # 测试OCR（需要装好依赖）
        text = OCRHandler.recognize_text_from_image(path)
        if text:
            print(f"识别结果: {text[:100]}")
