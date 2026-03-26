import importlib
import json
import os
import runpy
import sys
import tempfile
import types
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / 'src'
RUNTIME_ENV_VAR = 'EASY_TRANSLATION_RUNTIME_DIR'


class ModuleIsolationMixin:
    managed_modules = ('settings_manager', 'config', 'translator_core')

    def setUp(self):
        self._sys_path_before = list(sys.path)
        self._env_runtime_before = os.environ.get(RUNTIME_ENV_VAR)

    def tearDown(self):
        self._clear_managed_modules()
        sys.path[:] = self._sys_path_before
        if self._env_runtime_before is None:
            os.environ.pop(RUNTIME_ENV_VAR, None)
        else:
            os.environ[RUNTIME_ENV_VAR] = self._env_runtime_before

    def _clear_managed_modules(self):
        for module_name in self.managed_modules:
            sys.modules.pop(module_name, None)

    def _prepare_isolated_imports(self, runtime_dir: Path):
        self._clear_managed_modules()
        os.environ[RUNTIME_ENV_VAR] = str(runtime_dir)
        if str(SRC_ROOT) not in sys.path:
            sys.path.insert(0, str(SRC_ROOT))


class SmokeBaselineTests(ModuleIsolationMixin, unittest.TestCase):
    def test_config_uses_runtime_override_and_bootstraps_default_files(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            runtime_dir = Path(temp_dir)
            self._prepare_isolated_imports(runtime_dir)

            config = importlib.import_module('config')

            self.assertEqual(config.PROJECT_ROOT.resolve(), PROJECT_ROOT)
            self.assertEqual(config.RUNTIME_DIR, runtime_dir)
            self.assertEqual(config.LOG_DIR, runtime_dir / 'logs')
            self.assertEqual(config.SCREENSHOT_DIR, runtime_dir / 'screenshots')
            self.assertTrue((runtime_dir / 'user_settings.json').exists())
            self.assertTrue((runtime_dir / '.settings.key').exists())
            self.assertTrue(config.LOG_DIR.exists())
            self.assertTrue(config.SCREENSHOT_DIR.exists())

    def test_settings_manager_round_trips_encrypted_credentials(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            runtime_dir = Path(temp_dir)
            self._prepare_isolated_imports(runtime_dir)
            settings_manager_module = importlib.import_module('settings_manager')

            settings_file = runtime_dir / 'test_settings.json'
            key_file = runtime_dir / 'test_settings.key'
            manager = settings_manager_module.SettingsManager(
                settings_file=settings_file,
                key_file=key_file,
            )

            settings = manager.get_all_settings()
            settings['api_keys']['baidu']['app_id'] = 'demo-app'
            settings['api_keys']['baidu']['secret_key'] = 'demo-secret'
            settings['hotkeys']['translate_input'] = 'alt+shift+x'
            manager.save_settings(settings)

            raw_payload = json.loads(settings_file.read_text(encoding='utf-8'))
            self.assertNotEqual(raw_payload['api_keys']['baidu']['app_id'], 'demo-app')
            self.assertNotEqual(raw_payload['api_keys']['baidu']['secret_key'], 'demo-secret')

            reloaded_manager = settings_manager_module.SettingsManager(
                settings_file=settings_file,
                key_file=key_file,
            )

            self.assertEqual(reloaded_manager.get_api_credentials('baidu')['app_id'], 'demo-app')
            self.assertEqual(reloaded_manager.get_api_credentials('baidu')['secret_key'], 'demo-secret')
            self.assertEqual(
                reloaded_manager.get_all_settings()['hotkeys']['translate_input'],
                'alt+shift+x',
            )

    def test_translator_core_handles_empty_text_and_smart_direction(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            runtime_dir = Path(temp_dir)
            self._prepare_isolated_imports(runtime_dir)
            translator_core_module = importlib.import_module('translator_core')

            core = translator_core_module.TranslatorCore()

            self.assertEqual(
                core._resolve_translation_direction('你好，世界', 'auto', '__smart__'),
                ('zh', 'en'),
            )
            self.assertEqual(
                core._resolve_translation_direction('hello world', 'auto', '__smart__'),
                ('en', 'zh'),
            )
            self.assertIsNone(core.translate_result('   '))
            self.assertEqual(core.last_error, '请输入要翻译的文本')

    def test_app_entry_injects_project_and_src_paths_before_import(self):
        app_path = PROJECT_ROOT / 'app.py'
        fake_main_window = types.ModuleType('main_window')

        def fake_main():
            return None

        fake_main_window.main = fake_main
        original_main_window = sys.modules.get('main_window')
        sys_path_before = list(sys.path)
        sys.modules['main_window'] = fake_main_window

        try:
            globals_after_run = runpy.run_path(str(app_path), run_name='easy_translation_app_smoke')
            injected_path_prefix = list(sys.path[:2])
        finally:
            sys.path[:] = sys_path_before
            if original_main_window is None:
                sys.modules.pop('main_window', None)
            else:
                sys.modules['main_window'] = original_main_window

        self.assertEqual(globals_after_run['main'], fake_main)
        self.assertEqual(globals_after_run['project_root'], str(PROJECT_ROOT))
        self.assertEqual(injected_path_prefix[0], str(SRC_ROOT))
        self.assertEqual(injected_path_prefix[1], str(PROJECT_ROOT))


if __name__ == '__main__':
    unittest.main(verbosity=2)
