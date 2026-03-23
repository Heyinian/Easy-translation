"""
主应用窗口 - PyQt6 UI
"""
import ctypes
import logging
import os
import sys
import time
from pathlib import Path

import pyperclip

def _configure_qt_dll_path():
    if not hasattr(os, 'add_dll_directory'):
        return

    qt_bin_path = Path(sys.prefix) / 'Lib' / 'site-packages' / 'PyQt6' / 'Qt6' / 'bin'
    if qt_bin_path.exists():
        os.add_dll_directory(str(qt_bin_path))


_configure_qt_dll_path()

import config
from PyQt6.QtCore import QEvent, QObject, QThread, QTimer, pyqtSignal
from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtNetwork import QLocalServer, QLocalSocket
from PyQt6.QtWidgets import (
    QApplication, QCheckBox, QComboBox, QDialog, QDialogButtonBox,
    QFormLayout, QHBoxLayout, QLabel, QLineEdit,
    QMainWindow, QMenu, QMessageBox, QPushButton, QSystemTrayIcon, QTextEdit,
    QVBoxLayout, QWidget
)
from pynput.keyboard import Controller as KeyboardController, Key

from config import (
    APP_ICON_FALLBACK_PATH,
    APP_ICON_PATH,
    APP_ID,
    APP_INSTANCE_KEY,
    APP_NAME,
    LANGUAGE_PAIRS,
    SMART_TARGET_LABEL,
    SMART_TARGET_LANG,
    TRANSLATION_APIS,
    WINDOW_HEIGHT,
    WINDOW_TITLE,
    WINDOW_WIDTH,
)
from hotkey_manager import HotkeyManager, TripleClickDetector
from clipboard_monitor import ClipboardMonitor
from ocr_handler import OCRHandler, ScreenshotHandler, configure_tesseract
from settings_manager import settings_manager
from translator_core import TranslatorCore


TRIPLE_SPACE_TRIGGER = 'triple_space'
TRIPLE_SPACE_LOGGER = logging.getLogger('easy_translation.triple_space')


def load_app_icon() -> QIcon:
    """加载应用图标，优先使用 ICO，不存在时回退 PNG。"""
    for icon_path in (APP_ICON_PATH, APP_ICON_FALLBACK_PATH):
        if Path(icon_path).exists():
            return QIcon(str(icon_path))
    return QIcon()


def set_windows_app_id():
    """设置 Windows AppUserModelID，确保任务栏图标和名称稳定。"""
    if os.name != 'nt':
        return

    try:
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(APP_ID)
    except Exception:
        pass


