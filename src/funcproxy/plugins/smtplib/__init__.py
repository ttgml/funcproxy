from funcproxy.core.plugin_base import PluginBase
import json

class Plugin(PluginBase):
    def __init__(self):
        print("SMTP Plugin initialized")
        self.plugin_id = "smtplib"
    
    def do_send_mail(self, parameters: dict) -> dict:
        # 使用smtplib发送邮件
        result = {}
        settings = self.get_settings()
        parameters = json.loads(parameters)
        try:
            import smtplib
            from email.mime.text import MIMEText
            msg = MIMEText(parameters["body"])
            print("what?")
            msg['From'] = settings['current']['smtp_username']
            msg['To'] = parameters["to"]
            msg['Subject'] = parameters["subject"]
            with smtplib.SMTP_SSL(settings['current']['smtp_server'], int(settings['current']['smtp_port'])) as server:
                server.login(settings["current"]['smtp_username'], settings['current']['smtp_password'])
                server.sendmail(from_addr=settings["current"]['smtp_username'], to_addrs=parameters["to"], msg=msg.as_string())
            result = {
                "status": "success",
                "message": "发送成功"
            }
            print("smtplib call: ", parameters)
        except Exception as e:
            print(e)
            print(settings)
            print("smtplib call: ", parameters)
            result = {
                "status": "error",
                "message": "发送失败"
            }
        return result
    
