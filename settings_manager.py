"""
设置管理模块 - 负责用户设置和 API 密钥的本地持久化
"""
import json
from copy import deepcopy
from pathlib import Path
from typing import Any, Dict, Optional

from cryptography.fernet import Fernet, InvalidToken


PROJECT_ROOT = Path(__file__).parent
SETTINGS_FILE = PROJECT_ROOT / 'user_settings.json'
KEY_FILE = PROJECT_ROOT / '.settings.key'

DEFAULT_SETTINGS = {
    'default_api': 'google',
    'current_api': 'google',
    'source_lang': 'auto',
    'target_lang': '__smart__',
    'ocr_language': 'chi_sim+eng',
    'tesseract_path': '',
    'auto_clipboard_monitor': True,
    'translate_input_time_window': 1.0,
    'api_keys': {
        'baidu': {
            'app_id': '',
            'secret_key': '',
        },
        'tencent': {
            'secret_id': '',
            'secret_key': '',
            'region': 'ap-beijing',
        },
        'deepl': {
            'auth_key': '',
        },
        'microsoft': {
            'subscription_key': '',
            'region': '',
        },
    },
    'provider_settings': {
        'ollama': {
            'base_url': 'http://127.0.0.1:11434',
            'model': 'qwen2.5:7b',
            'timeout': 20,
        },
    },
    'hotkeys': {
        'screenshot': 'alt+shift+s',
        'clipboard': 'alt+shift+c',
        'show_window': 'alt+shift+t',
        'translate_input': 'triple_space',
    },
}


class SettingsManager:
    """管理应用设置和敏感配置。"""

    def __init__(self, settings_file: Path = SETTINGS_FILE, key_file: Path = KEY_FILE):
        self.settings_file = Path(settings_file)
        self.key_file = Path(key_file)
        self._cipher = Fernet(self._load_or_create_key())
        self._settings = self.load_settings()

    def _load_or_create_key(self) -> bytes:
        if self.key_file.exists():
            return self.key_file.read_bytes().strip()

        key = Fernet.generate_key()
        self.key_file.write_bytes(key)
        return key

    def _encrypt(self, value: str) -> str:
        if not value:
            return ''
        return self._cipher.encrypt(value.encode('utf-8')).decode('utf-8')

    def _decrypt(self, value: str) -> str:
        if not value:
            return ''
        try:
            return self._cipher.decrypt(value.encode('utf-8')).decode('utf-8')
        except (InvalidToken, ValueError):
            return ''

    def _merge_defaults(self, current: Dict[str, Any], defaults: Dict[str, Any]) -> Dict[str, Any]:
        merged = deepcopy(defaults)
        for key, value in current.items():
            if isinstance(value, dict) and isinstance(merged.get(key), dict):
                merged[key] = self._merge_defaults(value, merged[key])
            else:
                merged[key] = value
        return merged

    def _encrypt_api_keys(self, settings: Dict[str, Any]) -> Dict[str, Any]:
        encrypted = deepcopy(settings)
        api_keys = encrypted.get('api_keys', {})
        for provider, credentials in api_keys.items():
            if not isinstance(credentials, dict):
                continue
            api_keys[provider] = {
                key: self._encrypt(str(value)) if value else ''
                for key, value in credentials.items()
            }
        return encrypted

    def _decrypt_api_keys(self, settings: Dict[str, Any]) -> Dict[str, Any]:
        decrypted = deepcopy(settings)
        api_keys = decrypted.get('api_keys', {})
        for provider, credentials in api_keys.items():
            if not isinstance(credentials, dict):
                continue
            api_keys[provider] = {
                key: self._decrypt(value) if value else ''
                for key, value in credentials.items()
            }
        return decrypted

    def load_settings(self) -> Dict[str, Any]:
        if not self.settings_file.exists():
            settings = deepcopy(DEFAULT_SETTINGS)
            self.save_settings(settings)
            return settings

        try:
            raw_settings = json.loads(self.settings_file.read_text(encoding='utf-8'))
        except (json.JSONDecodeError, OSError):
            raw_settings = {}

        merged = self._merge_defaults(raw_settings, DEFAULT_SETTINGS)
        return self._decrypt_api_keys(merged)

    def reload_settings(self) -> Dict[str, Any]:
        self._settings = self.load_settings()
        return deepcopy(self._settings)

    def save_settings(self, settings: Optional[Dict[str, Any]] = None) -> None:
        if settings is not None:
            self._settings = self._merge_defaults(settings, DEFAULT_SETTINGS)

        payload = self._encrypt_api_keys(self._settings)
        self.settings_file.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2),
            encoding='utf-8'
        )

    def get_all_settings(self) -> Dict[str, Any]:
        return deepcopy(self._settings)

    def get_setting(self, key: str, default: Any = None) -> Any:
        return self._settings.get(key, default)

    def update_setting(self, key: str, value: Any) -> None:
        self._settings[key] = value
        self.save_settings()

    def get_api_credentials(self, provider: str) -> Dict[str, str]:
        credentials = self._settings.get('api_keys', {}).get(provider, {})
        return deepcopy(credentials)

    def get_provider_settings(self, provider: str) -> Dict[str, Any]:
        provider_settings = self._settings.get('provider_settings', {}).get(provider, {})
        return deepcopy(provider_settings)

    def set_api_credentials(self, provider: str, credentials: Dict[str, str]) -> None:
        self._settings.setdefault('api_keys', {})[provider] = dict(credentials)
        self.save_settings()

    def set_provider_settings(self, provider: str, provider_settings: Dict[str, Any]) -> None:
        self._settings.setdefault('provider_settings', {})[provider] = dict(provider_settings)
        self.save_settings()

    def validate_api_credentials(self, provider: str, credentials: Dict[str, str]) -> bool:
        rules = {
            'baidu': ('app_id', 'secret_key'),
            'tencent': ('secret_id', 'secret_key'),
            'deepl': ('auth_key',),
            'microsoft': ('subscription_key', 'region'),
        }
        required_fields = rules.get(provider, ())
        if not required_fields:
            return True

        return all(bool(str(credentials.get(field, '')).strip()) for field in required_fields)

    def validate_provider_settings(self, provider: str, provider_settings: Dict[str, Any]) -> bool:
        if provider == 'ollama':
            base_url = str(provider_settings.get('base_url', '')).strip()
            model = str(provider_settings.get('model', '')).strip()
            return bool(base_url and model)
        return True

    def validate_translate_input_time_window(self, value: Any) -> bool:
        try:
            window = float(value)
        except (TypeError, ValueError):
            return False
        return 0.3 <= window <= 3.0


settings_manager = SettingsManager()
