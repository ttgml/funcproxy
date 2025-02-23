from abc import ABC, abstractmethod
import sys
import os
import json
from pathlib import Path

class PluginBase:

    def __init__(self):
        raise NotImplementedError("PluginBase is not implemented")
    
    def get_plugin_path(self) -> str:
        """
        Get the path of the plugin.
        """
        plugin_module_name = self.__class__.__module__
        child_module = sys.modules[plugin_module_name]
        plugin_path = Path(child_module.__file__).parent
        return str(plugin_path)
    def add_function(self, tools: list) -> list:
        """
        Add a function to the plugin.
        """
        plugin_path = self.get_plugin_path()
        plugin_obj = json.load(open(os.path.join(plugin_path, "info.json"),'r'))
        for func_item in plugin_obj.get("func",[]):
            item = {
                "type": "function",
                "function": {
                    "name": func_item.get("func"),
                    "description": func_item.get("description")
                }
            }
            if func_item.get("parameters", None) != None:
                item['function']["parameters"] = func_item.get("parameters")
            tools.append(item)
        return tools
    
    def get_settings(self) -> dict:
        """
        Get the settings of the plugin.
        """
        plugin_path = self.get_plugin_path()
        plugin_settings = json.load(open(os.path.join(plugin_path, "setting.json"),'r'))
        plugin_current_setting = plugin_settings.get("current",{})
        return plugin_current_setting
    def enable(self) -> dict:
        """
        Enable the plugin.
        """
        raise NotImplementedError("PluginBase.enable is not implemented")
    
    def disable(self) -> dict:
        """
        Disable the plugin.
        """
        raise NotImplementedError("PluginBase.disable is not implemented")
    
