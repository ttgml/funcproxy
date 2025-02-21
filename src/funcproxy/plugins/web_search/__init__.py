from funcproxy.core.plugin_base import PluginBase
import json

class Plugin(PluginBase):
    def __init__(self):
        print("Web Search Plugin initialized")

    def do_search_online(self, parameters) -> str:
        return "not found"
    
    def do_open_website(self, parameters) -> str:
        return "not found"