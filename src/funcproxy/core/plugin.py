# src/hook_tool/core/plugin.py
import importlib.util
import logging
import sys
import os
import hashlib
import json
from pathlib import Path
from threading import Lock
from typing import List, Dict, Type
from .plugin_base import PluginBase

logger = logging.getLogger("plugins")

class PluginManager:
    def __init__(self):
        self.enabled_plugins: dict[str, Type[PluginBase]] = {}   #已经启用的插件
        self.plugins: list = [] #插件列表
        self.tools: dict[str, str] = {} #工具列表 key:tool_name value: plugin_id
        self.lock = Lock()
        self.plugins_path = Path(__file__).parent.parent / "plugins"
        self.init_plugins()

    def init_plugins(self):
        if not self.plugins_path.is_dir():
            raise ValueError(f"Plugin directory not found: {self.plugins_path}")
        for plugin_dir in self.plugins_path.iterdir():
            if plugin_dir.is_dir():
                obj_file = os.path.join(plugin_dir, "info.json")
                if os.path.exists(obj_file):
                    plugin_info_obj = json.load(open(obj_file, "r"))
                    self.plugins.append(plugin_info_obj)
                    

    def get_plugins(self) -> list:
        return self.plugins.copy()
    def disable_plugin(self, plugin_id: str) -> dict:
        """禁用插件"""
        try:
            plugin = self.get_plugin_info(plugin_id)
            plugin['info']['enabled'] = False
            self.save_plugin_info(plugin_id, plugin['info'])
            self._unload_plugin(plugin_id)
        except Exception as e:
            print(e)
    def enable_plugin(self, plugin_id: str) -> bool:
        """启用插件"""
        try:
            plugin = self.get_plugin_info(plugin_id)
            plugin['info']['enabled'] = True
            self.save_plugin_info(plugin_id, plugin['info'])
            self._load_plugin(plugin_id)
        except Exception as e:
            print(e)
    def load_plugins_from_dir(self):
        """从目录加载所有插件"""
        if not self.plugins_path.is_dir():
            raise ValueError(f"Plugin directory not found: {self.plugins_path}")
        for plugin_dir in self.plugins_path.iterdir():
            if plugin_dir.is_dir():
                obj_file = os.path.join(plugin_dir, "info.json")
                if os.path.exists(obj_file):
                    plugin_info_obj = json.load(open(obj_file, "r"))
                    if plugin_info_obj["enabled"]:
                        self._load_plugin(plugin_info_obj['id'])
        print("load plugins from dir finish.")

    def _load_plugin(self, plugin_id: str) -> bool:
        """加载指定插件"""
        print(f"Loading plugin from {plugin_id}")
        module_name = plugin_id
        module = importlib.import_module(f"funcproxy.plugins.{module_name}")
        for attr in dir(module):
            cls = getattr(module, attr)
            if isinstance(cls, type) and issubclass(cls, PluginBase) and cls is not PluginBase:
                self.enabled_plugins[module_name] = cls()
                print(f"add done.")
                for tool in self.get_plugin_tools(module_name):
                    self.tools[tool['func']] = module_name
                    print("add func: ", tool['func'])
                return True
        return False
    def _unload_plugin(self, plugin_id: str):
        """卸载指定插件"""
        print(self.enabled_plugins)
        self.enabled_plugins.pop(plugin_id, None)
        print(f"remove done.")
        print(self.enabled_plugins)

    def get_plugin_tools(self, plugin_id: str) -> list:
        """获取指定插件的函数列表"""
        plugin_info = self.get_plugin_info(plugin_id)
        if plugin_info:
            tools = plugin_info['info'].get('func', [])
            return tools
        return []

    def get_plugin_info(self, plugin_id: str) -> dict:
        result = {}
        plugin_path = os.path.join(self.plugins_path, plugin_id)
        plugin_obj = os.path.join(plugin_path, "info.json")
        if os.path.exists(plugin_path):
            result['path'] = plugin_path
        else:
            raise FileNotFoundError(f"插件 {plugin_id} 不存在")
        if os.path.exists(plugin_obj):
            result['info'] = json.load(open(plugin_obj, 'r'))
        else:
            raise FileNotFoundError(f"插件 {plugin_id} 的信息文件不存在")
        return result
    
    
    def save_plugin_info(self, plugin_id: str, info: dict) -> dict:
        plugin_path = os.path.join(self.plugins_path, plugin_id)
        plugin_info_path = os.path.join(plugin_path, "info.json")
        with open(plugin_info_path, 'w') as f:
            json.dump(info, f, ensure_ascii=False, indent=4, sort_keys=True)
        return self.get_plugin_info(plugin_id)