from funcproxy.core.plugin_base import PluginBase
import json
import time
class Plugin(PluginBase):
    def __init__(self):
        self.logger.info("Runenv Plugin initialized")

    def do_get_current_time(self, parameters) -> str:
        self.logger.debug("do_get_current_time called")
        # 返回当前时间 ，年月日 时分秒
        return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())