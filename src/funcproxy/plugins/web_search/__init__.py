from funcproxy.core.plugin_base import PluginBase
import json
import requests

class Plugin(PluginBase):
    def __init__(self):
        print("Web Search Plugin initialized")
        self.firecrawl_api = "https://api.firecrawl.dev/v1/scrape"

    def do_search_online(self, parameters) -> str:
        parameters = json.loads(parameters)
        return "not found"
    
    def do_open_website(self, parameters) -> str:
        parameters = json.loads(parameters)
        setting = self.get_settings()
        try:
            headers = {
                "Authorization": "Bearer " + setting["apikey"]
            }
            data = {
                "url": parameters["url"],
                "formats": ["markdown"]
            }
            response = requests.post(self.firecrawl_api, json=data, headers=headers)
            if response.status_code == 200:
                if response.json()['success'] == True:
                    return response.json()["data"]["markdown"]
            return "not found"
        except Exception as e:
            print(e)
            return "not found"