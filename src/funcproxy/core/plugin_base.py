from abc import ABC, abstractmethod
import sys
import os
import json
from pathlib import Path

class PluginBase:

    def __init__(self):
        raise NotImplementedError("PluginBase is not implemented")
    
    def add_function(self, tools: list) -> list:
        """
        Add a function to the plugin.
        """
        plugin_module_name = self.__class__.__module__
        child_module = sys.modules[plugin_module_name]
        plugin_path = Path(child_module.__file__).parent
        plugin_obj = json.load(open(os.path.join(plugin_path, "info.json"),'r'))
        for func_item in plugin_obj.get("func",[]):
            item = {
                "type": "function",
                "function": {
                    "name": func_item.get("name"),
                    "description": func_item.get("description"),
                    "parameters": func_item.get("parameters")
                }
            }
            tools.append(item)
        return tools
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
    
