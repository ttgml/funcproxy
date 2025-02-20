from funcproxy.core.plugin_base import PluginBase

class Plugin(PluginBase):

    
    def __init__(self):
        print("SMTP Plugin initialized")
    
    def function_call(self, parameters: dict) -> dict:
        result = {
            "status": "success",
            "message": "SMTP Plugin called successfully"
        }
        print("smtplib call: ", parameters)
        return result

    def add_function(self, tools: list) -> list:
        fc = {
            "type": "function",
            "function": {
                "name": "send_email",
                "description": "Send an email using SMTP",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "to": {
                            "type": "string",
                            "description": "The email address of the recipient"
                        },
                        "subject": {
                            "type": "string",
                            "description": "The subject of the email"
                        },
                        "body": {
                            "type": "string",
                            "description": "The body of the email"
                        }
                    },
                    "required": ["to", "subject", "body"]
                }
            }
        }
        tools.append(fc)
        return tools
    
    def enable(self) -> dict:
        return {
            "status": "success",
            "message": "SMTP Plugin enabled successfully"
        }
    
    def disable(self) -> dict:
        return {
            "status": "success",
            "message": "SMTP Plugin disabled successfully"
        }
    
