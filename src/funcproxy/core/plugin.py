# src/hook_tool/core/plugin.py
import importlib.util
import logging
import sys
import hashlib
from pathlib import Path
from threading import Lock
from typing import List, Dict, Type

logger = logging.getLogger("plugins")

class PluginManager:
    def __init__(self):
        self.plugins: Dict[str, dict] = {}  # {path: {module, hook_class, instance}}
        self.hooks: List[str] = []
        self.lock = Lock()
        
    def _generate_module_name(self, path: str) -> str:
        """生成唯一的模块名避免冲突"""
        hash_id = hashlib.md5(path.encode()).hexdigest()[:8]
        return f"hook_plugin_{hash_id}"

    def _load_single_plugin(self, path: str) -> bool:
        """加载单个插件文件"""
        try:
            path = str(Path(path).resolve())
            module_name = self._generate_module_name(path)
            spec = importlib.util.spec_from_file_location(module_name, path)
            
            if spec is None:
                logger.error(f"Invalid plugin file: {path}")
                return False
                
            module = importlib.util.module_from_spec(spec)
            sys.modules[module_name] = module
            spec.loader.exec_module(module)
            
            # 检查插件是否正确定义了 Hook 类
            if not hasattr(module, "Hook"):
                logger.error(f"Plugin {path} missing 'Hook' class")
                return False
                
            hook_class = module.Hook
            if not issubclass(hook_class, BaseHook):
                logger.error(f"Plugin {path} Hook must inherit from BaseHook")
                return False
                
            instance = hook_class()
            
            with self.lock:
                self.plugins[path] = {
                    "module": module,
                    "hook_class": hook_class,
                    "instance": instance
                }
                self.hooks.append(instance)
                
            logger.info(f"Successfully loaded plugin: {path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load plugin {path}: {str(e)}")
            return False

    def load_plugins_from_dir(self, plugin_dir: str):
        """从目录加载所有插件"""
        plugin_path = Path(plugin_dir)
        if not plugin_path.is_dir():
            raise ValueError(f"Plugin directory not found: {plugin_dir}")
            
        for py_file in plugin_path.glob("*.py"):
            if py_file.name.startswith("_"):  # 忽略以_开头的文件
                continue
            self._load_single_plugin(str(py_file))

    def reload_plugin(self, path: str):
        """重新加载指定插件"""
        path = str(Path(path).resolve())
        
        if path not in self.plugins:
            logger.warning(f"Trying to reload unloaded plugin: {path}")
            return self._load_single_plugin(path)
            
        old_data = self.plugins[path]
        module_name = self._generate_module_name(path)
        
        try:
            # 先移除旧插件
            with self.lock:
                if old_data["instance"] in self.hooks:
                    self.hooks.remove(old_data["instance"])
                del self.plugins[path]
                
            # 清理模块缓存
            if module_name in sys.modules:
                del sys.modules[module_name]
                
            # 重新加载
            success = self._load_single_plugin(path)
            if not success:
                logger.error(f"Failed to reload plugin: {path}")
                
        except Exception as e:
            logger.error(f"Critical error during reload {path}: {str(e)}")
            # 尝试恢复旧版本
            with self.lock:
                self.plugins[path] = old_data
                self.hooks.append(old_data["instance"])

    def unload_plugin(self, path: str):
        """卸载指定插件"""
        path = str(Path(path).resolve())
        
        with self.lock:
            if path in self.plugins:
                data = self.plugins.pop(path)
                if data["instance"] in self.hooks:
                    self.hooks.remove(data["instance"])
                module_name = self._generate_module_name(path)
                if module_name in sys.modules:
                    del sys.modules[module_name]
                logger.info(f"Unloaded plugin: {path}")

    def get_plugin_info(self) -> List[dict]:
        """获取已加载插件信息"""
        return [{
            "path": path,
            "class": data["hook_class"].__name__,
            "version": getattr(data["module"], "__version__", "unknown")
        } for path, data in self.plugins.items()]