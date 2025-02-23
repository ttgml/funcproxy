from funcproxy.core.plugin_base import PluginBase
import json

class Plugin(PluginBase):
    def __init__(self):
        self.logger.info("Runenv Plugin initialized")

    def do_get_system_info(self, parameters) -> str:
        return "v0.1"