class SettingsDialog(QDialog):
    """应用设置对话框。"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('设置')
        if parent is not None and hasattr(parent, 'app_icon') and not parent.app_icon.isNull():
            self.setWindowIcon(parent.app_icon)
        self.setMinimumWidth(520)
        self.settings = settings_manager.get_all_settings()
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        help_label = QLabel('Google 无需密钥；百度和腾讯需要先填写对应凭证。输入框翻译触发键可填写 triple_space 或组合键，例如 alt+shift+x。')
        help_label.setWordWrap(True)
        layout.addWidget(help_label)

        form_layout = QFormLayout()

        self.default_api_combo = QComboBox()
        for api_code, api_info in TRANSLATION_APIS.items():
            self.default_api_combo.addItem(api_info['name'], api_code)
        self._set_combo_value(self.default_api_combo, self.settings.get('default_api', 'google'))
        form_layout.addRow('默认翻译源:', self.default_api_combo)

        self.source_lang_combo = QComboBox()
        self.source_lang_combo.addItem('自动检测', 'auto')
        for code, name in LANGUAGE_PAIRS.items():
            self.source_lang_combo.addItem(name, code)
        self._set_combo_value(self.source_lang_combo, self.settings.get('source_lang', 'auto'))
        form_layout.addRow('默认源语言:', self.source_lang_combo)

        self.target_lang_combo = QComboBox()
        self.target_lang_combo.addItem(SMART_TARGET_LABEL, SMART_TARGET_LANG)
        for code, name in LANGUAGE_PAIRS.items():
            self.target_lang_combo.addItem(name, code)
        self._set_combo_value(self.target_lang_combo, self.settings.get('target_lang', SMART_TARGET_LANG))
        form_layout.addRow('默认目标语言:', self.target_lang_combo)

        self.ocr_lang_input = QLineEdit(self.settings.get('ocr_language', 'chi_sim+eng'))
        form_layout.addRow('OCR语言包:', self.ocr_lang_input)

        self.tesseract_path_input = QLineEdit(self.settings.get('tesseract_path', ''))
        form_layout.addRow('Tesseract路径:', self.tesseract_path_input)

        hotkeys = self.settings.get('hotkeys', {})
        self.hotkey_screenshot_input = QLineEdit(hotkeys.get('screenshot', 'alt+shift+s'))
        form_layout.addRow('截图热键:', self.hotkey_screenshot_input)

        self.hotkey_clipboard_input = QLineEdit(hotkeys.get('clipboard', 'alt+shift+c'))
        form_layout.addRow('剪贴板热键:', self.hotkey_clipboard_input)

        self.hotkey_window_input = QLineEdit(hotkeys.get('show_window', 'alt+shift+t'))
        form_layout.addRow('显示窗口热键:', self.hotkey_window_input)

        self.hotkey_translate_input = QLineEdit(hotkeys.get('translate_input', TRIPLE_SPACE_TRIGGER))
        form_layout.addRow('输入框翻译触发键:', self.hotkey_translate_input)

        self.translate_input_window_input = QLineEdit(str(self.settings.get('translate_input_time_window', 1.0)))
        form_layout.addRow('三击空格窗口期(秒):', self.translate_input_window_input)

        baidu_credentials = self.settings.get('api_keys', {}).get('baidu', {})
        self.baidu_app_id_input = QLineEdit(baidu_credentials.get('app_id', ''))
        form_layout.addRow('百度 App ID:', self.baidu_app_id_input)

        self.baidu_secret_key_input = QLineEdit(baidu_credentials.get('secret_key', ''))
        self.baidu_secret_key_input.setEchoMode(QLineEdit.EchoMode.Password)
        form_layout.addRow('百度 Secret Key:', self.baidu_secret_key_input)

        self.baidu_test_btn = QPushButton('测试百度配置')
        self.baidu_test_btn.clicked.connect(lambda: self.test_api_credentials('baidu'))
        form_layout.addRow('', self.baidu_test_btn)

        ollama_settings = self.settings.get('provider_settings', {}).get('ollama', {})
        self.ollama_base_url_input = QLineEdit(ollama_settings.get('base_url', 'http://127.0.0.1:11434'))
        form_layout.addRow('Ollama 地址:', self.ollama_base_url_input)

        self.ollama_model_input = QLineEdit(ollama_settings.get('model', 'qwen2.5:7b'))
        form_layout.addRow('Ollama 模型:', self.ollama_model_input)

        self.ollama_timeout_input = QLineEdit(str(ollama_settings.get('timeout', 20)))
        form_layout.addRow('Ollama 超时(秒):', self.ollama_timeout_input)

        self.ollama_test_btn = QPushButton('测试 Ollama 配置')
        self.ollama_test_btn.clicked.connect(lambda: self.test_provider_settings('ollama'))
        form_layout.addRow('', self.ollama_test_btn)

        tencent_credentials = self.settings.get('api_keys', {}).get('tencent', {})
        self.tencent_secret_id_input = QLineEdit(tencent_credentials.get('secret_id', ''))
        form_layout.addRow('腾讯 Secret ID:', self.tencent_secret_id_input)

        self.tencent_secret_key_input = QLineEdit(tencent_credentials.get('secret_key', ''))
        self.tencent_secret_key_input.setEchoMode(QLineEdit.EchoMode.Password)
        form_layout.addRow('腾讯 Secret Key:', self.tencent_secret_key_input)

        self.tencent_region_input = QLineEdit(tencent_credentials.get('region', 'ap-beijing'))
        form_layout.addRow('腾讯 Region:', self.tencent_region_input)

        self.tencent_test_btn = QPushButton('测试腾讯配置')
        self.tencent_test_btn.clicked.connect(lambda: self.test_api_credentials('tencent'))
        form_layout.addRow('', self.tencent_test_btn)

        self.clear_cache_btn = QPushButton('清理翻译缓存')
        self.clear_cache_btn.clicked.connect(self.clear_translation_cache)
        form_layout.addRow('', self.clear_cache_btn)

        layout.addLayout(form_layout)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _set_combo_value(self, combo: QComboBox, value: str):
        index = combo.findData(value)
        if index >= 0:
            combo.setCurrentIndex(index)

    def get_settings_data(self):
        settings = settings_manager.get_all_settings()
        settings['default_api'] = self.default_api_combo.currentData()
        current_api = settings.get('current_api', settings['default_api'])
        settings['current_api'] = current_api if current_api in TRANSLATION_APIS else settings['default_api']
        settings['source_lang'] = self.source_lang_combo.currentData()
        settings['target_lang'] = self.target_lang_combo.currentData()
        settings['ocr_language'] = self.ocr_lang_input.text().strip() or 'chi_sim+eng'
        settings['tesseract_path'] = self.tesseract_path_input.text().strip()
        settings['auto_clipboard_monitor'] = settings.get('auto_clipboard_monitor', True)
        settings['translate_input_time_window'] = self._parse_time_window(self.translate_input_window_input.text().strip())
        settings.setdefault('provider_settings', {})['ollama'] = {
            'base_url': self.ollama_base_url_input.text().strip() or 'http://127.0.0.1:11434',
            'model': self.ollama_model_input.text().strip() or 'qwen2.5:7b',
            'timeout': self._parse_timeout(self.ollama_timeout_input.text().strip()),
        }
        settings['hotkeys'] = {
            'screenshot': self.hotkey_screenshot_input.text().strip() or 'alt+shift+s',
            'clipboard': self.hotkey_clipboard_input.text().strip() or 'alt+shift+c',
            'show_window': self.hotkey_window_input.text().strip() or 'alt+shift+t',
            'translate_input': self.hotkey_translate_input.text().strip().lower() or TRIPLE_SPACE_TRIGGER,
        }
        settings['api_keys']['baidu'] = {
            'app_id': self.baidu_app_id_input.text().strip(),
            'secret_key': self.baidu_secret_key_input.text().strip(),
        }
        settings['api_keys']['tencent'] = {
            'secret_id': self.tencent_secret_id_input.text().strip(),
            'secret_key': self.tencent_secret_key_input.text().strip(),
            'region': self.tencent_region_input.text().strip() or 'ap-beijing',
        }
        return settings

    def _parse_timeout(self, value: str) -> int:
        try:
            return max(1, int(value))
        except (TypeError, ValueError):
            return 20

    def _parse_time_window(self, value: str) -> float:
        try:
            return max(0.3, min(3.0, float(value)))
        except (TypeError, ValueError):
            return 1.0

    def _get_provider_credentials(self, provider: str):
        if provider == 'baidu':
            return {
                'app_id': self.baidu_app_id_input.text().strip(),
                'secret_key': self.baidu_secret_key_input.text().strip(),
            }
        if provider == 'tencent':
            return {
                'secret_id': self.tencent_secret_id_input.text().strip(),
                'secret_key': self.tencent_secret_key_input.text().strip(),
                'region': self.tencent_region_input.text().strip() or 'ap-beijing',
            }
        return {}

    def test_api_credentials(self, provider: str):
        credentials = self._get_provider_credentials(provider)
        if not settings_manager.validate_api_credentials(provider, credentials):
            QMessageBox.warning(self, '配置测试', f'{provider} 配置未填写完整，无法测试')
            return

        translator = TranslatorCore(provider, credentials_override=credentials)
        result = translator.translate('hello', 'en', 'zh')
        if result:
            QMessageBox.information(self, '配置测试', f'{provider} 配置可用，测试结果: {result}')
            return

        QMessageBox.warning(self, '配置测试', translator.last_error or f'{provider} 配置测试失败')

    def test_provider_settings(self, provider: str):
        if provider != 'ollama':
            QMessageBox.warning(self, '配置测试', f'{provider} 暂无配置测试能力')
            return

        provider_settings = {
            'base_url': self.ollama_base_url_input.text().strip(),
            'model': self.ollama_model_input.text().strip(),
            'timeout': self._parse_timeout(self.ollama_timeout_input.text().strip()),
        }

        if not settings_manager.validate_provider_settings(provider, provider_settings):
            QMessageBox.warning(self, '配置测试', 'Ollama 地址或模型名称不能为空')
            return

        original_settings = settings_manager.get_provider_settings(provider)
        try:
            settings_manager.set_provider_settings(provider, provider_settings)
            translator = TranslatorCore(provider)
            result = translator.translate('你好，世界', 'zh', 'en')
            if result:
                QMessageBox.information(self, '配置测试', f'Ollama 配置可用，测试结果: {result}')
                return
            QMessageBox.warning(self, '配置测试', translator.last_error or 'Ollama 配置测试失败')
        finally:
            settings_manager.set_provider_settings(provider, original_settings)

    def clear_translation_cache(self):
        parent = self.parent()
        if parent and hasattr(parent, 'clear_translation_cache'):
            parent.clear_translation_cache(show_message=True)
            return
        QMessageBox.information(self, '缓存', '当前没有可清理的翻译缓存')

    def accept(self):
        settings = self.get_settings_data()
        validation_error = self._validate_settings(settings)
        if validation_error:
            QMessageBox.warning(self, '设置校验失败', validation_error)
            return
        super().accept()

    def _validate_settings(self, settings):
        hotkey_values = list(settings.get('hotkeys', {}).values())
        if len(set(hotkey_values)) != len(hotkey_values):
            return '热键不能重复，请为每个功能设置不同的快捷键'

        for hotkey_name, hotkey_value in settings.get('hotkeys', {}).items():
            if not self._is_valid_hotkey(hotkey_value):
                return f'{hotkey_name} 热键格式无效，请使用类似 alt+shift+s 的格式'

        selected_api = settings.get('default_api', 'google')
        if selected_api == 'baidu' and not settings_manager.validate_api_credentials('baidu', settings['api_keys']['baidu']):
            return '默认翻译源选择了百度翻译，但百度凭证未填写完整'

        if selected_api == 'tencent' and not settings_manager.validate_api_credentials('tencent', settings['api_keys']['tencent']):
            return '默认翻译源选择了腾讯翻译，但腾讯凭证未填写完整'

        if selected_api == 'ollama' and not settings_manager.validate_provider_settings('ollama', settings['provider_settings']['ollama']):
            return '默认翻译源选择了 Ollama，但服务地址或模型名称未填写完整'

        if not settings_manager.validate_translate_input_time_window(settings.get('translate_input_time_window', 1.0)):
            return '三击空格窗口期必须在 0.3 到 3.0 秒之间'

        return None

    def _is_valid_hotkey(self, hotkey_value: str) -> bool:
        if hotkey_value.strip().lower() == TRIPLE_SPACE_TRIGGER:
            return True

        allowed_tokens = {'alt', 'shift', 'ctrl'}
        allowed_final_keys = {'space', 'enter', 'tab', 'esc', 'backspace'}
        parts = [part.strip().lower() for part in hotkey_value.split('+') if part.strip()]
        if len(parts) < 2:
            return False

        for part in parts[:-1]:
            if part not in allowed_tokens:
                return False

        last_part = parts[-1]
        if len(last_part) == 1 and last_part.isalnum():
            return True
        if last_part in allowed_final_keys:
            return True
        if last_part.startswith('f') and last_part[1:].isdigit():
            key_number = int(last_part[1:])
            return 1 <= key_number <= 12
        return False


class TranslationWorker(QObject):
    """后台翻译工作线程"""
    
    result_ready = pyqtSignal(object)
    error_occurred = pyqtSignal(str)
    
    def __init__(self, text, source_lang, target_lang, api_type):
        super().__init__()
        self.text = text
        self.source_lang = source_lang
        self.target_lang = target_lang
        self.api_type = api_type
    
    def run(self):
        """执行翻译"""
        try:
            translator = TranslatorCore(self.api_type)
            result = translator.translate_result(
                self.text, 
                self.source_lang, 
                self.target_lang
            )
            
            if result:
                self.result_ready.emit(result)
            else:
                self.error_occurred.emit(translator.last_error or '翻译失败，请重试')
                
        except Exception as e:
            self.error_occurred.emit(f"出错: {str(e)}")


class SingleInstanceManager(QObject):
    """确保应用只保留一个运行实例。"""

    activate_requested = pyqtSignal()

    def __init__(self, server_name: str):
        super().__init__()
        self.server_name = server_name
        self.server = None
        self._is_primary_instance = False

    def start(self) -> bool:
        """尝试注册主实例；如果已有实例，则通知其显示窗口。"""
        socket = QLocalSocket(self)
        socket.connectToServer(self.server_name)
        if socket.waitForConnected(300):
            self._notify_existing_instance(socket)
            return False

        QLocalServer.removeServer(self.server_name)
        self.server = QLocalServer(self)
        if not self.server.listen(self.server_name):
            return False

        self.server.newConnection.connect(self._handle_new_connection)
        self._is_primary_instance = True
        return True

    def _notify_existing_instance(self, socket: QLocalSocket):
        socket.write(b'SHOW')
        socket.flush()
        socket.waitForBytesWritten(300)
        socket.disconnectFromServer()

    def _handle_new_connection(self):
        if not self.server:
            return

        while self.server.hasPendingConnections():
            socket = self.server.nextPendingConnection()
            if socket is None:
                continue

            socket.readyRead.connect(
                lambda connection=socket: self._read_activation_request(connection)
            )
            socket.disconnected.connect(socket.deleteLater)

    def _read_activation_request(self, socket: QLocalSocket):
        payload = bytes(socket.readAll()).decode('utf-8', errors='ignore').strip().upper()
        if payload == 'SHOW':
            self.activate_requested.emit()
        socket.disconnectFromServer()

    def cleanup(self):
        if self.server and self._is_primary_instance:
            self.server.close()
            QLocalServer.removeServer(self.server_name)


class MainWindow(QMainWindow):
    """主应用窗口"""

    screenshot_requested = pyqtSignal()
    clipboard_translate_requested = pyqtSignal()
    show_window_requested = pyqtSignal()
    translate_input_requested = pyqtSignal()
    clipboard_text_received = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.runtime_settings = config.reload_config()
        self.translator = TranslatorCore(self.runtime_settings.get('default_api', config.DEFAULT_API))
        self.hotkey_manager = HotkeyManager()
        self.screenshot_requested.connect(self.on_screenshot_clicked)
        self.clipboard_translate_requested.connect(self.on_clipboard_translate)
        self.show_window_requested.connect(self.show_window)
        self.translate_input_requested.connect(self.on_global_translate_triggered)
        self.clipboard_text_received.connect(self.on_clipboard_change)
        self.clipboard_monitor = ClipboardMonitor(self.clipboard_text_received.emit)
        self.triple_click_detector = None
        self.keyboard_controller = KeyboardController()
        self.translation_thread = None
        self.translation_worker = None
        self._active_translation_threads = []
        self._is_applying_settings = False
        self._clipboard_capture_in_progress = False
        self._pending_external_replace = False
        self._pending_clipboard_restore = None
        self.app_icon = load_app_icon()
        self._is_quitting = False
        self._tray_background_tip_shown = False
        
        self.init_ui()
        self.apply_runtime_settings_to_ui()
        self.setup_hotkeys()
        self.start_monitors()
    
    def init_ui(self):
        """初始化UI"""
        self.setWindowTitle(WINDOW_TITLE)
        if not self.app_icon.isNull():
            self.setWindowIcon(self.app_icon)
        self.resize(WINDOW_WIDTH, WINDOW_HEIGHT)
        screen = QApplication.primaryScreen().geometry()
        self.move(
            (screen.width() - WINDOW_WIDTH) // 2,
            (screen.height() - WINDOW_HEIGHT) // 2,
        )

        # 中央窗口
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout()
        
        # ===== 语言选择区域 =====
        lang_layout = QHBoxLayout()

        lang_layout.addWidget(QLabel("翻译源:"))
        self.api_combo = QComboBox()
        for api_code, api_info in TRANSLATION_APIS.items():
            self.api_combo.addItem(api_info['name'], api_code)
        self.api_combo.currentIndexChanged.connect(self.on_api_changed)
        lang_layout.addWidget(self.api_combo)

        lang_layout.addSpacing(20)
        
        lang_layout.addWidget(QLabel("源语言:"))
        self.source_lang_combo = QComboBox()
        self.source_lang_combo.addItem("自动检测", "auto")
        for code, name in LANGUAGE_PAIRS.items():
            self.source_lang_combo.addItem(name, code)
        self.source_lang_combo.setCurrentText("自动检测")
        lang_layout.addWidget(self.source_lang_combo)
        
        lang_layout.addSpacing(20)
        
        lang_layout.addWidget(QLabel("目标语言:"))
        self.target_lang_combo = QComboBox()
        self.target_lang_combo.addItem(SMART_TARGET_LABEL, SMART_TARGET_LANG)
        for code, name in LANGUAGE_PAIRS.items():
            self.target_lang_combo.addItem(name, code)
        self.target_lang_combo.setCurrentIndex(0)
        lang_layout.addWidget(self.target_lang_combo)
        
        main_layout.addLayout(lang_layout)
        
        # ===== 输入区域 =====
        main_layout.addWidget(QLabel("输入文本:"))
        self.input_text = QTextEdit()
        self.input_text.setPlaceholderText(
            "在此输入要翻译的文本，或使用快捷键热键:\n"
            "Alt+Shift+S - 截图翻译\n"
            "Alt+Shift+C - 复制翻译\n"
            "连续按3次空格 - 翻译输入框内容"
        )
        self.input_text.setMinimumHeight(100)
        main_layout.addWidget(self.input_text)
        
        # ===== 输出区域 =====
        main_layout.addWidget(QLabel("翻译结果:"))
        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        self.output_text.setMinimumHeight(100)
        main_layout.addWidget(self.output_text)

        self.status_label = QLabel('当前翻译源: Google Translate')
        main_layout.addWidget(self.status_label)
        
        # ===== 按钮区域 =====
        button_layout = QHBoxLayout()
        
        self.translate_btn = QPushButton("翻译")
        self.translate_btn.clicked.connect(self.do_translation)
        button_layout.addWidget(self.translate_btn)
        
        self.screenshot_btn = QPushButton("🖼️ 截图翻译")
        self.screenshot_btn.clicked.connect(self.on_screenshot_clicked)
        button_layout.addWidget(self.screenshot_btn)
        
        self.copy_btn = QPushButton("📋 由剪贴板翻译")
        self.copy_btn.clicked.connect(self.on_clipboard_translate)
        button_layout.addWidget(self.copy_btn)
        
        self.clear_btn = QPushButton("清空")
        self.clear_btn.clicked.connect(self.clear_texts)
        button_layout.addWidget(self.clear_btn)

        self.settings_btn = QPushButton("设置")
        self.settings_btn.clicked.connect(self.open_settings_dialog)
        button_layout.addWidget(self.settings_btn)
        
        main_layout.addLayout(button_layout)
        
        # ===== 配置区域 =====
        self.auto_monitor_checkbox = QCheckBox("自动监听剪贴板")
        self.auto_monitor_checkbox.setChecked(True)
        self.auto_monitor_checkbox.stateChanged.connect(self.on_auto_monitor_changed)
        main_layout.addWidget(self.auto_monitor_checkbox)
        
        central_widget.setLayout(main_layout)
        
        # ===== 托盘图标 =====
        self.setup_tray()
    
    def setup_tray(self):
        """设置系统托盘"""
        self.tray_icon = QSystemTrayIcon(self)
        if not self.app_icon.isNull():
            self.tray_icon.setIcon(self.app_icon)
        self.tray_icon.setToolTip(f'{APP_NAME} - 后台运行中')
        
        tray_menu = QMenu()

        status_action = QAction(f"{APP_NAME} 正在后台运行", self)
        status_action.setEnabled(False)
        tray_menu.addAction(status_action)
        tray_menu.addSeparator()
        
        show_action = QAction("打开主界面", self)
        show_action.triggered.connect(self.show_window)
        tray_menu.addAction(show_action)

        clipboard_action = QAction("翻译当前剪贴板", self)
        clipboard_action.triggered.connect(self.on_clipboard_translate)
        tray_menu.addAction(clipboard_action)

        settings_action = QAction("设置", self)
        settings_action.triggered.connect(self.open_settings_from_tray)
        tray_menu.addAction(settings_action)
        
        tray_menu.addSeparator()
        
        exit_action = QAction("退出应用", self)
        exit_action.triggered.connect(self.quit_app)
        tray_menu.addAction(exit_action)
        
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()
        
        self.tray_icon.activated.connect(self.tray_icon_activated)
    
    def tray_icon_activated(self, reason):
        """托盘图标被点击"""
        if reason in (
            QSystemTrayIcon.ActivationReason.Trigger,
            QSystemTrayIcon.ActivationReason.DoubleClick,
        ):
            self.show_window()

    def _show_background_running_tip(self):
        if self._tray_background_tip_shown or not self.tray_icon.isVisible():
            return

        self.tray_icon.showMessage(
            APP_NAME,
            '应用已切换到后台运行，可通过托盘图标打开主界面、设置或退出应用。',
            QSystemTrayIcon.MessageIcon.Information,
            3000,
        )
        self._tray_background_tip_shown = True

    def minimize_to_tray(self):
        """隐藏窗口并保留托盘图标。"""
        self.hide()
        self._show_background_running_tip()
    
    def setup_hotkeys(self):
        """设置全局快捷键"""
        hotkeys = config.HOTKEYS
        self.hotkey_manager.register_hotkey('screenshot', self.screenshot_requested.emit, hotkeys['screenshot'])
        self.hotkey_manager.register_hotkey('clipboard', self.clipboard_translate_requested.emit, hotkeys['clipboard'])
        self.hotkey_manager.register_hotkey('show_window', self.show_window_requested.emit, hotkeys['show_window'])
        if hotkeys.get('translate_input', TRIPLE_SPACE_TRIGGER) != TRIPLE_SPACE_TRIGGER:
            self.hotkey_manager.register_hotkey('translate_input', self.translate_input_requested.emit, hotkeys['translate_input'])
        self.hotkey_manager.start()
        self._restart_translate_input_detector()

    def _restart_translate_input_detector(self):
        if self.triple_click_detector:
            self.triple_click_detector.stop()
            self.triple_click_detector = None

        trigger_value = config.HOTKEYS.get('translate_input', TRIPLE_SPACE_TRIGGER)
        if trigger_value == TRIPLE_SPACE_TRIGGER:
            time_window = float(self.runtime_settings.get('translate_input_time_window', 1.0))
            self.triple_click_detector = TripleClickDetector(self.translate_input_requested.emit, time_window=time_window)
            self.triple_click_detector.start()

    def restart_hotkeys(self):
        """重启热键监听以应用新配置。"""
        self.hotkey_manager.stop()
        self.hotkey_manager = HotkeyManager()
        self.setup_hotkeys()

    def _format_translate_input_trigger_label(self) -> str:
        trigger_value = config.HOTKEYS.get('translate_input', TRIPLE_SPACE_TRIGGER)
        if trigger_value == TRIPLE_SPACE_TRIGGER:
            time_window = self.runtime_settings.get('translate_input_time_window', 1.0)
            return f'连续按3次空格({time_window}秒内)'
        return trigger_value

    def apply_runtime_settings_to_ui(self):
        """将当前配置应用到界面。"""
        self.runtime_settings = config.reload_config()
        current_api = self.runtime_settings.get('current_api', self.runtime_settings.get('default_api', config.DEFAULT_API))
        self._is_applying_settings = True
        self.translator.set_api_type(current_api)

        api_index = self.api_combo.findData(current_api)
        if api_index >= 0:
            self.api_combo.setCurrentIndex(api_index)

        source_lang = self.runtime_settings.get('source_lang', 'auto')
        target_lang = self.runtime_settings.get('target_lang', 'zh')

        source_index = self.source_lang_combo.findData(source_lang)
        if source_index >= 0:
            self.source_lang_combo.setCurrentIndex(source_index)

        target_index = self.target_lang_combo.findData(target_lang)
        if target_index >= 0:
            self.target_lang_combo.setCurrentIndex(target_index)

        self.input_text.setPlaceholderText(
            "在此输入要翻译的文本，或使用快捷键热键:\n"
            f"{config.HOTKEYS['screenshot']} - 截图翻译\n"
            f"{config.HOTKEYS['clipboard']} - 复制翻译\n"
            f"{self._format_translate_input_trigger_label()} - 翻译输入框内容"
        )
        self.auto_monitor_checkbox.setChecked(self.runtime_settings.get('auto_clipboard_monitor', True))
        self._update_status_label()
        self._is_applying_settings = False

    def _update_status_label(self):
        api_name = TRANSLATION_APIS.get(self.translator.api_type, {}).get('name', self.translator.api_type)
        self.status_label.setText(f'当前翻译源: {api_name}')

    def on_api_changed(self, *_):
        selected_api = self.api_combo.currentData()
        if not selected_api:
            return
        self.translator.set_api_type(selected_api)
        self._update_status_label()
        if not self._is_applying_settings:
            settings_manager.update_setting('current_api', selected_api)

    def on_auto_monitor_changed(self, state):
        if self._is_applying_settings:
            return
        settings_manager.update_setting('auto_clipboard_monitor', bool(state))

    def open_settings_dialog(self):
        """打开设置对话框。"""
        dialog = SettingsDialog(self)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return

        settings = dialog.get_settings_data()
        settings_manager.save_settings(settings)
        config.reload_config()
        tesseract_ready = configure_tesseract()
        self.apply_runtime_settings_to_ui()
        self.restart_hotkeys()
        message = '设置已保存并生效'
        if not tesseract_ready:
            message += '\n当前 Tesseract 路径不可用，截图 OCR 功能暂不可用。'
        QMessageBox.information(self, '设置', message)

    def open_settings_from_tray(self):
        """从托盘打开主界面和设置。"""
        self.show_window()
        self.open_settings_dialog()
    
    def start_monitors(self):
        """启动监听器"""
        self.clipboard_monitor.start()
        self._restart_translate_input_detector()
    
    def do_translation(self, text: str = None, replace_active_input: bool = False):
        """执行翻译"""
        if isinstance(text, bool):
            text = None
        text = (text if text is not None else self.input_text.toPlainText()).strip()
        
        if not text:
            QMessageBox.warning(self, "提示", "请输入要翻译的文本")
            return

        self._pending_external_replace = replace_active_input
        
        source_lang = self.source_lang_combo.currentData()
        target_lang = self.target_lang_combo.currentData()
        
        self.output_text.setText("翻译中...")
        self._update_status_label()
        
        # 在新线程中执行翻译
        self.translation_worker = TranslationWorker(
            text,
            source_lang,
            target_lang,
            self.api_combo.currentData(),
        )
        self.translation_thread = QThread(self)
        self.translation_worker.moveToThread(self.translation_thread)
        self.translation_worker.result_ready.connect(self.on_translation_result)
        self.translation_worker.error_occurred.connect(self.on_translation_error)
        self.translation_worker.result_ready.connect(self.translation_thread.quit)
        self.translation_worker.error_occurred.connect(self.translation_thread.quit)
        self.translation_thread.finished.connect(self.translation_worker.deleteLater)
        self.translation_thread.finished.connect(self.translation_thread.deleteLater)
        current_thread = self.translation_thread
        self.translation_thread.finished.connect(lambda thread=current_thread: self._release_translation_thread(thread))
        self.translation_thread.started.connect(self.translation_worker.run)
        self._active_translation_threads.append(current_thread)
        self.translation_thread.start()
    
    def on_translation_result(self, result):
        """翻译完成"""
        primary_result = result.get('primary', '') if isinstance(result, dict) else str(result)

        self.output_text.setText(primary_result)
        if self._pending_external_replace:
            self.replace_text_in_active_input(primary_result)
            self._pending_external_replace = False
    
    def on_translation_error(self, error):
        """翻译出错"""
        self.output_text.setText(f"❌ {error}")
        if self._pending_external_replace:
            TRIPLE_SPACE_LOGGER.warning('External input translation failed: %s', error)
            self._notify_background_message(APP_NAME, f'外部输入框翻译失败：{error}')
            self._pending_external_replace = False
    
    def on_screenshot_clicked(self):
        """截图翻译按钮被点击"""
        if not configure_tesseract():
            QMessageBox.warning(
                self,
                'OCR 不可用',
                '未找到 Tesseract 可执行文件，请在设置中检查 Tesseract 路径。'
            )
            return

        self.statusBar().showMessage("请选择要翻译的区域...")
        
        # 获取截图
        screenshot_path = ScreenshotHandler.take_screenshot()
        
        if not screenshot_path:
            QMessageBox.critical(self, "错误", "截图失败")
            return
        
        # OCR识别
        ocr_language = self.runtime_settings.get('ocr_language', 'chi_sim+eng')
        text = OCRHandler.recognize_text_from_image(screenshot_path, ocr_language)
        
        if not text:
            QMessageBox.warning(self, "提示", "未识别到文字")
            self.statusBar().showMessage("就绪")
            return
        
        # 显示识别结果
        self.input_text.setText(text)
        
        # 自动翻译
        self.do_translation()
        self.statusBar().showMessage("就绪")
    
    def on_clipboard_change(self, text):
        """剪贴板内容变化"""
        if self._clipboard_capture_in_progress:
            return

        if self.auto_monitor_checkbox.isChecked():
            self.input_text.setText(text)
            self.do_translation()
    
    def on_clipboard_translate(self):
        """从剪贴板翻译"""
        text = self.clipboard_monitor.get_current_clipboard()
        
        if not text:
            QMessageBox.warning(self, "提示", "剪贴板为空")
            return
        
        self.input_text.setText(text)
        self.do_translation()
    
    def _is_our_app_foreground(self) -> bool:
        """用 Win32 API 判断当前前台窗口是否属于本进程。

        比 Qt 的 hasFocus() / isActiveWindow() 更可靠：pynput 在驱动层拦截按键，
        速度快于 Windows 向 Qt 发送 WM_KILLFOCUS，存在竞态导致 hasFocus() 返回旧值。
        """
        try:
            foreground_hwnd = ctypes.windll.user32.GetForegroundWindow()
            if not foreground_hwnd:
                return False
            pid = ctypes.c_ulong(0)
            ctypes.windll.user32.GetWindowThreadProcessId(foreground_hwnd, ctypes.byref(pid))
            return pid.value == os.getpid()
        except Exception:
            return self.isActiveWindow()

    def on_global_translate_triggered(self):
        """全局翻译热键回调"""
        TRIPLE_SPACE_LOGGER.info('Global translate trigger received')
        # 使用 Win32 GetForegroundWindow 检查系统级焦点，不依赖 Qt hasFocus()
        # 以规避 pynput 竞态（按键事件早于 WM_KILLFOCUS 到达 Qt 事件队列）
        if self._is_our_app_foreground() and self.input_text.hasFocus():
            text = self.input_text.toPlainText().strip()
            if text:
                TRIPLE_SPACE_LOGGER.info('Trigger handled inside main window input, text_length=%d', len(text))
                self.do_translation()
            return

        trim_trigger_spaces = config.HOTKEYS.get('translate_input', TRIPLE_SPACE_TRIGGER) == TRIPLE_SPACE_TRIGGER
        if trim_trigger_spaces:
            TRIPLE_SPACE_LOGGER.info('Trigger mode is triple_space, capture first and trim trailing spaces in memory')

        captured_text = self.capture_text_from_active_input()
        if not captured_text:
            TRIPLE_SPACE_LOGGER.warning('Failed to capture text from active input')
            self._notify_background_message(APP_NAME, '未能从当前输入框获取文本，请确认光标位于可编辑文本框内。')
            return

        if trim_trigger_spaces:
            captured_text = self._trim_triple_space_trigger(captured_text)

        TRIPLE_SPACE_LOGGER.info('Captured text from active input, text_length=%d', len(captured_text))
        self.input_text.setText(captured_text)
        self.do_translation(captured_text, replace_active_input=True)

    def _press_key_sequence(self, *keys):
        for key in keys:
            self.keyboard_controller.press(key)
        for key in reversed(keys):
            self.keyboard_controller.release(key)

    def _tap_key(self, key):
        self.keyboard_controller.press(key)
        self.keyboard_controller.release(key)

    def _suppress_triple_space_detection(self, reason: str):
        if self.triple_click_detector:
            return self.triple_click_detector.suppress_detection(reason)
        return None

    def _notify_background_message(self, title: str, message: str):
        TRIPLE_SPACE_LOGGER.info('Background notification: %s | %s', title, message)
        if hasattr(self, 'tray_icon') and self.tray_icon.isVisible():
            self.tray_icon.showMessage(
                title,
                message,
                QSystemTrayIcon.MessageIcon.Warning,
                3000,
            )

    def _clear_external_selection(self):
        """抓取后清掉外部输入框的全选状态，避免后续空格覆盖全文。"""
        suppression = self._suppress_triple_space_detection('clear_selection')
        try:
            if suppression:
                with suppression:
                    self._tap_key(Key.right)
            else:
                self._tap_key(Key.right)
            TRIPLE_SPACE_LOGGER.info('Cleared external text selection with RIGHT key')
        except Exception:
            TRIPLE_SPACE_LOGGER.exception('Failed to clear external text selection')
            pass

    def _trim_triple_space_trigger(self, text: str) -> str:
        if text.endswith('   '):
            TRIPLE_SPACE_LOGGER.info('Trimmed trailing triple-space trigger from captured text')
            return text[:-3]

        TRIPLE_SPACE_LOGGER.info('Captured text did not end with triple-space trigger, no trimming applied')
        return text

    def _wait_for_clipboard_change(self, previous_text: str, timeout: float = 0.8) -> str:
        deadline = time.time() + timeout
        while time.time() < deadline:
            current_text = pyperclip.paste()
            if current_text != previous_text and current_text.strip():
                return current_text
            time.sleep(0.05)
        return ''

    def _foreground_has_text_input(self) -> bool:
        """尽力检测前台窗口是否有文本输入焦点（光标），避免向游戏等非文本窗口发送 Ctrl+A。"""
        try:
            hwnd = ctypes.windll.user32.GetForegroundWindow()
            if not hwnd:
                return False

            thread_id = ctypes.windll.user32.GetWindowThreadProcessId(hwnd, None)

            class _GUITHREADINFO(ctypes.Structure):
                _fields_ = [
                    ('cbSize',       ctypes.c_uint32),
                    ('flags',        ctypes.c_uint32),
                    ('hwndActive',   ctypes.c_void_p),
                    ('hwndFocus',    ctypes.c_void_p),
                    ('hwndCapture',  ctypes.c_void_p),
                    ('hwndMenuOwner',ctypes.c_void_p),
                    ('hwndMoveSize', ctypes.c_void_p),
                    ('hwndCaret',    ctypes.c_void_p),
                    ('rcCaret',      ctypes.c_byte * 16),  # RECT: 4 × LONG
                ]

            gui_info = _GUITHREADINFO()
            gui_info.cbSize = ctypes.sizeof(_GUITHREADINFO)
            if not ctypes.windll.user32.GetGUIThreadInfo(thread_id, ctypes.byref(gui_info)):
                return True  # API 调用失败，保守地认为有文本输入

            if gui_info.hwndCaret:
                return True  # Win32 caret 激活 → 标准文本控件

            # 浏览器和 Electron 应用自行绘制光标，不走 Win32 caret API
            # 通过窗口类名识别，使三击空格在浏览器文本框内仍可用
            focused_hwnd = gui_info.hwndFocus or hwnd
            buf = ctypes.create_unicode_buffer(256)
            ctypes.windll.user32.GetClassNameW(focused_hwnd, buf, 256)
            class_name = buf.value

            web_render_classes = {
                'Chrome_RenderWidgetHostHWND',  # Chrome / Edge（新版）/ Electron
                'MozillaWindowClass',            # Firefox
            }
            return class_name in web_render_classes
        except Exception:
            TRIPLE_SPACE_LOGGER.exception('_foreground_has_text_input 检测失败')
            return True  # 保守回退：假设有文本输入

    def _copy_active_input_text(self, previous_clipboard: str, select_all: bool = True, timeout: float = 0.8) -> str:
        suppression = self._suppress_triple_space_detection('capture_active_input')
        if suppression:
            with suppression:
                if select_all:
                    self._press_key_sequence(Key.ctrl, 'a')
                    time.sleep(0.08)
                self._press_key_sequence(Key.ctrl, 'c')
        else:
            if select_all:
                self._press_key_sequence(Key.ctrl, 'a')
                time.sleep(0.08)
            self._press_key_sequence(Key.ctrl, 'c')

        time.sleep(0.05)
        return self._wait_for_clipboard_change(previous_clipboard, timeout=timeout)

    def capture_text_from_active_input(self):
        """从当前激活的软件输入框抓取文本。"""
        original_clipboard = self.clipboard_monitor.get_current_clipboard()
        capture_sentinel = f'__easy_translation_capture__{time.time_ns()}__'
        self._clipboard_capture_in_progress = True
        did_select_all = False
        TRIPLE_SPACE_LOGGER.info('Starting capture from active input, previous_clipboard_length=%d', len(original_clipboard or ''))

        # 在开始前记录当前前台窗口，用于防止焦点漂移后向错误窗口发送 Ctrl+A
        foreground_hwnd_before = ctypes.windll.user32.GetForegroundWindow()

        try:
            self.clipboard_monitor.set_clipboard(capture_sentinel)
            self.clipboard_monitor.last_clipboard = capture_sentinel
            time.sleep(0.03)

            # 第一步：仅 Ctrl+C（无副作用），获取已选中的文本
            captured_text = self._copy_active_input_text(capture_sentinel, select_all=False, timeout=0.5)

            if not captured_text:
                # 第二步：若无选中文本，检查前台窗口是否仍是触发时的同一窗口
                # 策略：只要窗口未切换就尝试 Ctrl+A，不依赖 Win32 caret 检测
                # （Win32 caret 只存在于旧式控件，WPF/Qt/UWP/Electron 等现代框架均不使用）
                # 安全保障：对比窗口句柄，防止焦点漂移后误全选背景应用
                current_foreground_hwnd = ctypes.windll.user32.GetForegroundWindow()
                if foreground_hwnd_before and current_foreground_hwnd == foreground_hwnd_before:
                    did_select_all = True
                    TRIPLE_SPACE_LOGGER.info('No selection found, attempting select-all copy (hwnd=%s)', hex(current_foreground_hwnd))
                    captured_text = self._copy_active_input_text(capture_sentinel, select_all=True, timeout=0.8)
                    if not captured_text:
                        TRIPLE_SPACE_LOGGER.warning('Select-all capture returned empty, retrying')
                        captured_text = self._copy_active_input_text(capture_sentinel, select_all=True, timeout=1.0)
                else:
                    TRIPLE_SPACE_LOGGER.info(
                        'Foreground window changed during capture (before=%s, after=%s), skipping Ctrl+A to avoid selecting wrong window',
                        hex(foreground_hwnd_before or 0), hex(current_foreground_hwnd or 0)
                    )

            TRIPLE_SPACE_LOGGER.info('Capture finished, captured_length=%d', len(captured_text or ''))
            return captured_text.strip() if captured_text else ''
        except Exception:
            TRIPLE_SPACE_LOGGER.exception('Exception while capturing text from active input')
            return ''
        finally:
            if did_select_all:
                self._clear_external_selection()
            try:
                self.clipboard_monitor.set_clipboard(original_clipboard)
                self.clipboard_monitor.last_clipboard = original_clipboard
            except Exception:
                TRIPLE_SPACE_LOGGER.exception('Failed to restore clipboard after capture')
                pass
            self._clipboard_capture_in_progress = False

    def replace_text_in_active_input(self, translated_text: str):
        """将翻译结果回填到当前激活的外部输入框。"""
        previous_clipboard = self.clipboard_monitor.get_current_clipboard()
        self._clipboard_capture_in_progress = True
        TRIPLE_SPACE_LOGGER.info('Replacing text in active input, translated_length=%d', len(translated_text or ''))

        try:
            self.clipboard_monitor.set_clipboard(translated_text)
            self.clipboard_monitor.last_clipboard = translated_text
            time.sleep(0.05)
            suppression = self._suppress_triple_space_detection('replace_active_input')
            if suppression:
                with suppression:
                    self._press_key_sequence(Key.ctrl, 'a')
                    time.sleep(0.03)
                    self._press_key_sequence(Key.ctrl, 'v')
            else:
                self._press_key_sequence(Key.ctrl, 'a')
                time.sleep(0.03)
                self._press_key_sequence(Key.ctrl, 'v')
            time.sleep(0.03)
            self._clear_external_selection()
            TRIPLE_SPACE_LOGGER.info('External input replacement completed')
        finally:
            time.sleep(0.05)
            try:
                self.clipboard_monitor.set_clipboard(previous_clipboard)
                self.clipboard_monitor.last_clipboard = previous_clipboard
            except Exception:
                TRIPLE_SPACE_LOGGER.exception('Failed to restore clipboard after replacement')
                pass
            self._clipboard_capture_in_progress = False
    
    def show_window(self):
        """显示窗口"""
        if self.isMinimized():
            self.showNormal()
        else:
            self.show()
        self.raise_()
        self.activateWindow()

    def changeEvent(self, event):
        """最小化时切换到托盘后台运行。"""
        super().changeEvent(event)
        if self._is_quitting:
            return

        if event.type() == QEvent.Type.WindowStateChange and self.isMinimized():
            QTimer.singleShot(0, self.minimize_to_tray)
    
    def clear_texts(self):
        """清空文本"""
        self.input_text.clear()
        self.output_text.clear()

    def clear_translation_cache(self, show_message: bool = False):
        """清理当前翻译缓存。"""
        self.translator.clear_cache()
        if show_message:
            QMessageBox.information(self, '缓存', '翻译缓存已清理')

    def _release_translation_thread(self, thread):
        if thread in self._active_translation_threads:
            self._active_translation_threads.remove(thread)
        if self.translation_thread is thread:
            self.translation_thread = None
            self.translation_worker = None

    def _stop_translation_threads(self):
        for thread in list(self._active_translation_threads):
            thread.quit()
            thread.wait(1000)
        self._active_translation_threads.clear()
    
    def quit_app(self):
        """退出应用"""
        self._is_quitting = True
        self._stop_translation_threads()
        self.hotkey_manager.stop()
        self.clipboard_monitor.stop()
        if self.triple_click_detector:
            self.triple_click_detector.stop()
        self.tray_icon.hide()
        app = QApplication.instance()
        if app is not None:
            app.quit()
        else:
            sys.exit(0)
    
    def closeEvent(self, event):
        """窗口关闭事件"""
        if self._is_quitting:
            event.accept()
            return

        # 关闭窗口时最小化到托盘而不是退出
        self.minimize_to_tray()
        event.ignore()


def main():
    set_windows_app_id()
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setApplicationDisplayName(APP_NAME)
    app.setQuitOnLastWindowClosed(False)
    app_icon = load_app_icon()
    if not app_icon.isNull():
        app.setWindowIcon(app_icon)

    single_instance = SingleInstanceManager(APP_INSTANCE_KEY)
    if not single_instance.start():
        return 0

    window = MainWindow()
    single_instance.activate_requested.connect(window.show_window)
    app.aboutToQuit.connect(single_instance.cleanup)
    window.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
