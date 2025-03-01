from funcproxy.core.plugin_base import PluginBase
import json
import os

class Plugin(PluginBase):
    def __init__(self):
        self.logger.info("Notepad Plugin initialized")
        self.notepad_path = os.path.join(self.get_plugin_path(),"notepad.txt")

    def do_write_notepad(self, parameters) -> str:
        parameters = json.loads(parameters)
        self.logger.debug("notepad_path %s", self.notepad_path)
        try:
            with open(self.notepad_path, "a", encoding='utf-8') as f:
                f.write("\n\n")
                f.write(parameters["content"])
            return "记录成功"
        except Exception as e:
            print(e)
            return "记录失败"
    
    def do_read_notepad(self, parameters) -> str:
        parameters = json.loads(parameters)
        try:
            with open(self.notepad_path, "r", encoding='utf-8') as f:
                content = f.read().strip()
                return content
        except Exception as e:
            return "读取失败"
        
    
