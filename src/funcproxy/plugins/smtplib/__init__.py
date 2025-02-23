from funcproxy.core.plugin_base import PluginBase
import json

class Plugin(PluginBase):
    def __init__(self):
        self.logger.info("SMTP Plugin initialized")
    def do_send_mail(self, parameters) -> dict:
        # 使用smtplib发送邮件
        result = {}
        settings = self.get_settings()
        parameters = json.loads(parameters)
        try:
            import smtplib
            from email.mime.text import MIMEText
            msg = MIMEText(parameters["body"])
            msg['From'] = settings['smtp_username']
            msg['To'] = parameters["to"]
            msg['Subject'] = parameters["subject"]
            with smtplib.SMTP_SSL(settings['smtp_server'], int(settings['smtp_port'])) as server:
                server.login(settings['smtp_username'], settings['smtp_password'])
                server.sendmail(from_addr=settings['smtp_username'], to_addrs=parameters["to"], msg=msg.as_string())
            result = {
                "status": "success",
                "message": "发送成功"
            }
            self.logger.debug("smtplib call: %s", parameters)
        except Exception as e:
            self.logger.error(e)
            self.logger.debug(settings)
            self.logger.error("smtplib call: %s", parameters)
            result = {
                "status": "error",
                "message": "发送失败"
            }
        return result
    
