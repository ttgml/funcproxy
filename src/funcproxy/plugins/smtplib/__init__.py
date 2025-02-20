from funcproxy.core.plugin_base import PluginBase

class Plugin(PluginBase):
    def __init__(self):
        print("SMTP Plugin initialized")
        self.plugin_id = "smtplib"
        self.install()
    
    def function_call(self, parameters: dict) -> dict:
        result = {
            "status": "success",
            "message": "SMTP Plugin called successfully"
        }
        print("smtplib call: ", parameters)
        return result
    
    def do_send_mail(self, parameters: dict) -> dict:
        result = {
            "status": "success",
            "message": "SMTP Plugin called successfully"
        }
        print("smtplib call: ", parameters)
        return result
    
    def install(self) -> dict:
        return {
            "status": "success",
            "message": "SMTP Plugin enabled successfully"
        }
    
    def uninstall(self) -> dict:
        return {
            "status": "success",
            "message": "SMTP Plugin disabled successfully"
        }
    
