"""
翻译核心模块 - 处理翻译请求和API调用
"""
import hashlib
import hmac
import json
import re
import time
from typing import Optional
from urllib.parse import urljoin

import requests

from config import DEFAULT_API, SMART_TARGET_LANG, get_api_credentials, get_provider_settings


class TranslatorCore:
    """翻译引擎核心类"""
    
    def __init__(self, api_type: str = DEFAULT_API, credentials_override: Optional[dict] = None):
        self.api_type = api_type
        self.credentials_override = credentials_override or {}
        self.cache = {}  # 简单的翻译缓存
        self.last_error: Optional[str] = None

    def set_api_type(self, api_type: str):
        self.api_type = api_type

    def clear_cache(self) -> None:
        self.cache.clear()

    def _set_error(self, message: str) -> None:
        self.last_error = message

    def _detect_primary_script(self, text: str) -> str:
        for char in text:
            if re.match(r'[\u4e00-\u9fff]', char):
                return 'zh'
            if re.match(r'[A-Za-z]', char):
                return 'en'
        return 'unknown'

    def _calculate_language_signal(self, text: str):
        chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', text))
        english_words = len(re.findall(r'\b[A-Za-z]+\b', text))
        english_chars = len(re.findall(r'[A-Za-z]', text))
        return chinese_chars, english_words, english_chars

    def _resolve_translation_direction(self, text: str, source_lang: str, target_lang: str):
        if target_lang != SMART_TARGET_LANG:
            return source_lang, target_lang

        if source_lang == 'zh':
            return 'zh', 'en'
        if source_lang == 'en':
            return 'en', 'zh'

        chinese_count, english_word_count, english_char_count = self._calculate_language_signal(text)
        primary_script = self._detect_primary_script(text)

        if chinese_count == 0 and english_char_count == 0:
            return 'auto', 'zh'

        # 纯中文或接近纯中文
        if chinese_count > 0 and english_char_count == 0:
            return 'zh', 'en'

        # 纯英文或接近纯英文
        if english_char_count > 0 and chinese_count == 0:
            return 'en', 'zh'

        # 混合文本时，优先比较更稳定的中文字符数和英文单词数
        if chinese_count > english_word_count * 2:
            return 'zh', 'en'
        if english_word_count > max(chinese_count, 1):
            return 'en', 'zh'

        if primary_script == 'zh':
            return 'zh', 'en'
        if primary_script == 'en':
            return 'en', 'zh'

        # 如果单词数接近，再用字符数辅助判断
        if chinese_count >= english_char_count * 0.6:
            return 'zh', 'en'
        if english_char_count > chinese_count:
            return 'en', 'zh'

        return 'auto', 'zh'
        
    def translate(self, text: str, source_lang: str = 'auto', 
                  target_lang: str = 'zh') -> Optional[str]:
        result = self.translate_result(text, source_lang, target_lang)
        if not result:
            return None
        return result.get('primary')

    def translate_result(self, text: str, source_lang: str = 'auto',
                         target_lang: str = 'zh') -> Optional[dict]:
        """
        翻译文本
        
        Args:
            text: 要翻译的文本
            source_lang: 源语言（'auto'自动检测）
            target_lang: 目标语言
            
        Returns:
            翻译结果，失败返回None
        """
        self.last_error = None

        if not text or not text.strip():
            self._set_error('请输入要翻译的文本')
            return None

        source_lang, target_lang = self._resolve_translation_direction(
            text,
            source_lang,
            target_lang,
        )
            
        # 检查缓存
        cache_key = f"{self.api_type}:{source_lang}:{target_lang}:{text}"
        if cache_key in self.cache:
            cached_result = self.cache[cache_key]
            return {
                'primary': cached_result,
                'candidates': [cached_result],
                'source_lang': source_lang,
                'target_lang': target_lang,
            }
        
        # 调用对应的翻译API
        if self.api_type == 'google':
            result = self._translate_google(text, source_lang, target_lang)
        elif self.api_type == 'baidu':
            result = self._translate_baidu(text, source_lang, target_lang)
        elif self.api_type == 'tencent':
            result = self._translate_tencent(text, source_lang, target_lang)
        elif self.api_type == 'ollama':
            result = self._translate_ollama_result(text, source_lang, target_lang)
        else:
            self._set_error(f'不支持的翻译源: {self.api_type}')
            result = None

        if isinstance(result, str):
            result = {
                'primary': result,
                'candidates': [result],
                'source_lang': source_lang,
                'target_lang': target_lang,
            }
            
        # 缓存结果
        if result and result.get('primary'):
            self.cache[cache_key] = result['primary']
        elif self.last_error is None:
            self._set_error('翻译失败，请稍后重试')
            
        return result
    
    def _translate_google(self, text: str, source_lang: str, 
                         target_lang: str) -> Optional[str]:
        """Google翻译（免费方案）"""
        return SimpleGoogleTranslate.translate(text, source_lang, target_lang)
    
    def _translate_baidu(self, text: str, source_lang: str, 
                        target_lang: str) -> Optional[str]:
        """百度翻译（需要API密钥）"""
        credentials = self.credentials_override or get_api_credentials('baidu')
        app_id = credentials.get('app_id', '').strip()
        secret_key = credentials.get('secret_key', '').strip()

        if not app_id or not secret_key:
            self._set_error('百度翻译需要先在设置中填写 App ID 和 Secret Key')
            return None

        salt = str(int(time.time()))
        sign_raw = f'{app_id}{text}{salt}{secret_key}'
        sign = hashlib.md5(sign_raw.encode('utf-8')).hexdigest()

        params = {
            'q': text,
            'from': source_lang,
            'to': target_lang,
            'appid': app_id,
            'salt': salt,
            'sign': sign,
        }

        try:
            response = requests.get(
                'https://api.fanyi.baidu.com/api/trans/vip/translate',
                params=params,
                timeout=8,
            )
            response.raise_for_status()
            data = response.json()

            results = data.get('trans_result', [])
            if results:
                return '\n'.join(item.get('dst', '') for item in results if item.get('dst'))

            error_message = data.get('error_msg')
            if error_message:
                self._set_error(f'百度翻译失败: {error_message}')
                return None

            self._set_error('百度翻译返回了无效响应')
            return None
        except requests.RequestException as error:
            self._set_error(f'百度翻译网络异常: {error}')
            return None
        except Exception as error:
            self._set_error(f'百度翻译出错: {error}')
            return None
    
    def _translate_tencent(self, text: str, source_lang: str, 
                          target_lang: str) -> Optional[str]:
        """腾讯翻译（需要API密钥）"""
        credentials = self.credentials_override or get_api_credentials('tencent')
        secret_id = credentials.get('secret_id', '').strip()
        secret_key = credentials.get('secret_key', '').strip()
        region = credentials.get('region', 'ap-beijing').strip() or 'ap-beijing'

        if not secret_id or not secret_key:
            self._set_error('腾讯翻译需要先在设置中填写 Secret ID 和 Secret Key')
            return None

        service = 'tmt'
        host = 'tmt.tencentcloudapi.com'
        endpoint = f'https://{host}'
        action = 'TextTranslate'
        version = '2018-03-21'
        timestamp = int(time.time())
        date = time.strftime('%Y-%m-%d', time.gmtime(timestamp))

        payload = {
            'SourceText': text,
            'Source': source_lang,
            'Target': target_lang,
            'ProjectId': 0,
        }
        payload_json = json.dumps(payload, ensure_ascii=False, separators=(',', ':'))

        hashed_request_payload = hashlib.sha256(payload_json.encode('utf-8')).hexdigest()
        canonical_request = (
            'POST\n' 
            '/\n' 
            '\n' 
            'content-type:application/json; charset=utf-8\n' 
            f'host:{host}\n' 
            f'x-tc-action:{action.lower()}\n' 
            '\n' 
            'content-type;host;x-tc-action\n' 
            f'{hashed_request_payload}'
        )

        credential_scope = f'{date}/{service}/tc3_request'
        hashed_canonical_request = hashlib.sha256(canonical_request.encode('utf-8')).hexdigest()
        string_to_sign = (
            'TC3-HMAC-SHA256\n'
            f'{timestamp}\n'
            f'{credential_scope}\n'
            f'{hashed_canonical_request}'
        )

        secret_date = hmac.new(
            ('TC3' + secret_key).encode('utf-8'),
            date.encode('utf-8'),
            hashlib.sha256,
        ).digest()
        secret_service = hmac.new(secret_date, service.encode('utf-8'), hashlib.sha256).digest()
        secret_signing = hmac.new(secret_service, b'tc3_request', hashlib.sha256).digest()
        signature = hmac.new(
            secret_signing,
            string_to_sign.encode('utf-8'),
            hashlib.sha256,
        ).hexdigest()

        authorization = (
            'TC3-HMAC-SHA256 '
            f'Credential={secret_id}/{credential_scope}, '
            'SignedHeaders=content-type;host;x-tc-action, '
            f'Signature={signature}'
        )

        headers = {
            'Authorization': authorization,
            'Content-Type': 'application/json; charset=utf-8',
            'Host': host,
            'X-TC-Action': action,
            'X-TC-Timestamp': str(timestamp),
            'X-TC-Version': version,
            'X-TC-Region': region,
        }

        try:
            response = requests.post(endpoint, data=payload_json.encode('utf-8'), headers=headers, timeout=8)
            response.raise_for_status()
            data = response.json()
            response_data = data.get('Response', {})
            if 'Error' in response_data:
                error_info = response_data['Error']
                self._set_error(
                    f"腾讯翻译失败: {error_info.get('Code', 'Unknown')} - {error_info.get('Message', '')}"
                )
                return None
            target_text = response_data.get('TargetText')
            if target_text:
                return target_text

            self._set_error('腾讯翻译返回了无效响应')
            return None
        except requests.RequestException as error:
            self._set_error(f'腾讯翻译网络异常: {error}')
            return None
        except Exception as error:
            self._set_error(f'腾讯翻译出错: {error}')
            return None

    def _translate_ollama_result(self, text: str, source_lang: str,
                                target_lang: str) -> Optional[dict]:
        """Ollama 本地 AI 翻译，返回主结果和候选结果。"""
        provider_settings = get_provider_settings('ollama')
        base_url = provider_settings.get('base_url', 'http://127.0.0.1:11434').strip()
        model = provider_settings.get('model', '').strip()
        timeout_value = provider_settings.get('timeout', 20)
        candidate_count = provider_settings.get('candidate_count', 3)

        if not base_url or not model:
            self._set_error('Ollama 需要先在设置中填写服务地址和模型名称')
            return None

        try:
            timeout = max(1, int(timeout_value))
        except (TypeError, ValueError):
            timeout = 20
        try:
            candidate_count = max(1, int(candidate_count))
        except (TypeError, ValueError):
            candidate_count = 3

        source_label = self._language_label(source_lang)
        target_label = self._language_label(target_lang)
        prompt = (
            f'你是专业翻译助手。请将下面文本从{source_label}翻译成{target_label}。'
            f'请提供 {candidate_count} 个不同风格但都准确的译文候选。'
            '输出 JSON，格式必须为 {"translations": ["译文1", "译文2"]}。'
            '不要输出解释，不要输出 JSON 之外的任何内容。\n\n'
            f'原文:\n{text}'
        )

        payload = {
            'model': model,
            'prompt': prompt,
            'stream': False,
            'format': 'json',
            'options': {
                'temperature': 0.2,
            },
        }

        try:
            response = requests.post(
                urljoin(base_url.rstrip('/') + '/', 'api/generate'),
                json=payload,
                timeout=timeout,
            )
            response.raise_for_status()
            data = response.json()
            response_text = str(data.get('response', '')).strip()
            candidates = self._parse_ollama_candidates(response_text)
            if candidates:
                return {
                    'primary': candidates[0],
                    'candidates': candidates,
                    'source_lang': source_lang,
                    'target_lang': target_lang,
                }

            self._set_error('Ollama 返回了空结果')
            return None
        except requests.RequestException as error:
            self._set_error(f'Ollama 连接失败: {error}')
            return None
        except Exception as error:
            self._set_error(f'Ollama 翻译出错: {error}')
            return None

    def _parse_ollama_candidates(self, response_text: str) -> list[str]:
        if not response_text:
            return []

        candidates = []
        try:
            data = json.loads(response_text)
            translations = data.get('translations', [])
            if isinstance(translations, list):
                candidates = [str(item).strip() for item in translations if str(item).strip()]
        except json.JSONDecodeError:
            lines = [line.strip('-* \n\r\t') for line in response_text.splitlines() if line.strip()]
            candidates = [line for line in lines if line]

        unique_candidates = []
        for candidate in candidates:
            if candidate not in unique_candidates:
                unique_candidates.append(candidate)
        return unique_candidates

    def _language_label(self, language_code: str) -> str:
        language_map = {
            'auto': '自动检测到的语言',
            'zh': '中文',
            'en': '英文',
            'ja': '日文',
            'ko': '韩文',
            'fr': '法文',
            'de': '德文',
            'es': '西班牙文',
            'ru': '俄文',
        }
        return language_map.get(language_code, language_code)


class SimpleGoogleTranslate:
    """简单的Google翻译实现（无需API密钥）"""
    
    @staticmethod
    def translate(text: str, source_lang: str = 'auto', 
                  target_lang: str = 'zh') -> Optional[str]:
        """
        使用requests库调用Google翻译（基于user-agent）
        """
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                              'AppleWebKit/537.36'
            }
            
            # 使用第三方简单API或爬虫方式
            # 这里为演示，实际使用时建议使用专门的库
            url = f'https://translate.googleapis.com/translate_a/single'
            params = {
                'client': 'gtx',
                'sl': source_lang,
                'tl': target_lang,
                'dt': 't',
                'q': text
            }
            
            response = requests.get(url, params=params, headers=headers, 
                                   timeout=5)
            response.encoding = 'utf-8'
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list) and data:
                    segments = data[0]
                    translated_parts = [segment[0] for segment in segments if segment and segment[0]]
                    return ''.join(translated_parts)
            return None
            
        except Exception:
            return None


if __name__ == '__main__':
    # 测试
    translator = TranslatorCore()
    result = translator.translate("Hello World", "auto", "zh")
    print(f"翻译结果: {result}")
