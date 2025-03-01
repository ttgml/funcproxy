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
import shutil

logger = logging.getLogger(__name__)

class PluginManager:
    def __init__(self):
        self.enabled_plugins: dict[str, Type[PluginBase]] = {}   #已经启用的插件
        self.plugins: list = [] #插件列表
        self.tools: dict[str, str] = {} #工具列表 key:tool_name value: plugin_id
        self.lock = Lock()
        self.plugins_path = Path(__file__).parent.parent / "plugins"
        self.init_plugins()

    def init_plugins(self):
        self.plugins = []
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
            logger.error(f"禁用插件 {plugin_id} 失败: {e}")
    def enable_plugin(self, plugin_id: str) -> bool:
        """启用插件"""
        try:
            plugin = self.get_plugin_info(plugin_id)
            plugin['info']['enabled'] = True
            self.save_plugin_info(plugin_id, plugin['info'])
            self._load_plugin(plugin_id)
        except Exception as e:
            logger.error(f"启用插件 {plugin_id} 失败: {e}")
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
        logger.info("Loaded plugins: %s" % self.enabled_plugins)

    def _load_plugin(self, plugin_id: str) -> bool:
        """加载指定插件"""
        logger.info(f"Loading plugin {plugin_id}")
        module_name = plugin_id
        module = importlib.import_module(f"funcproxy.plugins.{module_name}")
        for attr in dir(module):
            cls = getattr(module, attr)
            if isinstance(cls, type) and issubclass(cls, PluginBase) and cls is not PluginBase:
                self.enabled_plugins[module_name] = cls()
                for tool in self.get_plugin_tools(module_name):
                    self.tools[tool['func']] = module_name
                    logger.debug(f"Loaded plugin: %s", tool['func'])
                return True
        return False
    def _unload_plugin(self, plugin_id: str):
        """卸载指定插件"""
        removed_funcs = []
        for func_name, plugin_name in list(self.tools.items()):
            if plugin_name == plugin_id:
                removed_funcs.append(func_name)
        for func_name in removed_funcs:
            self.tools.pop(func_name, None)
        self.enabled_plugins.pop(plugin_id, None)
        logger.debug(f"Removed plugin '{plugin_id}'. Functions: {removed_funcs}")
        

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
    
    def get_plugin_settings(self, plugin_id: str) -> dict:
        """获取插件设置"""
        result = {}
        plugin_path = os.path.join(self.plugins_path, plugin_id)
        plugin_setting_obj = os.path.join(plugin_path, "setting.json")
        if os.path.exists(plugin_setting_obj):
            result = json.load(open(plugin_setting_obj, 'r'))
        return result
    
    def update_plugin_settings(self, plugin_id: str, current_info: dict):
        """更新插件设置"""
        plugin_path = os.path.join(self.plugins_path, plugin_id)
        plugin_setting_obj = os.path.join(plugin_path, "setting.json")
        if os.path.exists(plugin_setting_obj):
            plugin_setting_json = json.load(open(plugin_setting_obj, 'r'))
            plugin_setting_json['current'].update(current_info)
            json.dump(plugin_setting_json, open(plugin_setting_obj, 'w'), ensure_ascii=False, indent=4, sort_keys=True)
            return True
        else:
            return False
    def save_plugin_info(self, plugin_id: str, info: dict) -> dict:
        """保存插件信息"""
        plugin_path = os.path.join(self.plugins_path, plugin_id)
        plugin_info_path = os.path.join(plugin_path, "info.json")
        with open(plugin_info_path, 'w') as f:
            json.dump(info, f, ensure_ascii=False, indent=4, sort_keys=True)
        return self.get_plugin_info(plugin_id)
    
    def install_plugin(self, target_plugin_path: str) -> dict:
        info_path = os.path.join(target_plugin_path, "info.json")
        init_path = os.path.join(target_plugin_path, "__init__.py")
        if not os.path.exists(info_path):
            return {"error": "info.json not found"}
        if not os.path.exists(init_path):
            return {"error": "__init__.py not found"}
        info_obj = {}
        try:
            info_obj = json.load(open(info_path, "r"))
            plugin_id = info_obj.get("id")
            plugin_name = info_obj.get("name")
            plugin_title = info_obj.get("title")
            plugin_type = info_obj.get("type")
            plugin_description = info_obj.get("description")
            plugin_author = info_obj.get("author")
            plugin_version = info_obj.get("version")
            plugin_func = info_obj.get("func")
            if plugin_id is None:
                return {"error": "info.json ['id'] is not valid"}
            if os.path.exists(os.path.join(self.plugins_path, plugin_id)):
                return {"error": "plugin already exists"}
        except Exception as e:
            logger.debug(e)
            return {"error": "plugin info.json is not vaild"}
        
        plugin_id = info_obj.get("id")
        installed_plugin_path = os.path.join(self.plugins_path, plugin_id)
        try:
            os.makedirs(installed_plugin_path)
            # 把 target_plugin_path 下的所有文件复制到 installed_plugin_path
            for root, dirs, files in os.walk(target_plugin_path):
                for file in files:
                    src_file = os.path.join(root, file)
                    if file.startswith("."):
                        continue
                    dst_file = os.path.join(installed_plugin_path, os.path.relpath(src_file, target_plugin_path))
                    shutil.copy2(src_file, dst_file)
        except Exception as e:
            logger.debug(f"Failed to install plugin: {e}")
            return {"error": "Failed to install plugin"}
        