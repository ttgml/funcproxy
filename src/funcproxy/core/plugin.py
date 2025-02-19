# src/hook_tool/core/plugin.py
import importlib.util
import logging
import sys
import os
import hashlib
from pathlib import Path
from threading import Lock
from typing import List, Dict, Type
from .plugin_base import PluginBase

logger = logging.getLogger("plugins")

class PluginManager:
    def __init__(self):
        self.plugins: List[PluginBase] = []
        self.lock = Lock()
    
    def load_plugins_from_dir(self):
        """从目录加载所有插件"""
        plugin_path = Path(__file__).parent.parent / "plugins"
        if not plugin_path.is_dir():
            raise ValueError(f"Plugin directory not found: {plugin_path}")
        for plugin_dir in plugin_path.iterdir():
            if plugin_dir.is_dir():
                obj_file = os.path.join(plugin_dir, "info.json")
                if os.path.exists(obj_file):
                    self._load_plugin(plugin_dir)
        print("load plugins from dir finish.")

    def _load_plugin(self, plugin_path: Path):
        """加载指定插件"""
        print(f"Loading plugin from {plugin_path.name}")
        module_name = plugin_path.name
        module = importlib.import_module(f"funcproxy.plugins.{module_name}")
        for attr in dir(module):
            cls = getattr(module, attr)
            if isinstance(cls, type) and issubclass(cls, PluginBase) and cls is not PluginBase:
                self.plugins.append(cls)
                print(f"Loaded plugin {cls.name(cls)}")
    def unload_plugin(self, path: str):
        """卸载指定插件"""
        pass

    def get_plugin_info(self) -> List[dict]:
        """获取已加载插件信息"""
        return [{
            "path": path
        } for path, data in self.plugins.items()]