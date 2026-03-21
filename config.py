"""
配置文件 - 存放应用的全局配置和常量
"""
from copy import deepcopy
from pathlib import Path

from settings_manager import settings_manager

# 项目根目录
PROJECT_ROOT = Path(__file__).parent
ASSETS_DIR = PROJECT_ROOT / 'assets'

# 应用基础信息
APP_NAME = 'Easy-translation'
APP_ID = 'EasyTranslation.EasyTranslation'
APP_INSTANCE_KEY = 'EasyTranslation.SingleInstance'
APP_ICON_PATH = ASSETS_DIR / 'easy-translation.ico'
APP_ICON_FALLBACK_PATH = ASSETS_DIR / 'easy-translation.png'

# 设置管理器
SETTINGS_MANAGER = settings_manager

# 翻译API配置
TRANSLATION_APIS = {
    'google': {
        'name': 'Google Translate',
        'url': 'https://translate.googleapis.com/element.js',
        'free': True
    },
    'baidu': {
        'name': '百度翻译',
        'url': 'https://api.fanyi.baidu.com/api/trans/vip/translate',
        'requires_key': True
    },
    'tencent': {
        'name': '腾讯翻译',
        'url': 'https://tmt.tencentcloudapi.com',
        'requires_key': True
    },
    'ollama': {
        'name': 'Ollama 本地 AI',
        'url': 'http://127.0.0.1:11434',
        'requires_key': False,
        'local': True
    }
}

# 默认API（可修改）
DEFAULT_API = 'google'

# 智能默认翻译模式
SMART_TARGET_LANG = '__smart__'
SMART_TARGET_LABEL = '默认模式（中->英，英->中）'

# 支持的语言对
LANGUAGE_PAIRS = {
    'zh': '中文',
    'en': '英文',
    'ja': '日文',
    'ko': '韩文',
    'fr': '法文',
    'de': '德文',
    'es': '西班牙文',
    'ru': '俄文',
}

# 截图保存路径
SCREENSHOT_DIR = PROJECT_ROOT / 'screenshots'
SCREENSHOT_DIR.mkdir(exist_ok=True)

# OCR配置（Tesseract）
# Windows上需要先安装Tesseract: https://github.com/UB-Mannheim/tesseract/wiki
TESSERACT_PATH = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# 快捷键配置
HOTKEYS = {
    'screenshot': 'alt+shift+s',      # 截图翻译
    'clipboard': 'alt+shift+c',       # 复制翻译
    'show_window': 'alt+shift+t',     # 显示应用窗口
    'translate_input': 'triple_space', # 翻译当前输入框/选中文本
}

# UI配置
WINDOW_WIDTH = 600
WINDOW_HEIGHT = 400
WINDOW_TITLE = APP_NAME

# 日志配置
LOG_DIR = PROJECT_ROOT / 'logs'
LOG_DIR.mkdir(exist_ok=True)
LOG_LEVEL = 'INFO'


def _apply_user_settings() -> dict:
    settings = SETTINGS_MANAGER.reload_settings()

    global DEFAULT_API, HOTKEYS, TESSERACT_PATH
    DEFAULT_API = settings.get('default_api', DEFAULT_API)
    HOTKEYS = deepcopy(settings.get('hotkeys', HOTKEYS))
    TESSERACT_PATH = settings.get('tesseract_path', TESSERACT_PATH)

    return settings


USER_SETTINGS = _apply_user_settings()


def reload_config() -> dict:
    """重新加载用户配置，并更新运行时常量。"""
    global USER_SETTINGS
    USER_SETTINGS = _apply_user_settings()
    return deepcopy(USER_SETTINGS)


def get_api_credentials(provider: str) -> dict:
    """读取指定翻译源的 API 凭证。"""
    return SETTINGS_MANAGER.get_api_credentials(provider)


def get_provider_settings(provider: str) -> dict:
    """读取指定翻译源的非密钥配置。"""
    return SETTINGS_MANAGER.get_provider_settings(provider)
